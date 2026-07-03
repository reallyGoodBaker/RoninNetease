# -*- coding: utf-8 -*-
import time

from ....compact import remote, Component, BaseCompClient, getOneComponent, NamedEntityVariable
from ....core.log import error as _log_error
from ....utils.persona.client import PersonaRendererComponent
from ....math.double import clamp, inf, epsilon
from ..enum import AnimationEasingTypes, AnimationBlendingTypes, LoopType


class AnimationEasingConf(object):
    def __init__(self, target=1, duration=0.15, func=AnimationEasingTypes.LINEAR):
        self.target = target
        self.func = func
        self.duration = duration


class AnimPlayingInfo(object):
    def __init__(self, meta, entityId, animName, layer, startTime, playRate, serverSync=False):
        self.serverSync = serverSync
        self.animName = animName
        self.layer = layer
        self.startTime = startTime
        self.playRate = playRate
        self.playTime = 0
        nameSuffix = animName.replace('animation.', '')
        self.animTimeComp = NamedEntityVariable(entityId, 'anim_timeex.' + nameSuffix, 0)
        self._manualStop = False
        self._dt = epsilon
        self.duration = inf if meta['length'] == -1 else meta['length']
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
        self.setPlayTime(curTime)

    def setPlayTime(self, time, dt=-1):
        # type: (float, float) -> None
        """
        :param time: 播放时间, 对于于循环动画和保持最后一帧的动画, time 可以大于 duration
        :param dt: 与上一帧的间隔
        这个属性会影响 notifies 的触发, 如果 dt 为 -1, 则使用当前帧和上一帧的时间差
        """
        if dt != -1:
            self._dt = clamp(dt, epsilon, self.duration)
        self.playTime = time
        self.animTimeComp.setValue(self.progress() * self.duration)

    def getNotifies(self):
        if not self.notifies:
            return []
        cur = self.playTime % self.duration if self.loop == LoopType.LOOP else self.playTime
        prev = cur - self._dt
        for time, notifies in self.notifies.items():
            if prev < float(time) <= cur:
                return notifies
        return []

    def progress(self):
        # type: () -> float
        """
        动画进度, 始终返回 0 ~ 1
        """
        if self.loop == LoopType.LOOP:
            return clamp((self.playTime % self.duration) / self.duration, 0, 1)
        return clamp(self.playTime / self.duration, 0, 1)

    def isFinished(self):
        # type: () -> bool
        """
        动画是否播放完毕, 如果循环类型为始终或者保持最后一帧则始终返回 False .
        你可以使用 stop 方法手动终止这两种动画
        """
        if self._manualStop:
            return True
        if self.loop in (LoopType.LOOP, LoopType.KEEP_LAST_FRAME):
            return False
        elif self.loop == LoopType.ONCE:
            return self.playTime >= self.duration
        else:
            raise Exception('Unknown loop type: ' + self.loop)


