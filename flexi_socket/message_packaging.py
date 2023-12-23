# message_packaging.py
from __future__ import annotations

import asyncio
from abc import ABC


class MessageStrategy(ABC):
    reader: asyncio.StreamReader
    writer: asyncio.StreamWriter

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
        self.length = length

    async def send(self, message):
        message = message.encode()
        message += b" " * (self.length - len(message))
        self.writer.write(message)
        await self.writer.drain()

    async def receive(self):
        return await self.reader.read(self.length)


class TimeoutStrategy(MessageStrategy):
    timeout: int

    def __init__(self, timeout: int = 1):
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
