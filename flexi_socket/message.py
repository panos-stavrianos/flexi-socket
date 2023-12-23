class Message:
    def __init__(self, message, processed_message=None, incoming=False):
        self.message = message
        self.processed_message = processed_message
        if processed_message is None:
            self.processed_message = message
        self.incoming = incoming

    def __str__(self):
        return f"{'Incoming' if self.incoming else 'Outgoing'} message: {self.message}\n\t processed: {self.processed_message}"
