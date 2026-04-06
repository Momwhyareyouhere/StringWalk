import asyncio
import contextlib
import socket


LOBBY_PORT = 50555


class LobbyManager:
    def __init__(self):
        self.server = None
        self.server_task = None
        self.reader_task = None
        self.client_writer = None
        self.client_reader = None
        self.peer_writer = None
        self.is_host = False
        self.players = []
        self.status = "No active lobby."
        self.host_address = ""
        self.listeners = set()
        self.closing = False

    def register_listener(self, callback):
        self.listeners.add(callback)

    def unregister_listener(self, callback):
        self.listeners.discard(callback)

    def snapshot(self):
        return {
            "is_host": self.is_host,
            "players": list(self.players),
            "status": self.status,
            "host_address": self.host_address,
            "has_lobby": self.server is not None or self.client_writer is not None,
        }

    def _notify(self):
        state = self.snapshot()
        for callback in list(self.listeners):
            callback(state)

    def _get_local_ip(self):
        try:
            probe = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            probe.connect(("8.8.8.8", 80))
            return probe.getsockname()[0]
        except OSError:
            return "127.0.0.1"
        finally:
            if "probe" in locals():
                probe.close()

    def _normalize_join_host(self, host: str):

        local_ip = self._get_local_ip()
        if host in {"localhost", "127.0.0.1", local_ip}:
            return "127.0.0.1"
        return host

    async def host_lobby(self, port=LOBBY_PORT):
        await self.close_lobby()

        self.closing = False
        self.is_host = True
        self.players = ["Player 1"]
        self.host_address = self._get_local_ip()
        self.status = f"Lobby created at {self.host_address}:{port}"
        self.server = await asyncio.start_server(self._handle_client, "0.0.0.0", port)
        self.server_task = asyncio.create_task(self.server.serve_forever())
        self._notify()

    async def join_lobby(self, host, port=LOBBY_PORT):
        await self.close_lobby()

        self.closing = False
        connect_host = self._normalize_join_host(host)
        self.client_reader, self.client_writer = await asyncio.open_connection(connect_host, port)
        self.is_host = False
        self.host_address = host
        self.players = ["Player 1", "Player 2"]
        self.status = f"Joined lobby at {host}:{port}"
        self.reader_task = asyncio.create_task(self._watch_host())
        self._notify()

    async def close_lobby(self):
        self.closing = True

        if self.reader_task is not None:
            self.reader_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.reader_task
            self.reader_task = None

        if self.server_task is not None:
            self.server_task.cancel()
            with contextlib.suppress(asyncio.CancelledError):
                await self.server_task
            self.server_task = None

        if self.client_writer is not None:
            self.client_writer.close()
            with contextlib.suppress(Exception):
                await self.client_writer.wait_closed()
            self.client_writer = None
            self.client_reader = None

        if self.peer_writer is not None:
            self.peer_writer.close()
            with contextlib.suppress(Exception):
                await self.peer_writer.wait_closed()
            self.peer_writer = None

        if self.server is not None:
            self.server.close()
            with contextlib.suppress(Exception):
                await self.server.wait_closed()
            self.server = None

        self.is_host = False
        self.players = []
        self.host_address = ""
        self.status = "No active lobby."
        self._notify()
        self.closing = False

    async def _handle_client(self, reader, writer):
        if self.peer_writer is not None:
            writer.close()
            with contextlib.suppress(Exception):
                await writer.wait_closed()
            return

        self.peer_writer = writer
        self.players = ["Player 1", "Player 2"]
        self.status = f"Player 2 joined {self.host_address}:{LOBBY_PORT}"
        self._notify()

        try:
            while await reader.read(1024):
                pass
        except (ConnectionError, OSError):
            pass
        finally:
            if self.peer_writer is writer:
                self.peer_writer = None
                if not self.closing:
                    self.players = ["Player 1"]
                    self.status = f"Lobby created at {self.host_address}:{LOBBY_PORT}"
                    self._notify()
            writer.close()
            with contextlib.suppress(Exception):
                await writer.wait_closed()

    async def _watch_host(self):
        try:
            while await self.client_reader.read(1024):
                pass
        except (ConnectionError, OSError):
            pass
        finally:
            self.client_writer = None
            self.client_reader = None
            if not self.closing:
                self.players = []
                self.status = "Disconnected from lobby."
                self._notify()


lobby_manager = LobbyManager()
