class EventNotValidException(Exception):
    
    def __init__(self, event_name: str, message: str = "Event not valid"):
        self.event_name = event_name
        self.message = f"{message}: {event_name}"
        super().__init__(self.message)