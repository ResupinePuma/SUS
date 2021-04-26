from requests import Session

class Network(Session):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headers.update({
            "User-Agent" : "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:87.0) Gecko/20100101 Firefox/87.0"
        })

    def get(self, url: str, **kwargs):
        return super().get(url, **kwargs)

    def post(self, url: str, **kwargs):
        return super().get(url, **kwargs)