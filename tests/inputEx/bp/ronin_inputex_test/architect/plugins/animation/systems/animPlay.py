import time, math

from ....compact import remote, getOneComponent, Remote, Sched, Query, ClientSubsystem, SubsystemClient, EventListener, createComponent
from ....math.double import lerp

from ..enum import AnimationEasingTypes, AnimationBlendingTypes, AnimExEvents
from ..components.animClient import AnimationExComponent
from ..components.dilation import AnimationDilation
from ..utils import AnimationEventDispatcher


@SubsystemClient
class AnimationExSubsystem(ClientSubsystem):

    EasingFuncs = {
        AnimationEasingTypes.LINEAR: lambda a, b, t: lerp(a, b, t),
        AnimationEasingTypes.QUAD: lambda a, b, t: lerp(a, b, t * t),
        AnimationEasingTypes.CUBIC: lambda a, b, t: lerp(a, b, t ** 3),
        AnimationEasingTypes.QUART: lambda a, b, t: lerp(a, b, t ** 4),
        AnimationEasingTypes.QUINT: lambda a, b, t: lerp(a, b, t ** 5),
        AnimationEasingTypes.SINE: lambda a, b, t: lerp(a, b, math.sin(t * math.pi / 2)),
        AnimationEasingTypes.EXPO: lambda a, b, t: lerp(a, b, pow(2, 10 * (t - 1)))
    }

    @classmethod
    def registerEasingFunc(cls, easingType, func):
        # type: (str, function) -> None
        """
        :example:
        ```
            registerEasingFunc('custom', lambda a, b, t: lerp(a, b, t * t * t))
        ```
        """
        cls.EasingFuncs[easingType] = func


    def _getBlendValue(self, animEx, animKey, blending, dilation):
        # type: (AnimationExComponent, str, dict, float) -> float
        target = blending['target']
        duration = blending['duration']
        func = blending['func']
        startTime = blending['startTime']
        type = blending['type']
        now = time.time()
        dt = (now - startTime) * dilation
        if dt >= duration:
            animEx.blending.pop(animKey)
            return target
        t = dt / duration
        if type == AnimationBlendingTypes.OUT:
            t = 1 - t
        return self.EasingFuncs[func](0, 1, t)
    

    def onInit(self):
        self.lastFrameTime = 0
        self.canTick = True
        self.broadcastEvent = False


    def onRender(self, dt):
        self.lastFrameTime = dt


    @EventListener('AddPlayerCreatedClientEvent')
    def onAddPlayerCreatedClientEvent(self, event):
        createComponent(event.playerId, AnimationDilation)
        createComponent(event.playerId, AnimationExComponent)


    @Sched.Render()
    @Query(AnimationDilation, required=[AnimationExComponent])
    def updateDilation(self, dilation):
        oldVal = dilation._oldValue
        newVal = dilation.value
        if oldVal == newVal:
            return
        dilation._oldValue = newVal
        remote.client.call(
            'AnimationServer.updateDilation',
            dilation.value
        )


    @Remote
    def syncDilation(self, instigator, dilation):
        dilationComp = getOneComponent(instigator, AnimationDilation)
        dilationComp.value = dilation


    @Sched.Render()
    @Query(AnimationExComponent, AnimationDilation)
    def updateAnimState(self, animEx, dilation):
        # type: (AnimationExComponent, AnimationDilation) -> None

        # update blending
        blendingOutFinished = []
        for animKey, blending in animEx.blending.items():
            curValue = self._getBlendValue(animEx, animKey, blending, dilation.value)
            animEx.variables[animKey].setValue(curValue)
            if curValue == blending['target'] and blending['type'] == AnimationBlendingTypes.OUT:
                blendingOutFinished.append(animKey)

        # update animation
        for animKey, animInfo in animEx.playing.items():
            animName = animInfo.animName
            for notify in animInfo.getNotifies():
                name = notify['name']
                state = notify['state']
                eventData = {
                    'type': AnimExEvents.Notify,
                    'state': state,
                    'animKey': animKey,
                    'entityId': animEx.entityId,
                    'animName': animName,
                    'notifyName': name,
                    'serverSync': animInfo.serverSync,
                }
                if not animInfo.serverSync:
                    dispatcher = AnimationEventDispatcher.getDispatcher(animName)
                    if dispatcher:
                        dispatcher.dispatch(eventData, animEx)
                if self.broadcastEvent:
                    self.broadcast(
                        AnimExEvents.Notify,
                        eventData
                    )
                    self.broadcast(
                        AnimExEvents.NotifyStart if state else AnimExEvents.NotifyEnd,
                        eventData
                    )

            if animInfo.isFinished() or animKey in blendingOutFinished:
                eventType = AnimExEvents.Interrupted if animInfo._manualStop else AnimExEvents.Finish
                eventDate = {
                    'type': eventType,
                    'animKey': animKey,
                    'entityId': animEx.entityId,
                    'animName': animName,
                    'serverSync': animInfo.serverSync,
                }
                if not animInfo.serverSync:
                    dispatcher = AnimationEventDispatcher.getDispatcher(animName)
                    if dispatcher:
                        dispatcher.dispatch(eventDate, animEx)
                if self.broadcastEvent:
                    self.broadcast(eventType, eventDate)

                animEx.playing.pop(animKey)
                animEx.variables[animKey].setValue(0)
                targetLayer = animEx.layers[animInfo.layer]
                if animKey in targetLayer:
                    targetLayer.remove(animKey)
                continue

            animInfo.doTick(self.lastFrameTime * dilation.value)


    @Remote
    def playFromServer(self, actorId, animKey, layer, replay, playRate, startTime, sync):
        animEx = getOneComponent(actorId, AnimationExComponent)
        # 防止服务端触发的重复播放
        # 通过 startTime 判断
        if animEx.isPlaying(animKey) and animEx.getPlayingAnimation(animKey).startTime == startTime:
            return
        animEx._playAnim(
            animKey, layer, replay, playRate, startTime, sync
        )


    @Remote
    def stopFromServer(self, actorId, key, layer, noBlending):
        animEx = getOneComponent(actorId, AnimationExComponent)
        animEx.stop(
            key, layer, noBlending
        )