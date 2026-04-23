import time

from ....compact import Ref, Component, BaseCompClient, getOneComponent, NamedEntityVariable, QueryVariable
from ....utils.persona.client import PersonaRendererComponent
from ..enum import AnimationEasingTypes, AnimationBlendingTypes, LoopType

try:
    from .....assets.animMeta import AnimMeta
except:
    print('[ERROR] 未找到 AnimMeta, 请使用 architect/tools/animExtractor 提取动画元数据')


class AnimationEasingConf(object):
    def __init__(self, target=1, duration=0.3, func=AnimationEasingTypes.LINEAR):
        self.target = target
        self.func = func
        self.duration = duration


class AnimPlayingInfo(object):
    def __init__(self, entityId, animName, layer, startTime, playRate):
        self.animName = animName
        self.layer = layer
        self.startTime = startTime
        self.playRate = playRate
        self.playTime = 0
        nameSuffix = animName.replace('animation.', '')
        self.animTimeComp = NamedEntityVariable(entityId, 'anim_timeex.' + nameSuffix, 0)
        self._manualStop = False
        self._dt = 0
        meta = AnimMeta[animName]
        self.duration = float('inf') if meta['length'] == -1 else meta['length']
        self.notifies = meta.get('notifies')
        if meta['loop'] == True:
            self.loop = LoopType.LOOP
        elif meta['loop'] == False:
            self.loop = LoopType.ONCE
        else:
            self.loop = LoopType.KEEP_LAST_FRAME

    def doTick(self, _dt):
        dt = _dt * self.playRate
        self._dt = dt
        prevTime = self.playTime
        curTime = dt + prevTime
        self.playTime = curTime
        self.animTimeComp.setValue(curTime)

    def getNotifies(self):
        if not self.notifies:
            return []
        cur = self.playTime
        prev = cur - self._dt
        for time, notifies in self.notifies.items():
            if prev < float(time) <= cur:
                return notifies
        return []

    def isFinished(self):
        if self._manualStop:
            return True
        if self.loop == LoopType.LOOP:
            return False
        elif self.loop in (LoopType.ONCE, LoopType.KEEP_LAST_FRAME):
            return self.playTime >= self.duration
        else:
            raise Exception('Unknown loop type: ' + self.loop)


@Component()
class AnimationExComponent(BaseCompClient):

    def onCreate(self, entityId):
        self.entityId = entityId
        self.layers = {} #type: dict[int, set]
        self.animations = {} # type: dict[str, str]
        self.variables = {}
        self.blending = {}
        self.blendingConf = {}
        self.playing = {} # type: dict[str, AnimPlayingInfo]
        self.notifies = {}

    def registerAnimations(self, mapping):
        # type: (dict[str, str]) -> None
        for name, anim in mapping.items():
            self.animations[name] = anim

    def _createActorRendererAnims(self):
        animations = {}
        for animName in self.animations.values():
            animations[animName] = animName
        return animations
    
    def _createActorAnimate(self):
        animateScripts = []
        for animKey, animName in self.animations.items():
            nameSuffix = animName.replace('animation.', '')
            variable = NamedEntityVariable(self.entityId, 'blendex.' + nameSuffix)
            self.variables[animKey] = variable
            animateScripts.append({
                animName: variable.getName() + ' > 0'
            })
        return animateScripts

    def updateActorAnimDef(self):
        """
        更新动画定义, 内部调用 ActorRender 的 Rebuild 系列方法，
        registerAnimations 后务必调用

        注意, 这个方法会导入 PersonaRendererComponent, 请保证这个组件已经创建
        """
        personaRenderer = getOneComponent(self.entityId, PersonaRendererComponent) # type: PersonaRendererComponent
        personaRenderer.addRenderConf({
            'animations': self._createActorRendererAnims(),
            'scripts': {
                'animate': self._createActorAnimate()
            }
        })

    def registerEasing(self, animKey, inConf=AnimationEasingConf(), outConf=AnimationEasingConf(0)):
        # type: (str, AnimationEasingConf, AnimationEasingConf) -> None
        self.blendingConf[animKey] = {
            'in': inConf,
            'out': outConf
        }

    def updateBlending(self, blendingType, animKey, partial={}):
        # type: (AnimationBlendingTypes, str, dict) -> None
        rawBlendingConf = self.blendingConf.get(animKey)
        if not rawBlendingConf:
            return
        bConf = rawBlendingConf.get(blendingType)
        target = partial.get('target', bConf['target'])
        duration = partial.get('duration', bConf['duration'])
        func = partial.get('func', bConf['func'])
        existedBlending = self.blending.get(animKey)
        if existedBlending:
            existedBlending['target'] = target
            existedBlending['duration'] = duration
            existedBlending['func'] = func
        else:
            self.blending[animKey] = {
                'target': target,
                'duration': duration,
                'func': func,
                'startTime': time.time(),
                'type': blendingType
            }

    def isPlaying(self, animKey):
        # type: (str) -> bool
        return animKey in self.playing

    def play(self, animKey, layer='default', replay=True, playRate=1):
        # type: (str, str, bool, float) -> None
        """
        不同 layer 的动画可以同时播放，但同一 layer 的动画不能同时播放
        """
        if not replay and self.isPlaying(animKey):
            return

        # 将其他层的同名动画删除
        playingLayer = self.playing.get(animKey)
        if playingLayer and playingLayer.layer:
            self.playing.pop(animKey)
            self.layers.pop(playingLayer.layer)
        self.playing[animKey] = AnimPlayingInfo(
            self.entityId,
            self.animations[animKey],
            layer, time.time(), playRate
        )

        playing = self.layers.get(layer, set()) # type: set[str]
        if len(playing) > 0:
            # 长度大于 0 才需要混合动画
            for _animKey in playing:
                self.updateBlending(AnimationBlendingTypes.OUT, _animKey)
            self.variables[animKey].setValue(0)
            self.updateBlending(AnimationBlendingTypes.IN, animKey)
        else:
            variable = self.variables[animKey]
            # 直接播放
            variable.setValue(0)
            variable.setValue(1)
        playing.add(animKey)
        self.layers[layer] = playing

    def stop(self, animKey, layer='default', noBlending=False):
        # type: (str, str, bool) -> None
        animInfo = self.playing.get(animKey)
        if not animInfo or animInfo.layer != layer:
            return
        animInfo._manualStop = True

        if noBlending:
            self.variables[animKey].setValue(0)
        else:
            self.updateBlending(AnimationBlendingTypes.OUT, animKey)
        playing = self.layers.get(layer, set()) # type: set[str]
        playing.remove(animKey)
        self.layers[layer] = playing