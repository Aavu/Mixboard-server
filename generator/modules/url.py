
class Url:
    def __init__(self, url: str) -> None:
        self._url = url

    def get(self) -> str:
        return self._url
    
    def append(self, data):
        self._url += data.get() if type(data) == Url else str(data)
        return self
    
    def __str__(self) -> str:
        return self.get()