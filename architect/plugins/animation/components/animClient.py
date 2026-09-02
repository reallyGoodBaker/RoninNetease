# -*- coding: utf-8 -*-
import time

from ....compact import remote, Component, BaseCompClient, getOneComponent, NamedEntityVariable
from ..blendVars import blendVar, animTimeVar
from ....core.log import error as _log_error
from ....utils.persona.client import PersonaRendererComponent
from ....math.double import clamp, inf, epsilon
from ..enum import AnimationEasingTypes, LoopType


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
        # Fix: startOffset was ignored before; now play(startOffset=x) starts from x seconds.
        self.playTime = max(0.0, time.time() - startTime)
        self.animTimeComp = NamedEntityVariable(entityId, animTimeVar(animName), 0)
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
        """
        这个方法不会同步到其他客户端！
        如果你的客户端玩家没有注册动画元数据，
        那么clientOnly=False也没有任何作用
        """
        for key, data in metadata.items():
            self.animMetas[key] = data

    def registerAnimations(self, mapping):
        # type: (dict[str, str]) -> None
        """
        注册动画映射后需要调用 updateActorAnimDef
        这个方法不会同步到其他客户端！
        你需要在其他客户端玩家的AnimationExComponent上注册动画，
        才能收到他们客户端发来的动画同步
        """
        for name, anim in mapping.items():
            if anim in self.animMetas:
                self.animations[name] = anim
            else:
                _log_error('动画 {} 元数据不存在, 动画是否存在或通过 animExtractor 提取?', anim)

    def clearRegisteredAnimations(self):
        # type: () -> None
        """
        卸载当前已注册的所有动画。
        这个方法不会同步到其他客户端！

        注意：网易 ActorRender 的 AddPlayerAnimation/AddPlayerScriptAnimate
        没有对应的 Remove 接口，脚本层无法把已经 Add 进去的动画定义真正删掉。
        这里能做的清理是：
          1. 把所有 blend 变量归零，让旧动画的 scripts.animate 条件立即失效；
          2. 清空组件内部已注册的动画映射、播放状态、混合状态，
             避免切换武器时残留上一把武器的动画。
        """
        for animKey in list(self.playing.keys()):
            animInfo = self.playing[animKey]
            self.stop(animKey, animInfo.layer)

        for variable in self.variables.values():
            variable.setValue(0)

        self.animations.clear()
        self.variables.clear()
        self.blending.clear()
        self.blendingConf.clear()
        self.playing.clear()
        self.layers.clear()
        self.notifies.clear()


    def _createActorRendererAnims(self):
        animations = {}
        for animName in self.animations.values():
            animations[animName] = animName
        return animations
    
    def _createActorAnimate(self):
        animateScripts = []
        for animKey, animName in self.animations.items():
            variable = NamedEntityVariable(self.entityId, blendVar(animName))
            self.variables[animKey] = variable
            animateScripts.append({
                animName: '({} ?? 0) > 0'.format(variable.getName())
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

    def registerEasing(self, animKey, inConf=AnimationEasingConf()):
        # type: (str, AnimationEasingConf) -> None
        """
        注册动画混合的缓动效果, 不注册时没有混合效果
        """
        self.blendingConf[animKey] = inConf

    def setBlending(self, animKey, partial={}, startValue=0.0):
        # type: (str, dict, float) -> None
        inConf = self.blendingConf.get(animKey)
        if not inConf:
            self.variables[animKey].setValue(1)
            return
        target = partial.get('target', inConf.target)
        duration = partial.get('duration', inConf.duration)
        func = partial.get('func', inConf.func)
        existedBlending = self.blending.get(animKey)
        if existedBlending:
            existedBlending['target'] = target
            existedBlending['duration'] = duration
            existedBlending['func'] = func
            existedBlending['startTime'] = time.time()
            existedBlending['startValue'] = startValue
        else:
            self.blending[animKey] = {
                'target': target,
                'duration': duration,
                'func': func,
                'startTime': time.time(),
                'startValue': startValue,
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

        # 如果同名动画是该层唯一动画，只重置 playTime，不动 blend
        existingInfo = self.playing.get(animKey)
        if existingInfo and replay:
            layerSet = self.layers.get(existingInfo.layer, set())
            if len(layerSet) == 1 and animKey in layerSet:
                existingInfo.setPlayTime(0, 0)
                return
        # 如果同名动画已存在，从原层中移除（不删除整个 layer）
        if existingInfo and existingInfo.layer:
            self.playing.pop(animKey)
            oldLayer = existingInfo.layer
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

        # 如果 animKey 之前被挤出过（在 layer set 但不在 playing），
        # 继承当前的变量值作为 blend 起点，避免跳变
        resumedWeight = 0.0
        if animKey not in self.playing and animKey in playing:
            resumedWeight = variable.getValue()
            playing.discard(animKey)

        # 同层互斥
        # noBlending：旧动画立刻归零 + 移出 layer set（硬切）
        # 有 blending：旧动画保留在 layer set，权重由 updateAnimState 分配
        hasOldAnims = len(playing) > 0
        if hasOldAnims:
            for _animKey in list(playing):
                if _animKey == animKey:
                    continue
                self.blending.pop(_animKey, None)
                if noBlending:
                    _v = self.variables.get(_animKey)
                    _v and _v.setValue(0)
                    playing.discard(_animKey)
                # else: 不移出 layer set，权重由 updateAnimState 分配
                if _animKey in self.playing:
                    self.playing.pop(_animKey)

        if noBlending:
            variable.setValue(1)
        elif not isBlendingOut:
            variable.setValue(resumedWeight)
            self.setBlending(animKey, startValue=resumedWeight)
        else:
            self.setBlending(animKey, startValue=resumedWeight)

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

    def stop(self, animKey, layer='default', clientOnly=False):
        # type: (str, str, bool) -> None
        animInfo = self.playing.get(animKey)
        if not animInfo or animInfo.layer != layer:
            return
        animInfo._manualStop = True
        if animKey in self.variables:
            self.variables[animKey].setValue(0)
        playing = self.layers.get(layer, set())
        playing.discard(animKey)
        self.layers[layer] = playing
        if clientOnly:
            return
        remote.client.call(
            'AnimExServer._syncStop',
            animKey, layer
        )
