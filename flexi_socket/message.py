class Message:
    def __init__(self, message, processed_message=None, from_client=False, from_server=False):
        self.message = message
        self.processed_message = processed_message
        if processed_message is None:
            self.processed_message = message
        self.from_client = from_client
        self.from_server = from_server

    def __str__(self):
        if self.from_client:
            return f"From Client: {self.message.strip()}, Processed: {self.processed_message.strip()}"
        elif self.from_server:
            return f"From Server: {self.message.strip()}, Processed: {self.processed_message.strip()}"
        else:
            return f"{self.message.strip()}, Processed: {self.processed_message.strip()}"
