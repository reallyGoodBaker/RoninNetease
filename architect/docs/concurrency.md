# 并发编程 — Future、异步与远程调用

RoninNetease 运行在网易 Minecraft 引擎的单线程环境中，**不支持真正的多线程并发**。但框架提供了基于 Future 模式的异步编程模型，让你以同步风格编写涉及网络 I/O、区块加载和跨端通信的代码。

> 引擎所有的 Python 代码都在主线程中执行（`threading.current_thread().ident` 用于区分服务端/客户端上下文），不存在竞态条件问题。本章的「并发」指逻辑上的异步协作，不涉及操作系统线程。

---

## 1. 架构概览

```
                    ┌─────────────────────────────┐
                    │      Scheduler (主循环)        │
                    │  tickSched / renderSched      │
                    │  executeSequence()            │
                    └──────────┬──────────────────┘
                               │ 每帧驱动
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
         Task (fn)      SuspendableTask    Generator
         立即执行           (callOnce)      @Async 协程
                               │               │
                               ▼               ▼
                          yield 控制权      yield Future
                               │               │
                               ▼               ▼
                          Future 链式调用（done / expected）
                               │
               ┌───────────────┼───────────────┐
               ▼               ▼               ▼
         command.*       remote.invoke    requireChunk
       (区块操作)       (跨端 RPC)      (区块就绪等待)
```

---

## 2. Future — 异步原语

### 2.1 核心概念

`Future` 代表一个**尚未完成的计算结果**。它有三种状态：

| 状态 | 常量 | 含义 |
|---|---|---|
| `PENDING` | `Future.PENDING` | 计算进行中 |
| `FULFILLED` | `Future.FULFILLED` | 计算成功完成 |
| `REJECTED` | `Future.REJECTED` | 计算失败 |

与 JavaScript Promise 不同，RoninNetease 的 `Future` **回调是同步执行的**——当 `_resolve()` 或 `_reject()` 被调用时，注册的回调立即在当前调用栈中执行，不存在微任务队列。

### 2.2 创建 Future

**方式一：传入 executor 函数**

```python
from architect.core.scheduler import Future

def loadPlayerData(resolve, reject):
    data = readFromStorage()
    if data:
        resolve(data)
    else:
        reject(ValueError('Player not found'))

future = Future(loadPlayerData)
```

`executor` 接收两个参数：`resolve`（成功回调）和 `reject`（失败回调）。它在 `Future.__init__` 中被立即调用。

**方式二：使用 `Future.resolvers()` 工厂**

```python
ftr, resolve, reject = Future.resolvers()

# 在某个回调中：
resolve('data ready')

# 在另一个地方等待：
ftr.done(lambda result: print('Got:', result))
```

`resolvers()` 返回 `(future, resolve, reject)` 三元组，resolve/reject 可以在外部持有的地方调用。

### 2.3 注册回调

```python
future = requireChunk(someLocation)

# 成功回调（可链式调用）
future.done(lambda: print('Chunk loaded'))

# 失败回调
future.expected(lambda err: print('Failed:', err))

# 链式写法
future.done(onSuccess).expected(onError)
```

- `done(callback)` — 注册成功回调。如果 Future 已 FULFILLED，立即执行
- `expected(callback)` — 注册失败回调。如果 Future 已 REJECTED，立即执行

### 2.4 Future 链（顺序依赖）

`requireChunk` 返回一个 Future，然后用 `.done()` 串联后续操作：

```python
from architect.command.server import command, requireChunk

def spawnOnLoad(location, entityId):
    ftr, resolve, reject = Future.resolvers()

    # 等区块加载 → 传送 → 生成实体
    requireChunk(location, 16)\
        .done(lambda: command.teleport(entityId, location))\
        .done(lambda pos: command.spawnEntity('my_mob', location, 0))\
        .done(lambda entityId: resolve(entityId))\
        .expected(reject)

    return ftr
```

---

## 3. `@Async` — 生成器协程

### 3.1 为什么需要 `@Async`？

RoninNetease 运行在 **Python 2.7** 上，不支持 `async/await` 语法。`@Async` 利用**生成器的 `yield`**来实现暂停和恢复，模拟 `await` 语义。

