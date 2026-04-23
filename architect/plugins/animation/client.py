from ...core.loader import Plugin, PluginBase

@Plugin(
    'RoninAnimationEx',
    [ 1, 0, 0 ],
    'RGB39',
    'Anim Seq & Montage'
)
class AnimationExPlugin(PluginBase):
    def onAttach(self, manager):
        from .systems.animPlay import AnimationExSubsystem