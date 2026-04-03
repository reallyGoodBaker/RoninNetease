# coding=utf-8
from .basic import compClient, compServer, isServer, clientApi, serverApi
from time import time
from types import *
from .annotation import AnnotationHelper
from .conf import TIMER_TASK, SCHED_UPDATE, SCHED_BEFORE_UPDATE, SCHED_AFTER_UPDATE, SYSTEM_SCHED_ANNO


class Task:
    taskId = 0

    def __init__(self, fn):
        self.fn = fn  # type: FunctionType
        self.id = Task.taskId
        self.finished = False  # type: bool
        Task.taskId += 1


class SuspendableTask:
    def __init__(self, generator):
        self.fn = generator  # type: GeneratorType
        self.gen = generator()
        self.id = Task.taskId
        self.finished = False  # type: bool
        Task.taskId += 1

    def callOnce(self):
        if self.finished:
            return None

        try:
            return next(self.gen)
        except StopIteration:
            self.finished = True
            return None

class Scheduler:
    def __init__(self):
        self._sequenceExecuting = False
        self._lastExecutedTime = time()
        self._skippedUpdates = 0
        self._innerTicks = 0
        self._scheduleQueues = {}  # type: dict[str, list[Task]]
        self._executingThreads = []  # type: list[Task]
        self.scheduleSequence = (
            SCHED_BEFORE_UPDATE,
            SCHED_UPDATE,
            SCHED_AFTER_UPDATE,
        )
        self._shouldRemoveTaskFns = []


    def _getTaskQueue(self, scheduleName):
        # type: (str) -> list[Task]
        queue = self._scheduleQueues.get(scheduleName)
        if queue is None:
            queue = []
            self._scheduleQueues[scheduleName] = queue

        return queue


    def execute(self, scheduleName):
        queue = self._getTaskQueue(scheduleName)
        for t in queue:
            if t.fn in self._shouldRemoveTaskFns:
                queue.remove(t)
                self._shouldRemoveTaskFns.remove(t.fn)
                continue

            self._executingThreads.append(t)

        for t in self._executingThreads:
            if isinstance(t, Task):
                t.fn()
                self._executingThreads.remove(t)

            elif isinstance(t, SuspendableTask):
                t.callOnce()
                if t.finished:
                    self._executingThreads.remove(t)


    def addTask(self, scheduleName, fn):
        # type: (str, FunctionType) -> int
        queue = self._getTaskQueue(scheduleName)
        task = Task(fn)
        queue.append(task)
        return task.id


    def addSuspendableTask(self, scheduleName, generator):
        # type: (str, GeneratorType) -> int
        queue = self._getTaskQueue(scheduleName)
        task = SuspendableTask(generator)
        queue.append(task)
        return task.id


    # 注意, 如果 taskId=-1, 则移除该 scheduleName 下的所有任务
    def removeTask(self, scheduleName, taskId=-1):
        # type: (str, int) -> None
        queue = self._getTaskQueue(scheduleName)
        if taskId != -1:
            for task in queue:
                if task.id == taskId:
                    queue.remove(task)
                    return
        else:
            queue.clear()


    def executeSequence(self):
        """
        :rtype: tuple[float, int]
        :return: (deltaTime, skippedUpdates)
        """
        self._innerTicks += 1
        if self._sequenceExecuting:
            self._skippedUpdates += 1
            return 0.0, self._skippedUpdates

        self._sequenceExecuting = True
        self.execute(TIMER_TASK)
        for scheduleName in self.scheduleSequence:
            self.execute(scheduleName)

        dt = time() - self._lastExecutedTime
        self._lastExecutedTime = time()
        self._sequenceExecuting = False

        return dt, self._skippedUpdates


    def _timeoutWrapper(self, fn, ticks, once=False):
        startTick = self._innerTicks

        def wrapper():
            if (self._innerTicks - startTick) % ticks <= 0:
                fn()
                if once:
                    self._shouldRemoveTaskFns.append(wrapper)

        return wrapper


    def addPeriodicTask(self, fn, ticks=1, interval=False):
        return self.addTask(
            TIMER_TASK,
            self._timeoutWrapper(fn, max(1, ticks), not interval),
        )

    def runTimeout(self, fn, ticks=1):
        return self.addPeriodicTask(fn, ticks, False)
    
    def runInterval(self, fn, ticks=1):
        return self.addPeriodicTask(fn, ticks, True)

    def run(self, fn):
        return self.addPeriodicTask(fn)
    
    def clearTimeout(self, taskId):
        self.removeTask(TIMER_TASK, taskId)


def addTimer(period, fn):
    GameServer = compServer.CreateGame(serverApi.GetLevelId())
    GameClient = compClient.CreateGame(clientApi.GetLevelId())
    game = GameServer if isServer() else GameClient
    return game.AddRepeatedTimer(period, fn)

def cancelTimer(timer):
    GameServer = compServer.CreateGame(serverApi.GetLevelId())
    GameClient = compClient.CreateGame(clientApi.GetLevelId())
    game = GameServer if isServer() else GameClient
    game.CancelTimer(timer)

class TimerAdapter:
    def __init__(self, period, fn):
        self.period = period
        self.fn = fn
        self.timer = None
    
    def start(self):
        self.timer = addTimer(self.period, self.fn)

    def cancel(self):
        if self.timer:
            cancelTimer(self.timer)
            self.timer = None


class SchedulerPoller:
    def __init__(self, scheduler, period=1):
        # type: (Scheduler, float) -> None
        self.period = period
        self.scheduler = scheduler
        self.timer = TimerAdapter(self.period, lambda: scheduler.executeSequence())

    def start(self):
        self.timer.start()

    def cancel(self):
        self.timer.cancel()


class SimpleFixedScheduler(SchedulerPoller):
    def __init__(self, period=1):
        SchedulerPoller.__init__(self, Scheduler(), period)


class Sched:
    TYPE_TICK = 1
    TYPE_RENDER = 2
    TYPE_FIXED = 3

    @staticmethod
    def Tick(scheduleName=SCHED_UPDATE):
        def wrapper(fn):
            AnnotationHelper.addAnnotation(fn, SYSTEM_SCHED_ANNO, [Sched.TYPE_TICK, scheduleName])
            return fn
        return wrapper

    @staticmethod
    def Render(scheduleName=SCHED_UPDATE):
        def wrapper(fn):
            AnnotationHelper.addAnnotation(fn, SYSTEM_SCHED_ANNO, [Sched.TYPE_RENDER, scheduleName])
            return fn
        return wrapper
    
    @staticmethod
    def Fixed(schedulerName):
        # type: (str) -> FunctionType
        def wrapper(fn):
            AnnotationHelper.addAnnotation(fn, SYSTEM_SCHED_ANNO, [Sched.TYPE_FIXED, schedulerName])
            return fn
        return wrapper