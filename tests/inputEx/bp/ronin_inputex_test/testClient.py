from .architect.compact import *
from .architect.plugins.input.client import InputAction, InputState
from .architect.plugins.input.systems.inputExClient import InputExClient


@SubsystemClient
class TestClient(ClientSubsystem):

    @EventListener('OnLocalPlayerStopLoading')
    def onLocalPlayerStopLoading(self, ev):
        # 启用 'move' 映射
        InputExClient.getInstance().enableMapping('move')
        # 屏蔽原版走路逻辑
        LevelClient.getInstance().operation.SetCanMove(False)

    @InputAction('laravelMovement')
    def iaMove(self, ev):
        # 通过输入控制玩家移动
        x, y = ev.value
        motion = compClient.CreateActorMotion(localPlayerId())
        cam = LevelClient.getInstance().camera
        forward = vec(cam.GetForward())
        up = vec((0, 1, 0))
        right = normalize(cross(forward, up))
        laravelForward = normalize(cross(up, right))
        moveVec = y * laravelForward + x * right
        motion.SetMotion(tup(moveVec * 1))