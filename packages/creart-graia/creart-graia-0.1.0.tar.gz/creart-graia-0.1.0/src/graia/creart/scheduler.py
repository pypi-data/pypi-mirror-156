from __future__ import annotations

from typing import TYPE_CHECKING

from creart import AbstractCreator, CreateTargetInfo, it

from .broadcast import BroadcastCreator

if TYPE_CHECKING:
    from graia.scheduler import GraiaScheduler
    from graia.scheduler.saya.behaviour import GraiaSchedulerBehaviour


class SchedulerCreator(AbstractCreator):
    targets = (CreateTargetInfo("graia.scheduler", "Scheduler"),)

    @staticmethod
    def available() -> bool:
        try:
            import graia.scheduler

            return BroadcastCreator.available()
        except ImportError:
            return False

    @staticmethod
    def create(create_type: type[GraiaScheduler]) -> GraiaScheduler:
        from graia.broadcast import Broadcast

        broadcast = it(Broadcast)
        return create_type(loop=broadcast.loop, broadcast=broadcast)


class SchedulerBehaviourCreator(AbstractCreator):
    targets = (
        CreateTargetInfo("graia.scheduler.saya.behaviour", "GraiaSchedulerBehaviour"),
    )

    @staticmethod
    def available() -> bool:
        try:
            import graia.saya

            return SchedulerCreator.available()
        except ImportError:
            return False

    @staticmethod
    def create(create_type: type[GraiaSchedulerBehaviour]) -> GraiaSchedulerBehaviour:
        from graia.scheduler import GraiaScheduler

        scheduler = it(GraiaScheduler)
        return create_type(scheduler)
