# Flexi-Socket

**Note:** This project is under ongoing development, with additional features planned for future releases.

## Overview

`Flexi-Socket` is a Python library for developing robust server and client socket applications. It supports TCP protocol
and is capable of handling connections, messages, and disconnections in both server and client modes. The library is
equipped with message classification and string message handling, suitable for a range of network programming needs.

[View on PyPI](https://pypi.org/project/flexi-socket/)

## Installation

```python
pip install flexi-socket
```

## General Setup

### Importing the Library

```python
from flexi_socket import FlexiSocket, Connection, Protocol, Mode
```

### Creating a Socket

Create a socket instance for server or client:

```python
socket = FlexiSocket(mode=Mode.SERVER, protocol=Protocol.TCP, port=8081, read_buffer_size=1024)  # Server
# or
socket = FlexiSocket(mode=Mode.CLIENT, protocol=Protocol.TCP, host="0.0.0.0", port=8080)  # Client
```

### Event Handlers

Implement event handlers for operations like connect, message handling, and disconnect:

#### On Connect

```python
@socket.on_connect()
async def on_connect(connection: Connection):
    print(f"Connected to {connection}")
    # Additional logic
```

#### On Disconnect

```python
@socket.on_disconnect()
async def on_disconnect(connection: Connection):
    print(f"Disconnected from {connection}")
    # Additional logic
```

#### On Message

```python
@socket.on_message()
async def on_message(connection: Connection, message: str):
    print(f"Received message from {connection}: {message}")
    # Additional logic
```

#### After Receive and Before Send

This can be used to implement start/end bytes, checksums, message cleanup or any other logic that needs to be
applied to the message but without cluster the `on_message` handler. 
A future implementation will combine these two handlers into one using something like yield.

```python
@socket.after_receive()
async def after_receive(connection: Connection, message: str):
    print(f"Received message from {connection}: {message}")
    # Additional logic


@socket.before_send()
async def before_send(connection: Connection, message: str):
    print(f"Sending message to {connection}: {message}")
    # Additional logic
```

### Sending Messages

To send a message:

```python
await socket.send("Your message here")
```

### Starting the Socket

```python
socket.start()
# or 
await socket.start_async()
```

## Using Message Classification

Message classification allows handling different message types based on first message received from a client.
This is useful because a lot of protocols include a handshake message, which can be used to identify the type of client
(very popular in alarm systems).

> This is an attempt to make something similar to http routing, but for classic socket programming.

```python
class ClientTypes(ClientClassifier):
    client_types = ["001", "002", "003"]

    def classify(self, first_message):
        if first_message.startswith("!!"):
            return ClientTypes.client_types[0]
        elif first_message.startswith("##"):
            return ClientTypes.client_types[1]
        else:
            return ClientClassifier.DEFAULT
```

### Using the Classifier

```python
@socket.on_message(ClientTypes.client_types[0])
async def handle_client_001(client: Connection, message: str):
    if client.is_first_message_from_client:
        print("First message from client")
    print(f"Client {client} sent {message}")
    await client.send("Hello from server! You are type 001")
```

## Planned Features

- **UDP Protocol Support:** Future implementation to handle UDP connections.
- **Binary Message Support:** Upgrade to allow sending and receiving binary data, in addition to string messages.