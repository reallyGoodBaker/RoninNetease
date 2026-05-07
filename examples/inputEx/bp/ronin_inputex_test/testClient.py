from .architect.compact import *
from .architect.plugins.input.client import InputAction, InputState
from .architect.plugins.input.systems.inputExClient import InputExClient

JUMP_POWER = 0.5
MOVE_SPEED = 0.5


@SubsystemClient
class TestClient(ClientSubsystem):

    def onReady(self):
        self.inputExCient = InputExClient.getInstance()

    @EventListener('OnLocalPlayerStopLoading')
    def onLocalPlayerStopLoading(self, ev):
        # 启用 'move' 映射
        self.inputExCient.enableMapping('move')
        # 屏蔽原版走路逻辑
        LevelClient.getInstance().camera.DepartCamera()
        operation = LevelClient.getInstance().operation
        operation.SetCanMove(False)
        operation.SetCanJump(False)

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
        moveVec = (y * laravelForward + x * right) * MOVE_SPEED
        mx, mz = moveVec.x, moveVec.z
        my = motion.GetMotion()[1]
        motion.SetMotion((mx, my, mz))

    @InputAction('jump')
    def iaJump(self, _):
        # 通过输入控制玩家跳跃
        attr = compClient.CreateAttr(localPlayerId())
        # 如果玩家在地面上，则执行跳跃
        if attr.isEntityOnGround():
            motion = compClient.CreateActorMotion(localPlayerId())
            x, _, z = motion.GetMotion()
            motion.SetMotion((x, JUMP_POWER, z))

    @InputAction('toggleFly')
    def iaToggleFly(self, _):
        # 通过输入控制玩家飞行
        print ('toggleFly')