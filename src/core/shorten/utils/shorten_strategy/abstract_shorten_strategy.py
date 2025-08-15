from abc import ABC, abstractmethod


class ShortCodeStrategy(ABC):
    @abstractmethod
    def generate(self, url_id: int) -> str: ...
