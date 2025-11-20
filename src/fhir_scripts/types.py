class Url:
    def __init__(self, url: str):
        self.url = url

    def __str__(self) -> str:
        return self.url

    def __repr__(self) -> str:
        return "<url={}>".format(self.url)

    def __truediv__(self, other: str) -> "Url":
        return Url(self.url + "/" + other.strip("/"))

    def endswith(self, value: str) -> bool:
        return self.url.endswith(value)

    def __eq__(self, value: object) -> bool:
        return isinstance(value, Url) and self.url == value.url

    @property
    def name(self) -> str:
        return self.url.rsplit("/", 1)[-1]

    def is_dir(self):
        return "." not in self.name
