import asyncio

from flexi_socket.message import Message


class Connection:
    def __init__(self, reader: asyncio.StreamReader, writer: asyncio.StreamWriter,
                 client_type=None,
                 classifier=None,
                 after_receive_handlers=None,
                 before_send_handlers=None,
                 receive_handlers=None,
                 read_buffer_size=-1):
        self.address = writer.get_extra_info('peername')[0]
        self.port = writer.get_extra_info('peername')[1]

        self.read_buffer_size = read_buffer_size
        self.client_type = client_type
        self.reader = reader
        self.writer = writer
        self.history = []
        self.status = "connected"
        self.state = None
        self.data = None
        self.classifier = classifier

        self.after_receive_handlers = after_receive_handlers
        self.before_send_handlers = before_send_handlers
        self.receive_handlers = receive_handlers

        self.after_receive_handler = None
        self.before_send_handler = None
        self.receive_handler = None

    @property
    def is_connected(self):
        return self.status == "connected"

    @property
    def messages_from_client(self):
        return [message for message in self.history if message.from_client]

    @property
    def messages_from_server(self):
        return [message for message in self.history if message.from_server]

    @property
    def is_first_message_from_client(self):
        return len(self.messages_from_client) == 1

    async def send(self, message: str):
        processed_message = message
        if self.before_send_handler:
            processed_message = await self.before_send_handler(self, message)
        self.history.append(Message(message, processed_message, from_server=True))
        processed_message = processed_message.encode()
        self.writer.write(processed_message)
        self.writer.write_eof()

        await self.writer.drain()

    async def receive(self):
        while True:
            try:
                message = (await self.reader.read(self.read_buffer_size)).decode()
            except ConnectionResetError:
                self.status = "disconnected"
                break
            if not message:
                self.status = "disconnected"
                break
            is_first_message = len(self.history) == 0
            if is_first_message:
                self.process_first_message(message)
            processed_message = message
            if self.after_receive_handler:
                processed_message = await self.after_receive_handler(self, processed_message)
            self.history.append(Message(message, processed_message, from_client=True))

            if self.receive_handler:
                await asyncio.create_task(self.receive_handler(self, processed_message))

        print(f"TCP connection from {self} closed")
        try:
            await self.close()
        except ConnectionResetError as e:
            pass

    async def close(self):
        self.writer.close()
        await self.writer.wait_closed()

        self.reader.feed_eof()

    def process_first_message(self, first_message):
        if not self.classifier:
            return
        self.client_type = self.classifier.classify(first_message)
        if self.client_type in self.after_receive_handlers:
            self.after_receive_handler = self.after_receive_handlers[self.client_type]
        if self.client_type in self.before_send_handlers:
            self.before_send_handler = self.before_send_handlers[self.client_type]
        if self.client_type in self.receive_handlers:
            self.receive_handler = self.receive_handlers[self.client_type]

    def __str__(self):
        return f"SocketClient: Address={self.address}, Port={self.port}, ClientType={self.client_type}"

    def print_history(self):
        print("-----------------------------------")
        for message in self.history:
            print(message)
        print("-----------------------------------")