```python
from architect.core.scheduler import Future, Async

@Async
def loadAndPlace():
    # yield 一个 Future → @Async 自动等待它完成
    chunkLoaded = yield requireChunk(location, 16)
    # 区块就绪后才执行到这里
    result = yield command.setBlock(location, 'minecraft:stone')
    print('Block placed:', result)

# 调用方
future = loadAndPlace()
future.done(lambda: print('All done'))
```

### 3.2 工作原理

```
1. loadAndPlace() 被调用 → 创建生成器 → advance() 启动
       │
2. gen.next() → yield requireChunk(...)  ← 暂停，返回 Future
       │
3. @Async 在 requireChunk Future 上注册 done/expected
       │
4. requireChunk 完成 → advance(value) → gen.send(value)  ← 恢复
       │
5. yield command.setBlock(...)  ← 再次暂停
       │
6. setBlock 完成 → advance(value) → gen.send(value)  ← 恢复
       │
7. 生成器 return → StopIteration → resolve(result)
```

关键的 `advance` 函数源码：

```python
def advance(value=None, exc=None):
    try:
        if exc is not None:
            yielded = gen.throw(exc)
        else:
            yielded = gen.send(value) if value is not None else gen.next()
    except StopIteration as e:
        resolve(e.args[0] if e.args else None)  # 协程完成
        return
    except Exception as e:
        reject(e)                                  # 异常传播
        return

    # 等待 yield 出来的 Future
    if isinstance(yielded, Future):
        yielded.done(lambda *res: advance(res[0] if res else None))
        yielded.expected(lambda *err: advance(None, err[0] if err else Exception("Future rejected")))
```

### 3.3 多个并发 Future

`@Async` 是串行模型——一次只能等待一个 Future。如果需要同时等待多个独立的 Future，需要手动跟踪：

```python
from architect.core.scheduler import Future

def waitAll(*futures):
    """等待所有 Future 完成，返回结果列表"""
    ftr, resolve, reject = Future.resolvers()
    results = [None] * len(futures)
    completed = [0]

    def on_done(i, resolve, reject, results, completed):
        def handler(value):
            results[i] = value
            completed[0] += 1
            if completed[0] == len(futures):
                resolve(results)
        return handler

    for i, f in enumerate(futures):
        f.done(on_done(i, resolve, reject, results, completed))\
         .expected(lambda err, reject=reject: reject(err))

    return ftr

# 使用
a = requireChunk(locA)
b = requireChunk(locB)
waitAll(a, b).done(lambda results: print('Both chunks loaded'))
```

---

## 4. Scheduler 中的任务模型

### 4.1 Task — 即时任务

```python
class Task:
    def __init__(self, fn):
        self.fn = fn
        self.finished = False
```

每帧由 `Scheduler.execute()` 遍历并调用 `task.fn()`，执行完即标记为 finished。

### 4.2 SuspendableTask — 可暂停任务

```python
class SuspendableTask:
    def __init__(self, generator):
        self.gen = generator()

    def callOnce(self):
        try:
            return next(self.gen)
        except StopIteration:
            self.finished = True
```

`SuspendableTask` 包装一个生成器函数，每帧调用 `next()` 推进一次。生成器通过 `yield` 让出控制权，下一帧继续执行。适合分帧执行的耗时操作（如批量方块填充）。

```python
# command.fillBlocks 内部使用 serverApi.StartCoroutine 执行分帧填充
# 等效于 SuspendableTask 的 callOnce 模式
def fillBlocks(self, pos1, pos2, blockId):
    def _filler(rect):
        # ... 每次 yield 暂停，下一帧继续
        for x in range(minX, maxX + 1):
            for y in range(minY, maxY + 1):
                for z in range(minZ, maxZ + 1):
                    setBlock((x, y, z), blockId)
                    i += 1
                    if i >= chunkSize:
                        i = 0
                        yield  # ← 让出控制权
    serverApi.StartCoroutine(_filler(rect), resolve)
```

### 4.3 重入保护

Scheduler 的 `executeSequence` 通过 `_sequenceExecuting` 标志防止同一帧内重复进入：

