from abc import ABC, abstractmethod


class AbstractMessageQueue(ABC):
    """
    An abstract base class defining the interface for a message queue client.
    """

    @abstractmethod
    async def publish(self, message: dict):
        """Publishes a message to the queue."""
        pass

    @abstractmethod
    async def get_batch(self, batch_size: int) -> list[dict]:
        """Fetches a batch of messages from the queue."""
        pass

    @abstractmethod
    async def close(self):
        """Closes the connection to the message queue."""
        pass
