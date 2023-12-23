# flexi_socket.py
import asyncio
import traceback
from enum import Enum
from typing import Union

from flexi_socket.client_classifier import ClientClassifier
from flexi_socket.connection import Connection
from flexi_socket.constraints import Protocol, Mode
from flexi_socket.message_packaging import MessageStrategy, EOFStrategy


class Listener(Enum):
    """
    Type of listener.
    """
    ON_CONNECT = 0
    ON_DISCONNECT = 1
    ON_MESSAGE = 2
    AFTER_RECEIVE = 3
    BEFORE_SEND = 4


class State(Enum):
    """
    State of the socket.
    """
    STOPPED = 0
    STARTING = 1
    RUNNING = 2
    STOPPING = 3


class FlexiSocket:
    def __init__(self, mode: Union[Mode.SERVER, Mode.CLIENT] = Mode.SERVER,
                 protocol: Union[Protocol.TCP, Protocol.UDP] = Protocol.TCP,
                 message_strategy: MessageStrategy = EOFStrategy(),
                 host="0.0.0.0", port=None, classifier=None, read_buffer_size=-1):
        self.mode = mode
        self.message_strategy = message_strategy
        self.protocol = protocol
        self.stop_event = asyncio.Event()
        self.host = host
        if port is None:
            raise ValueError("Port cannot be None, please specify a port.")
        self.port = port

        self.classifier = ClientClassifier() if classifier is None else classifier
        self.connections = []
        self.on_connect_handler = None
        self.on_disconnect_handler = None
        self.handlers = {}
        self.after_receive_handlers = {}
        self.post_send_handlers = {}
        self.state = State.STOPPED

        self.read_buffer_size = read_buffer_size

    def start(self):
        asyncio.run(self.start_async())

    def stop(self):
        print("Stopping server")
        self.stop_event.set()

    async def start_async(self):
        if self.state == State.RUNNING:
            return

        self.state = State.STARTING

        if self.protocol == Protocol.TCP:
            await self.tcp_socket()
        elif self.protocol == Protocol.UDP:
            raise NotImplementedError

    async def stop_async(self):
        print(f"Stopping {self}!!!", self.state)
        if self.state != State.RUNNING:
            return
        self.stop_event.set()
        print(f"Emitting stop event {self.stop_event.is_set()}")

        while self.state == State.STOPPED:
            print("Waiting for server to stop", self.state)
            await asyncio.sleep(1)

    async def tcp_socket(self):
        socket = None
        if self.mode == Mode.SERVER:
            socket = await asyncio.start_server(self.handle_new_connection_tcp, self.host, self.port)
            try:
                async with socket:
                    self.state = State.RUNNING
                    await self.stop_event.wait()
            except Exception as e:
                traceback.print_exc()
            except asyncio.CancelledError as e:
                traceback.print_exc()
                raise e
            finally:
                await self.message_strategy.close()
                self.state = State.STOPPED
        elif self.mode == Mode.CLIENT:
            _reader, _writer = await asyncio.open_connection(self.host, self.port)
            socket = asyncio.create_task(self.handle_new_connection_tcp(_reader, _writer))
            try:
                self.state = State.RUNNING
                await self.stop_event.wait()
            except Exception as e:
                traceback.print_exc()
            except asyncio.CancelledError as e:
                traceback.print_exc()
                raise e
            finally:
                await self.message_strategy.close()
                self.state = State.STOPPED

    def add_listener(self, listener: Listener, handler):
        if listener == Listener.ON_CONNECT:
            self.on_connect_handler = handler
        elif listener == Listener.ON_MESSAGE:
            self.handlers[ClientClassifier.DEFAULT] = handler
        elif listener == Listener.AFTER_RECEIVE:
            self.after_receive_handlers[ClientClassifier.DEFAULT] = handler
        elif listener == Listener.BEFORE_SEND:
            self.post_send_handlers[ClientClassifier.DEFAULT] = handler
        elif listener == Listener.ON_DISCONNECT:
            raise NotImplementedError
        else:
            raise ValueError(f"Unknown listener {listener}, please use one of {Listener}")

    async def handle_new_connection_tcp(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
        connection = Connection(reader=reader, writer=writer,
                                classifier=self.classifier,
                                message_strategy=self.message_strategy,
                                after_receive_handlers=self.after_receive_handlers,
                                before_send_handlers=self.post_send_handlers,
                                receive_handlers=self.handlers,
                                read_buffer_size=self.read_buffer_size)

        self.connections.append(connection)
        if self.on_connect_handler is not None:
            await self.on_connect_handler(connection)
        try:
            await connection.receive()
        except asyncio.CancelledError:
            await connection.close()
        if self.on_disconnect_handler:
            await self.on_disconnect_handler(connection)
        self.connections.remove(connection)

    def on_connect(self):
        def decorator(func):
            async def wrapper(client):
                return await func(client)

            self.on_connect_handler = wrapper
            return wrapper

        return decorator

    def on_disconnect(self):
        def decorator(func):
            async def wrapper(client):
                return await func(client)

            self.on_disconnect_handler = wrapper
            return wrapper

        return decorator

    def on_message(self, *client_types):
        def decorator(func):
            if not client_types:
                self.handlers[ClientClassifier.DEFAULT] = func
            for client_type in client_types:
                self.handlers[client_type] = func
            return func

        return decorator

    def after_receive(self, *client_types):
        def decorator(func):
            async def wrapper(client, message):
                return await func(client, message)

            if not client_types:
                self.after_receive_handlers[ClientClassifier.DEFAULT] = wrapper
            for client_type in client_types:
                self.after_receive_handlers[client_type] = wrapper
            return wrapper

        return decorator

    def before_send(self, *client_types):
        def decorator(func):
            async def wrapper(client, message):
                return await func(client, message)

            if not client_types:
                self.post_send_handlers[ClientClassifier.DEFAULT] = wrapper
            for client_type in client_types:
                self.post_send_handlers[client_type] = wrapper
            return wrapper

        return decorator

    def __str__(self):
        return f"FlexiSocket: {self.mode}, {self.protocol}, {self.host}:{self.port}"