```python
def executeSequence(self, *args):
    if self._sequenceExecuting:
        self._skippedUpdates += 1          # ← 记录跳帧
        return 0.0, self._skippedUpdates

    self._sequenceExecuting = True
    self.execute(TIMER_TASK, args)
    for scheduleFlag in self.scheduleSequence:
        self.execute(scheduleFlag, args)
    # ...
    self._sequenceExecuting = False
```

如果上一帧的任务耗时超过帧间隔，下一帧的 `executeSequence` 会检测到 `_sequenceExecuting=True` 并跳过本次执行，`_skippedUpdates` 计数器递增。`getSkippedUpdates()` 可获取跳帧次数以进行性能诊断。

---

## 5. 跨端远程调用（RPC）

### 5.1 架构

RoninNetease 的远程调用基于网易引擎的 `sendServer` / `sendClient` 事件通道，框架在此之上封装了 Future 风格的异步 RPC：

```
Client                                 Server
  │                                      │
  │  remote.client.invoke('uri', args)   │
  │  ─────────────────────────────────→  │
  │       sendServer(REMOTE_CALL_KEY)     │  _callRemoteMethod()
  │                                      │  → _serverRemoteMethods[uri](playerId, *args)
  │                                      │
  │  remote.client.call('uri', args)     │
  │  ─────────────────────────────────→  │  _callRemoteMethod()
  │       sendServer(REMOTE_CALL_KEY)     │  (fire-and-forget, 无返回值)
```

### 5.2 `remote.client.call()` — 单向调用（不等待返回）

```python
from architect.remote.common import remote

# 客户端 → 服务端，不关心返回值
remote.client.call('PlayerMotionSyncServer.syncMotion', playerId, motion)
```

### 5.3 `remote.client.invoke()` — 双向调用（返回 Future）

```python
# 客户端 → 服务端，等待返回值
future = remote.client.invoke('MyServerSystem.getPlayerStats', playerId)

future.done(lambda stats: print('Stats:', stats))\
     .expected(lambda err: print('RPC failed:', err))
```

`invoke()` 内部：
1. 发送调用数据到对端
2. 创建一个 3 秒超时定时器
3. 返回一个 Future

```python
# remote/common.py — invoke 内部实现
def invoke(self, uri, *args, **kwargs):
    ftr, resolve, reject = Future.resolvers()
    retId = self.accId()
    self.subsys.sendServer(REMOTE_CALL_KEY, _createInvokeData(retId, uri, *args, **kwargs))

    # 3 秒超时
    def _timeout():
        del _clientRets[retId]
        reject('timeout')
    timer = LevelClient.getInstance().game.AddTimer(3, _timeout)

    def _recieveReturn(result, err):
        LevelClient.getInstance().game.CancelTimer(timer)
        if err:
            return reject(err)
        return resolve(result)
    _clientRets[retId] = _recieveReturn

    return ftr
```

### 5.4 服务端 RPC

```python
# 服务端向单个客户端发送
remote.server.call(playerId, 'ClientSystem.showDialog', 'Hello!')
future = remote.server.invoke(playerId, 'ClientSystem.getConfirmation')

# 广播所有客户端
remote.server.callEvery('ClientSystem.onGlobalEvent', eventData)
```

### 5.5 服务端 @Remote 方法声明

```python
from architect.remote.common import Remote

class MyServerSystem(ServerSubsystem):
    @Remote
    def getPlayerStats(self, playerId, statKey):
        """playerId 由框架自动注入（第一个参数）"""
        return self.stats[playerId].get(statKey)

    @Remote(key=str, value=int)  # 可选参数验证
    def setPlayerStat(self, playerId, key, value):
        self.stats[playerId][key] = value
```

> **注意：** 服务端的 `@Remote` 方法第一个参数会被框架自动注入为发起调用的玩家 ID。客户端不需要这个参数，因此参数列表略有不同。

### 5.6 RPC 中的 Future

服务端 `@Remote` 方法可以直接返回一个 `Future`，框架会自动等待：

```python
@Remote
def teleportPlayer(self, playerId, targetLocation):
    # command.teleport 返回 Future
    # 框架检测到返回值是 Future 后，自动注册 done/expected
    return command.teleport(playerId, targetLocation)
```

