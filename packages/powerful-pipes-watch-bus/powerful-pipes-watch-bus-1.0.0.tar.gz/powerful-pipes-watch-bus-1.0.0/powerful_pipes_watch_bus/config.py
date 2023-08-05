from typing import List
from dataclasses import dataclass, field

from argparse import Namespace

@dataclass
class RunningConfig:
    queue_name: str
    bus_connection: List[str]
    debug: bool = False
    banner: bool = False

    @classmethod
    def from_cli(cls, parsed: Namespace):
        return cls(**{k: v for k, v in parsed.__dict__.items() if v is not None})

__all__ = ("RunningConfig", )
