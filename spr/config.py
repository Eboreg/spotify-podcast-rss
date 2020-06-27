import configparser
import os


class Config:
    def __init__(self, client_id=None, client_secret=None, market=None):
        self.client_id = client_id
        self.client_secret = client_secret
        self.market = market

    @classmethod
    def from_file(cls, filename):
        config = configparser.ConfigParser()
        config.read(filename)
        assert "spotify" in config, "No `spotify` section in {}".format(filename)
        assert "client_id" in config["spotify"], "No Spotify client ID in {}".format(filename)
        assert "client_secret" in config["spotify"], "No Spotify client secret in {}".format(filename)

        return cls(
            client_id=config["spotify"]["client_id"],
            client_secret=config["spotify"]["client_secret"],
            market=config["spotify"].get("market", None))

    @classmethod
    def load(cls, filename=None):
        if filename is None:
            filename = os.environ.get("SPR_CONFIG", "config.ini")
        return cls.from_file(filename)