```python
# remote/common.py — _callRemoteMethod 中的处理
if isinstance(result, Future):
    result.done(lambda v: _sendReturn(v, None))
    result.expected(lambda e: _sendReturn(None, e))
```

---

## 6. command 模块 — 区块感知的异步操作

`architect.command.server` 模块封装了需要等待区块加载的服务器操作，所有方法都返回 `Future`：

```python
from architect.command.server import command, requireChunk

# 确保区块加载完成
requireChunk(location, radius=16)\
    .done(lambda: print('Chunk ready'))

# 传送实体（自动等待区块）
command.teleport(entityId, location)\
    .done(lambda pos: print('Teleported to', pos))\
    .expected(lambda err: print('Teleport failed:', err))

# 放置方块
command.setBlock(location, 'minecraft:stone')\
    .done(lambda: print('Block placed'))

# 批量填充
command.fillBlocks(minPos, maxPos, 'minecraft:dirt', chunkSize=256)\
    .done(lambda: print('Fill complete'))

# 放置结构
command.placeStructure(location, 'my:house', loadingRadius=32)\
    .done(lambda: print('Structure placed'))

# 查询顶层空位
command.queryTopEmptySpace(location)\
    .done(lambda y: print('Top Y:', y))
```

**`requireChunk` 的核心原理：**

```python
def requireChunk(location, radius=16):
    def _executor(res, rej):
        pos = vec(location.pos)
        r = vec((radius, radius, radius))

        def _detector(result):
            res() if result['code'] else rej()

        result = LevelServer.chunkSource.DoTaskOnChunkAsync(
            location.dim, tup(pos - r), tup(pos + r), _detector
        )

        if not result:
            return rej(ValueError("invalid location"))
    return Future(_executor)
```

引擎的 `DoTaskOnChunkAsync` 是异步的——它会在区块加载完成后调用 `_detector` 回调。`requireChunk` 将其包装成 `Future`，使上层代码可以统一用 `.done()` 链式调用。

---

## 7. 最佳实践

### 7.1 选择正确的异步模式

| 场景 | 推荐模式 | 示例 |
|---|---|---|
| 单一异步操作 | `Future` + `.done()` | `requireChunk(loc).done(action)` |
| 多个顺序异步操作 | `@Async` + `yield` | 加载区块 → 传送 → 放置方块 |
| 多个并行异步操作 | `waitAll()` 手动收集 | 同时加载多个区块 |
| 分帧循环（每帧一步） | `SuspendableTask` / `StartCoroutine` | 批量填充 10000 个方块 |
| 跨端调用（不关心返回） | `remote.*.call()` | 同步运动状态 |
| 跨端调用（需要返回） | `remote.*.invoke()` | 查询玩家数据 |

### 7.2 避免阻塞主线程

**错误做法：**
```python
# ❌ 不要用循环轮询等待
while not dataReady:
    pass
```

**正确做法：**
```python
# ✅ 用 Future 回调
loadData().done(lambda data: process(data))
```

### 7.3 处理 Future 错误

```python
requireChunk(location)\
    .done(lambda: command.setBlock(location, block))\
    .expected(lambda err: log('Failed to load chunk: %s' % err))

# @Async 中自动传播异常到 reject
@Async
def safePlace():
    try:
        yield command.setBlock(location, block)
    except Exception as e:
        print('Placement failed:', e)
```

### 7.4 跳帧监控

```python
class MySystem(ClientSubsystem):
    @Sched.Tick
    def checkPerformance(self):
        skipped = self.manager.tickSched.getSkippedUpdates()
        if skipped > 10:
            print('Warning: %d frames skipped' % skipped)
```

### 7.5 RPC 超时处理

`remote.*.invoke()` 有内置的 3 秒超时。如果调用链更长，需要在业务层自行处理：

```python
future = remote.client.invoke('Server.doComplexTask')
future.done(onSuccess)\
     .expected(lambda err: retryOrFallback() if err == 'timeout' else propagate(err))
```

---

## 下一步

- [调度系统 (scheduler.md)](scheduler.md) — Scheduler 的完整 API
- [事件系统 (event.md)](event.md) — 事件流与责任链
- [子系统 (subsystem.md)](subsystem.md) — 跨端通信的完整示例