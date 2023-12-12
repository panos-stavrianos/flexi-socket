from time import sleep

from flexi_socket import Protocol, Mode, FlexiSocket, Connection

while True:
    client = FlexiSocket(mode=Mode.CLIENT,
                         protocol=Protocol.TCP,
                         host="0.0.0.0",
                         port=8080)


    @client.on_connect()
    async def on_connect_(connection: Connection):
        print(f"Connected to {connection}")
        await connection.send("!!Hello from client 1")


    client.start()
    sleep(1)
