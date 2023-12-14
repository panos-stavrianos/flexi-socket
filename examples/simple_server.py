from flexi_socket import Connection
from flexi_socket import FlexiSocket
from flexi_socket import Protocol, Mode

server = FlexiSocket(mode=Mode.SERVER,
                     protocol=Protocol.TCP,
                     port=8081, read_buffer_size=1024)


@server.on_message()
async def on_message(client: Connection, message: str):
    if client.is_first_message_from_client:
        print("First message from client")
    print(f"Client {client} sent {message}")
    client.state = "some state"

    client.print_history()
    await client.send("Hello from server! You are type 001")


server.start()
