from flexi_socket import Protocol, Mode, FlexiSocket, Connection

client = FlexiSocket(mode=Mode.CLIENT,
                     protocol=Protocol.TCP,
                     host="0.0.0.0",
                     port=8009)


@client.on_connect()
async def on_connect(connection:  Connection):
    print(f"Connected to {connection}")
    await connection.send("!!Hello from client 1")


@client.on_disconnect()
async def on_disconnect(connection: Connection):
    print(f"Disconnected from {connection}")


client.start()
