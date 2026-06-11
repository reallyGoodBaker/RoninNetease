# Changelog

All notable changes to the RoninNetease framework.

## [1.1.0] — 2026-06-11

### Added

- **CommandBus** (`architect/core/bus.py`): Local synchronous command bus for decoupling subsystem communication. Supports register/execute/unregister/hasCommand/clearAll.
- **Profiler** (`architect/core/profiler.py`): Lightweight timing collector with `record()`, `flush()`, `snapshot()`, `enable()`/`disable()`. Global `profiler` singleton. Scheduler skipped frames (`scheduler.tickSkipped`, `scheduler.renderSkipped`) automatically fed to profiler.
- **FieldSchema** (`architect/component/schema.py`): `@defineFields` decorator with `FieldSchema(default, validator)` for component field declaration and validation. Auto-initialized in `createComponent`.
- **Entity lifecycle events**: `Marker` now exposes `onEntityCreated` and `onEntityDestroyed` EventSignals, triggered on first mark / last unmark.
- **Plugin dependency declaration**: `@Plugin` decorator now accepts `deps` parameter. `_loadPlugins` runs plugins in topological dependency order with cycle safety.
- **Hot-reloadable config**: `modConf().set(key, value)` runtime setter with `HOT_RELOADABLE` whitelist protection.
- **Scheduler.getSkippedUpdates()**: Public accessor for skipped frames counter.
- **Test suite** (`tests/`): 6 test files covering CommandBus, Profiler, Marker lifecycle, FieldSchema, plugin dependency topological sort, and scheduler skipped frames. Includes `tests/mocks.py` for local testing without MC engine.

### Changed

- **Subsystem._init() atomic rollback**: If any of `_addListeners` / `_addSchedMethods` / `_registerRemoteFuncs` fails during init, previously registered resources are cleaned up and the subsystem is removed from the manager. Prevents zombie subsystem state.
- **CompIndex fallback warning**: Full entity scan (when no targets/required specified) now emits a `RuntimeWarning`.
- **subsystem class docstring**: Added documentation explaining the role of the static utility class vs SubsystemManager.

### Fixed

- Added `# coding=utf-8` declarations to all source files for Py2 compatibility.
- Removed all `.pyc` files from the repository.

### Docs

- **`architecture.md`**: Architecture design document covering layered design, core decisions (decorator vs registry, CompIndex vs Archetype, reentry protection, Py2 strategy), data flow diagram, and module responsibility matrix.
- **`best-practices.md`**: Best practice guide for subsystem design, component design, query patterns, performance diagnostics, plugin usage, and common pitfalls.
- **`bus.md`**: CommandBus API reference with usage examples and comparison with Event/RPC systems.
- **`profiler.md`**: Profiler API reference with diagnostic workflow.

---

## [1.0.0] — Initial

- ECS component system with CompIndex reverse index
- Subsystem lifecycle management (ServerSubsystem / ClientSubsystem)
- Event system (EventChain, EventSignal, ChainedEvent)
- Scheduler (Tick / Render / Fixed / Event)
- UI subsystem with Signal/Sink reactive binding
- Remote RPC with Future-based async
- Plugin system with hot upgrade
- AOP aspect support (Before/After/Replace)
- Math library (vec3, mat4, vec4)
- FSM (deprecated)