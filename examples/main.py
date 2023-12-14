# from rich import print

from flexi_socket import ClientClassifier
from flexi_socket import Connection
from flexi_socket import FlexiSocket
from flexi_socket import Protocol, Mode


class ClientTypes(ClientClassifier):
    client_types = ["001", "002", "003"]

    def classify(self, first_message):
        if first_message.startswith("!!"):
            return ClientTypes.client_types[0]
        elif first_message.startswith("##"):
            return ClientTypes.client_types[1]
        else:
            return ClientClassifier.DEFAULT


server = FlexiSocket(mode=Mode.SERVER,
                     protocol=Protocol.TCP,
                     port=8080,
                     classifier=ClientTypes())


@server.on_connect()
async def on_connect(connection: Connection):
    print(f"Connected to {connection}")


@server.on_disconnect()
async def on_disconnect(connection: Connection):
    print(f"Disconnected from {connection}")


@server.on_message(ClientTypes.client_types[0])
async def handle_client_001(client: Connection, message: str):
    if client.is_first_message_from_client:
        print("First message from client")
    print(f"Client {client} sent {message}")
    client.state = "some state"

    client.print_history()
    await client.send("Hello from server! You are type 001")


@server.on_message()
async def handle_client_def(client: Connection, message: str):
    print(f"Client {client} sent {message}")
    await client.send("Hello from server! You are type DEFAULT")


@server.after_receive(ClientTypes.client_types[0])
async def handle_client_001_pre(client: Connection, message: str) -> str:
    return message.strip("!!")


@server.before_send(ClientTypes.client_types[0])
async def handle_client_001_before_send(client: Connection, message: str) -> str:
    return f"{message}!!@@"


@server.on_message(ClientTypes.client_types[1], ClientTypes.client_types[2])
async def handle_client_002_or_003(client: Connection, message: str):
    print(f"Client {client.address}:{client.port} type of {client.client_type} sent {message}")
    await client.send("Hello from server! You are type 002 or 003")


server.start()
