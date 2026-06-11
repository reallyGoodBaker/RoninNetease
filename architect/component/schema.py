# coding=utf-8
"""
组件字段 Schema 声明与验证。

允许开发者在组件类上声明预期字段和默认值，框架在 createComponent 时
自动初始化字段并可选的执行验证，减少因拼写错误导致的运行时 bug。

使用方式:
    from architect.component.schema import FieldSchema, DefineFields

    @Component()
    @DefineFields(
        health=FieldSchema(default=100, validator=lambda v: 0 <= v <= 1000),
        name=FieldSchema(default='unnamed')
    )
    class HealthComponent(BaseCompServer):
        pass
"""


class FieldSchema:
    """
    字段描述符：声明默认值和可选的验证函数。

    :param default:   字段默认值
    :param validator: 可选验证函数 (value) -> bool
    """
    def __init__(self, default=None, validator=None):
        self.default = default
        self.validator = validator

    def validate(self, value):
        if self.validator is not None and not self.validator(value):
            raise ValueError(
                "Validation failed for value: {} (validator: {})".format(
                    repr(value), self.validator.__name__ if hasattr(self.validator, '__name__') else 'custom'
                )
            )


def DefineFields(**fields):
    """
    装饰器：为组件类声明字段 schema。

    框架在 createComponent 中检测类是否定义了 _field_schemas，
    若定义则在 onCreate 回调之后自动为实例设置默认值。
    """
    def decorator(cls):
        cls._field_schemas = fields
        return cls
    return decorator


def initComponentFields(comp, component_class, entityId):
    """
    由 createComponent 内部调用，根据 _field_schemas 初始化实例字段。

    若组件类未声明 _field_schemas，此函数无操作。
    """
    schemas = getattr(component_class, '_field_schemas', None)
    if schemas is None:
        return
    for field_name, schema in schemas.items():
        if isinstance(schema, FieldSchema):
            current = getattr(comp, field_name, None)
            if current is None and schema.default is not None:
                setattr(comp, field_name, schema.default)
            schema.validate(getattr(comp, field_name, schema.default))
