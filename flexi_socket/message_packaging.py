# message_packaging.py
from __future__ import annotations

import asyncio
from abc import ABC


class MessageStrategy(ABC):

    def __init__(self):
        self.reader: asyncio.StreamReader | None = None
        self.writer: asyncio.StreamWriter | None = None

    def set_reader_writer(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        self.reader = reader
        self.writer = writer

    def pack_message(self, message):
        pass

    def unpack_message(self):
        pass

    async def send(self, message):
        pass

    async def receive(self):
        pass

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

        self.reader.feed_eof()

    def __str__(self):
        return f"{self.__class__.__name__}"

    def clone(self) -> MessageStrategy:
        """Create a clone of the current strategy."""
        return self.__class__()


class EOFStrategy(MessageStrategy):

    async def send(self, message):
        if isinstance(message, str):
            message = message.encode()

        self.writer.write(message)
        self.writer.write_eof()
        await self.writer.drain()

    async def receive(self) -> bytes:
        return await self.reader.read(-1)


class SeparatorStrategy(MessageStrategy):
    separator: str

    def __init__(self, separator: str = "\n"):
        super().__init__()
        self.separator = separator

    async def send(self, message: bytes | str):
        if isinstance(message, str):
            message = message.encode()

        message += self.separator.encode()
        self.writer.write(message)

        await self.writer.drain()

    async def receive(self):
        return await self.reader.readuntil(self.separator.encode())


class FixedLengthStrategy(MessageStrategy):
    length: int

    def __init__(self, length: int = 1024):
        super().__init__()
        self.length = length

    async def send(self, message):
        if isinstance(message, str):
            message = message.encode()
        message += b" " * (self.length - len(message))
        self.writer.write(message)
        await self.writer.drain()

    async def receive(self):
        print("waiting for read", self.__repr__())
        data = await self.reader.read(self.length)
        print("read data", data)
        return data


class TimeoutStrategy(MessageStrategy):
    timeout: int

    def __init__(self, timeout: int = 1):
        super().__init__()
        self.timeout = timeout

    async def send(self, message):
        message = message.encode()
        self.writer.write(message)
        await self.writer.drain()

    async def receive(self):
        while True:
            try:
                return await asyncio.wait_for(self.reader.read(-1), timeout=self.timeout)
            except asyncio.TimeoutError:
                await asyncio.sleep(1)
