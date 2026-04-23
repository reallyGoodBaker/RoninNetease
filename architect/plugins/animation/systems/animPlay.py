import time, math

from ....compact import Sched, Query, ClientSubsystem, SubsystemClient
from ....math.double import lerp

from ..enum import AnimationEasingTypes, AnimationBlendingTypes, AnimEvents
from ..components.animClient import AnimationExComponent


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

    def registerEasingFunc(self, easingType, func):
        # type: (str, function) -> None
        """
        :example:
        ```
            registerEasingFunc('custom', lambda a, b, t: lerp(a, b, t * t * t))
        ```
        """
        self.EasingFuncs[easingType] = func


    def _getBlendValue(self, animEx, animKey, blending):
        # type: (AnimationExComponent, str, dict) -> float
        target = blending['target']
        duration = blending['duration']
        func = blending['func']
        startTime = blending['startTime']
        type = blending['type']
        now = time.time()
        dt = now - startTime
        if dt >= duration:
            animEx.variables[animKey].setValue(target)
            animEx.blending.pop(animKey)
            animInfo = animEx.playing.get(animKey)
            if animInfo:
                animInfo._manualStop = True
            return target
        t = dt / duration
        if type == AnimationBlendingTypes.IN:
            t = 1 - t
        if func in self.EasingFuncs:
            t = self.EasingFuncs[func](0, 1, t)
        return lerp(0, target, t)
    

    def onInit(self):
        self.lastFrameTime = 0
        self.canTick = True


    def onRender(self, dt):
        self.lastFrameTime = dt
    

    @Sched.Render()
    @Query(AnimationExComponent)
    def updateAnimState(self, animEx):
        # type: (AnimationExComponent) -> None

        # update blending
        for animKey, blending in animEx.blending.items():
            curValue = self._getBlendValue(animEx, animKey, blending)
            animEx.variables[animKey].setValue(curValue)

        # update animation
        for animKey, animInfo in animEx.playing.items():
            if animInfo.isFinished():
                eventType = AnimEvents.Interrupted if animInfo._manualStop else AnimEvents.Finish
                self.broadcast(eventType, {
                    'animKey': animKey,
                    'entityId': animEx.entityId,
                    'animName': animInfo.animName
                })
                animEx.playing.pop(animKey)
                animEx.variables[animKey].setValue(0)
                targetLayer = animEx.layers[animInfo.layer]
                if animKey in targetLayer:
                    targetLayer.remove(animKey)
                continue

            for notify in animInfo.getNotifies():
                name = notify['name']
                state = notify['state']
                self.broadcast(
                    AnimEvents.NotifyStart if state else AnimEvents.NotifyEnd,
                    {
                        'animKey': animKey,
                        'entityId': animEx.entityId,
                        'animName': animInfo.animName,
                        'notifyName': name
                    }
                )

            animInfo.doTick(self.lastFrameTime)