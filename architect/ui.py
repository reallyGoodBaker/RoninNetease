from .annotation import AnnotationHelper
from .conf import UI_DEF, UI_AUTO_CREATE

def UiDef(uiDef):
    def decorator(cls):
        AnnotationHelper.addAnnotation(cls, UI_DEF, uiDef)
        return cls
    return decorator

def AutoCreate(cls):
    AnnotationHelper.addAnnotation(cls, UI_AUTO_CREATE, True)
    return cls

