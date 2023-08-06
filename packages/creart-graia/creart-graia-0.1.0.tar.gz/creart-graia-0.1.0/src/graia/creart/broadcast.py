from __future__ import annotations

from typing import TYPE_CHECKING

from creart import AbstractCreator, CreateTargetInfo, it

if TYPE_CHECKING:
    from graia.broadcast import Broadcast
    from graia.saya.builtins.broadcast.behaviour import BroadcastBehaviour


class BroadcastCreator(AbstractCreator):
    targets = (CreateTargetInfo("graia.broadcast", "Broadcast"),)

    @staticmethod
    def available() -> bool:
        try:
            import graia.broadcast

            return True
        except ImportError:
            return False

    @staticmethod
    def create(create_type: type[Broadcast]) -> Broadcast:
        import asyncio

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        return create_type(loop=loop)


class BroadcastBehaviourCreator(AbstractCreator):
    targets = (
        CreateTargetInfo("graia.saya.builtins.broadcast.behaviour", "Broadcast"),
    )

    @staticmethod
    def available() -> bool:
        try:
            import graia.broadcast
            import graia.saya

            return True
        except ImportError:
            return False

    @staticmethod
    def create(create_type: type[BroadcastBehaviour]) -> BroadcastBehaviour:
        broadcast = it(Broadcast)
        return create_type(broadcast)
