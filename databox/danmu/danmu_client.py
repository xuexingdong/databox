import abc
import asyncio
import ssl

import aiohttp


class DanmuClient(abc.ABC):
    def __init__(self, room_id: str, danmu_url=None):
        self.room_id = room_id
        self.danmu_url = danmu_url
        self.ws = None
        self.msg_queue = asyncio.Queue()

    async def _connect(self):
        if self.danmu_url is None:
            self.danmu_url = await self._get_danmu_url()
        ssl_context = ssl.create_default_context()
        ssl_context.set_ciphers('DEFAULT')
        headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36'
        }
        session = aiohttp.ClientSession()
        self.ws = await session.ws_connect(self.danmu_url, ssl=ssl_context, headers=headers)
        await self._login()

    @abc.abstractmethod
    async def _get_danmu_url(self):
        pass

    @abc.abstractmethod
    async def _login(self):
        pass

    async def _heartbeat(self):
        while True:
            await self.ws.send_bytes(self._build_heartbeat_packet())
            await asyncio.sleep(45)

    @staticmethod
    @abc.abstractmethod
    def _build_heartbeat_packet():
        pass

    async def _recv_data(self):
        buffer = bytearray()
        while True:
            data = await self.ws.receive_bytes()
            buffer.extend(data)
            frame_len = self._next_frame_len(buffer)
            if frame_len > 0:
                msg = self._frame_to_msg(buffer[:frame_len])
                buffer = buffer[frame_len:]
                await self.msg_queue.put(msg)
            else:
                break

    async def _process_messages(self):
        while True:
            msg = await self.msg_queue.get()
            self._parse_msg(msg)
            self.msg_queue.task_done()

    @staticmethod
    @abc.abstractmethod
    def _next_frame_len(buffer) -> (int, int):
        pass

    @staticmethod
    @abc.abstractmethod
    def _frame_to_msg(param):
        pass

    @staticmethod
    @abc.abstractmethod
    def _parse_msg(msg):
        pass

    async def start(self):
        await self._connect()
        heartbeat_task = asyncio.create_task(self._heartbeat())
        recv_task = asyncio.create_task(self._recv_data())
        process_task = asyncio.create_task(self._process_messages())
        try:
            await asyncio.gather(heartbeat_task, recv_task, process_task)
        except asyncio.CancelledError:
            await self.ws.close()
