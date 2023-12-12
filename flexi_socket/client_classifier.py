class ClientClassifier:
    DEFAULT = "default"
    def __init__(self):
        self.client_types = []

    def classify(self, first_message):
        return ClientClassifier.DEFAULT