@Component()
class AnimationExComponent(BaseCompClient):
    """
    一定要使用 registerMetadatas 和 registerAnimations 注册动画，
    否则该组件无法正常使用

    该组件在本地玩家 AddPlayerCreatedClientEvent 事件触发时无法修改本地玩家动画，
    但是可以用于其他玩家进入渲染时给其他玩家播放动画。

    所以如果你需要在所有玩家加载完成时都播放，请同时在 AddPlayerCreatedClientEvent 事件
    和 OnLocalPlayerStopLoading 事件中播放动画

    这个操作影响最大的是 clientOnly 动画，因为跨端同步动画即使在 client 端播放失败，
    也会在广播到自己时重新尝试播放一次。
    """

    def onCreate(self, entityId):
        self.entityId = entityId
        self.layers = {} #type: dict[int, set]
        self.animations = {} # type: dict[str, str]
        self.variables = {} # type: dict[str, NamedEntityVariable]
        self.blending = {}
        self.blendingConf = {} # type: dict[str, dict[str, AnimationEasingConf]]
        self.playing = {} # type: dict[str, AnimPlayingInfo]
        self.notifies = {}
        self.animMetas = {}

    def registerMetadatas(self, metadata):
        for key, data in metadata.items():
            self.animMetas[key] = data

    def registerAnimations(self, mapping):
        # type: (dict[str, str]) -> None
        """
        注册动画映射后需要调用 updateActorAnimDef
        """
        for name, anim in mapping.items():
            if anim in self.animMetas:
                self.animations[name] = anim
            else:
                _log_error('动画 {} 元数据不存在, 动画是否存在或通过 animExtractor 提取?', anim)

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

    def registerEasing(self, animKey, inConf=AnimationEasingConf(), outConf=AnimationEasingConf(0, 0.3)):
        # type: (str, AnimationEasingConf, AnimationEasingConf) -> None
        """
        注册动画混合的缓动效果, 不注册时没有混合效果
        """
        self.blendingConf[animKey] = {
            'in': inConf,
            'out': outConf
        }

    def setBlending(self, blendingType, animKey, partial={}):
        # type: (AnimationBlendingTypes, str, dict) -> None
        rawBlendingConf = self.blendingConf.get(animKey)
        # 无混合时，直接设置值
        if not rawBlendingConf:
            if blendingType == AnimationBlendingTypes.IN:
                self.variables[animKey].setValue(1)
            elif blendingType == AnimationBlendingTypes.OUT:
                self.variables[animKey].setValue(0)
            return
        bConf = rawBlendingConf.get(blendingType)
        target = partial.get('target', bConf.target)
        duration = partial.get('duration', bConf.duration)
        func = partial.get('func', bConf.func)
        existedBlending = self.blending.get(animKey)
        if existedBlending:
            existedBlending['target'] = target
            existedBlending['duration'] = duration
            existedBlending['func'] = func
            existedBlending['startTime'] = time.time()
            existedBlending['type'] = blendingType
        else:
            self.blending[animKey] = {
                'target': target,
                'duration': duration,
                'func': func,
                'startTime': time.time(),
                'type': blendingType
            }

    def anyAnimationPlaying(self):
        return len(self.playing) > 0

    def isPlaying(self, animKey):
        # type: (str) -> bool
        return animKey in self.playing
    
    def getPlayingAnimation(self, animKey):
        return self.playing.get(animKey)

    def _playAnim(self, animKey, layer='default', replay=False, playRate=1, startTime=0, serverSync=False, noBlending=False):
        # type: (str, str, bool, float, float, bool, bool) -> None
        """
        不同 layer 的动画可以同时播放，但同一 layer 的动画不能同时播放
        """
        if not replay and self.isPlaying(animKey):
            return

        animName = self.animations.get(animKey)
        if not animName:
            return

        # 如果同名动画已存在，从原层中移除（不删除整个 layer）
        animInfo = self.playing.get(animKey)
        if animInfo and animInfo.layer:
            self.playing.pop(animKey)
            oldLayer = animInfo.layer
            if oldLayer in self.layers:
                self.layers[oldLayer].discard(animKey)

        # 创建动画播放运行时
        animInfo = AnimPlayingInfo(
            self.animMetas[animName], self.entityId, self.animations[animKey],
            layer, startTime, playRate, serverSync
        )
        self.playing[animKey] = animInfo

        # 记录动画播放层级
        playing = self.layers.get(layer, set()) # type: set[str]
        variable = self.variables[animKey]
        isBlendingOut = animKey in self.blending

        # 先清理同层的旧动画，无论 isBlendingOut 是什么值
        # 保证同 layer 只有一个活跃动画
        hasOldAnims = len(playing) > 0
        if hasOldAnims:
            for _animKey in list(playing):
                if _animKey == animKey:
                    continue
                if noBlending:
                    _v = self.variables.get(_animKey)
                    _v and _v.setValue(0)
                else:
                    self.setBlending(AnimationBlendingTypes.OUT, _animKey)
                    # 立即从 playing 中移除，blend out 视觉效果由 self.blending 独立驱动
                if _animKey in self.playing:
                    self.playing.pop(_animKey)
                playing.discard(_animKey)

        if noBlending:
            variable.setValue(1)
            playing.add(animKey)
            self.layers[layer] = playing
            return

        if not isBlendingOut:
            # 重置播放状态
            variable.setValue(0)
            if hasOldAnims:
                self.setBlending(AnimationBlendingTypes.IN, animKey)
            else:
                variable.setValue(1)
        else:
            # 混合动画
            self.setBlending(AnimationBlendingTypes.IN, animKey)

        playing.add(animKey)
        self.layers[layer] = playing

    def play(self, animKey, layer='default', replay=False, playRate=1, startOffset=0, clientOnly=False, noBlending=False):
        # type: (str, str, bool, float, float, bool, bool) -> None
        startTime = time.time() - startOffset
        self._playAnim(animKey, layer, replay, playRate, startTime, False, noBlending)
        if clientOnly:
            return
        remote.client.call(
            'AnimExServer._syncPlay',
            animKey, layer, replay, playRate, startTime, noBlending,
        )

    def stop(self, animKey, layer='default', noBlending=False, clientOnly=False):
        # type: (str, str, bool, bool) -> None
        animInfo = self.playing.get(animKey)
        if not animInfo or animInfo.layer != layer:
            return
        animInfo._manualStop = True

        if noBlending:
            self.variables[animKey].setValue(0)
        else:
            self.setBlending(AnimationBlendingTypes.OUT, animKey)
        playing = self.layers.get(layer, set()) # type: set[str]
        playing.remove(animKey)
        self.layers[layer] = playing
        if clientOnly:
            return
        remote.client.call(
            'AnimExServer._syncStop',
            animKey, layer, noBlending
        )
