import yaml
from .loader import Loader
from box import Box

class Config:
    """ a Pythonic configuration object """

    def __init__(self, source: str = "config.yml") -> None:
        with open(source, 'r') as f:
            self.config = yaml.load(f, Loader=Loader)

    def __call__(self) -> Box:
        return Box(self.config)
