from ..annotation import AnnotationHelper
from ..conf import UI_GESTURE

def _btnDecoratorBuilder(type):
    @staticmethod
    def decorator(btnPath):
        def wrapper(func):
            AnnotationHelper.addAnnotation(func, UI_GESTURE, (type, btnPath))
            return func
        return wrapper
    return decorator


class Touch(object):
    Click = _btnDecoratorBuilder('click')
    Move = _btnDecoratorBuilder('move')
    MoveIn = _btnDecoratorBuilder('movein')
    MoveOut = _btnDecoratorBuilder('moveout')
    Cancel = _btnDecoratorBuilder('cancel')
    Down = _btnDecoratorBuilder('down')


TouchEvents = (
    'click',
    'down',
    'move',
    'movein',
    'moveout',
    'cancel'
)


GestureBinder = {
    'click': lambda control, method: control.asButton().SetButtonTouchUpCallback(method),
    'down': lambda control, method: control.asButton().SetButtonTouchDownCallback(method),
    'move': lambda control, method: control.asButton().SetButtonTouchMoveCallback(method),
    'movein': lambda control, method: control.asButton().SetButtonTouchMoveInCallback(method),
    'moveout': lambda control, method: control.asButton().SetButtonTouchMoveOutCallback(method),
    'cancel': lambda control, method: control.asButton().SetButtonTouchCancelCallback(method),
}
