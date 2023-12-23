# tests
import asyncio

import pytest

from flexi_socket import FlexiSocket, Mode, Protocol, Connection
from flexi_socket.flexi_socket import Listener
from flexi_socket.message_packaging import SeparatorStrategy, EOFStrategy


async def server_on_message(connection: Connection, message: str):
    print(f"server_on_message: {message}")


async def client_on_message(connection: Connection, message: str):
    print(f"client_on_message: {message}")


async def server_on_connect(connection: Connection):
    print(f"server_on_connect: {connection}")
    await asyncio.sleep(2)
    await connection.send("Hello from server99")


async def client_on_connect(connection: Connection):
    print(f"client_on_connect: {connection}")


@pytest.mark.asyncio
async def test_server_client_communication():
    # Setup server
    server = FlexiSocket(mode=Mode.SERVER, protocol=Protocol.TCP, host="127.0.0.1", port=8009,
                         message_strategy=SeparatorStrategy())
    server.add_listener(Listener.ON_MESSAGE, server_on_message)
    server.add_listener(Listener.ON_CONNECT, server_on_connect)

    # Setup client
    client = FlexiSocket(mode=Mode.CLIENT, protocol=Protocol.TCP, host="127.0.0.1", port=8009,
                         message_strategy=SeparatorStrategy())
    client.add_listener(Listener.ON_MESSAGE, client_on_message)
    client.add_listener(Listener.ON_CONNECT, client_on_connect)

    print("Initialized server and client")

    # Start server and client
    s_task = asyncio.create_task(server.start_async())
    await asyncio.sleep(.5)
    c_task = asyncio.create_task(client.start_async())
    await asyncio.sleep(.5)

    print("Server and client started")
    # Test sending and receiving messages
    # ...
    for i in range(1):
        await asyncio.sleep(.5)
        for connection in server.connections:
            await connection.send(f"@@Hello from server {i}")

        await asyncio.sleep(.5)
        for connection in client.connections:
            await connection.send(f"@@Hello from client {i}")
    # Assert conditions - for example, correct message received, correct callbacks triggered, etc.
    print("Asserting conditions")
    await asyncio.sleep(2)
    print("Asserting conditions done")

    # Teardown server and client
    await client.stop_async()
    await server.stop_async()
    await asyncio.gather(s_task, c_task)
