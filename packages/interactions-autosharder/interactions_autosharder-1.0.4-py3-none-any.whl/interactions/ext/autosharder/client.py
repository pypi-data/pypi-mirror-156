import asyncio
from typing import Coroutine, Optional, Union

from interactions.api.models.misc import MISSING, Snowflake
from interactions.client.bot import Client
from interactions.client.models.command import ApplicationCommand
from interactions.client.models.component import Button, Modal, SelectMenu

from .dummy import _Client


class ShardedClient(Client):
    def __init__(self, token: str, shard_count: int = MISSING, **kwargs):
        super().__init__(token, **kwargs)
        self.shards = []
        self._clients = []
        if shard_count and shard_count != MISSING and isinstance(shard_count, int):
            self._shard_count = shard_count
        else:
            self._shard_count = self._loop.run_until_complete(self._get_shard_count())
        self.generate_shard_list()

        for shard in self.shards:
            if not self._clients:
                _client = Client(token, shards=shard, **kwargs)
            else:
                kwargs["disable_sync"] = True
                _client = _Client(token, shards=shard, **kwargs)
            self._clients.append(_client)

    @property
    def latency(self) -> float:
        _latencies = [client.latency for client in self._clients]
        return sum(_latencies) / len(_latencies)

    async def _get_shard_count(self) -> int:
        data = await self._http.get_bot_gateway()
        return data[0]

    async def _ready(self) -> None:
        await self._login()

    def generate_shard_list(self) -> None:
        """
        Generates a list of shards.
        """
        for shard in range(self._shard_count):
            self.shards.append([shard, self._shard_count])

    async def _login(self) -> None:

        if self._clients[0]._automate_sync:
            await self._clients[0]._Client__sync()
            self._clients[0]._automate_sync = False

        _funcs = [client._ready() for client in self._clients]
        gathered = asyncio.gather(*_funcs)
        while not self._websocket._closed:
            await gathered

    def command(
        self,
        **kwargs,
    ):
        def decorator(coro: Coroutine):
            for client in self._clients[1:]:
                client.command(**kwargs)(coro)

            return self._clients[0].command(**kwargs)(coro)

        return decorator

    def message_command(
        self,
        **kwargs,
    ):
        def decorator(coro: Coroutine):
            for client in self._clients[1:]:
                client.message_command(**kwargs)(coro)
            return self._clients[0].message_command(**kwargs)(coro)

        return decorator

    def user_command(
        self,
        **kwargs,
    ):
        def decorator(coro: Coroutine):
            for client in self._clients[1:]:
                client.user_command(**kwargs)(coro)
            return self._clients[0].user_command(**kwargs)(coro)

        return decorator

    def component(self, component: Union[Button, SelectMenu, str]):
        def decorator(coro: Coroutine):
            for client in self._clients[1:]:
                client.component(component)(coro)
            return self._clients[0].component(component)(coro)

        return decorator

    def autocomplete(self, command: Union[ApplicationCommand, int, str, Snowflake], name: str):
        def decorator(coro: Coroutine) -> None:
            for client in self._clients[1:]:
                client.autocomplete(command, name)(coro)
            return self._clients[0].autocomplete(command, name)(coro)

        return decorator

    def modal(self, modal: Union[Modal, str]):
        def decorator(coro: Coroutine) -> None:
            for client in self._clients[1:]:
                client.modal(modal)(coro)
            return self._clients[0].modal(modal)(coro)

        return decorator

    def event(self, coro: Optional[Coroutine] = MISSING, **kwargs):
        def decorator(coro: Coroutine):
            for client in self._clients[1:]:
                client.event(**kwargs)(coro)

            return self._clients[0].event(**kwargs)(coro)

        if coro is not MISSING:
            for client in self._clients[1:]:
                client.event(**kwargs)(coro)
            return self._clients[0].event(**kwargs)(coro)

        return decorator
