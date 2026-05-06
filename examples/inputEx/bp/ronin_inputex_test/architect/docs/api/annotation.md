# Annotation API

`architect.annotation` 模块提供了用于处理 Python 对象注解的工具。

## `AnnotationHelper` 类

一个静态工具类，用于添加、获取和查找对象上的注解。

### 静态方法

#### `AnnotationHelper.addAnnotation(target, key, value)`

为目标对象添加一个注解。

- **`target`**: 任意 Python 对象（类或函数）。
- **`key`**: 注解的键（字符串）。
- **`value`**: 注解的值。

#### `AnnotationHelper.getAnnotation(target, key)`

获取目标对象上指定键的注解值。

- **`target`**: 任意 Python 对象。
- **`key`**: 注解的键（字符串）。
- **返回值**: 如果找到注解则返回其值，否则返回 `None`。

#### `AnnotationHelper.findAnnotatedMethods(target, key)`

查找目标对象（类实例）中所有被指定键注解的方法。

- **`target`**: 类实例。
- **`key`**: 注解的键（字符串）。
- **返回值**: 一个包含所有被注解方法的列表。

#### `AnnotationHelper.findAnnotatedClasses(target, key)`

查找目标模块或类中所有被指定键注解的类。

- **`target`**: 模块或类对象。
- **`key`**: 注解的键（字符串）。
- **返回值**: 一个包含所有被注解类的列表。

#### `AnnotationHelper.findAnnotatedAttributes(target, key)`

查找目标对象中所有被指定键注解的属性。

- **`target`**: 类实例或对象。
- **`key`**: 注解的键（字符串）。
- **返回值**: 一个包含所有被注解属性的列表。
