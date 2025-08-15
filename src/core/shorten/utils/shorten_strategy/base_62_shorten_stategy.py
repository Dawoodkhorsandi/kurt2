import string

from .abstract_shorten_strategy import ShortCodeStrategy


class Base62ShortCodeStrategy(ShortCodeStrategy):
    def __init__(self):
        self.characters = string.digits + string.ascii_letters  # 0-9a-zA-Z

    def generate(self, url_id: int) -> str:
        if url_id == 0:
            return self.characters[0]

        base62_str = []
        base = len(self.characters)

        num = url_id
        while num > 0:
            num, remainder = divmod(num, base)
            base62_str.append(self.characters[remainder])

        return "".join(reversed(base62_str))
