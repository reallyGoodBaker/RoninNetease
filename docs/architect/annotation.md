# `architect.annotation` 模块

用于在类/方法上添加注解并在运行时检索这些注解的辅助工具。

主要内容：

- 注解查找与方法检索的工具函数
- 用于事件监听器、定制标记等的注解支持

源文件： `architect/annotation.py`

主要类/方法：

- `AnnotationHelper` — 静态工具集合
	- `addAnnotation(target, key, value)` : 给 `target` 添加注解键值对
	- `getAnnotation(target, key)` : 获取 `target` 上的注解值（若存在）
	- `findAnnotatedMethods(target, key)` : 返回 `target` 中带指定注解的可调用方法列表
	- `findAnnotatedClasses(target, key)` : 返回带指定注解的类列表
	- `findAnnotatedAttributes(target, key)` : 返回带指定注解的属性列表

使用建议：在子系统或组件上使用 `AnnotationHelper.addAnnotation` 标记方法/类后，可通过 `findAnnotatedMethods` 在运行时自动绑定事件或执行初始化逻辑。
