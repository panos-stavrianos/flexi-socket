from flexi_socket import Connection
from flexi_socket import FlexiSocket
from flexi_socket import Protocol, Mode

server = FlexiSocket(mode=Mode.SERVER,
                     protocol=Protocol.TCP,
                     port=8009, read_buffer_size=1024)


@server.on_message()
async def on_message(client: Connection, message: str):
    if client.is_first_message_from_client:
        print("First message from client")
    print(f"Client {client} sent {message}")
    client.state = "some state"

    client.print_history()
    await client.send("Hello from server! You are type 001")


@server.on_connect()
async def on_connect(client: Connection):
    print(f"Client {client} connected!")
    client.data = "some data"


@server.on_disconnect()
async def on_disconnect(client: Connection):
    print(f"Client {client.data} disconnected!")


server.start()
