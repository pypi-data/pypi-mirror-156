from __future__ import annotations

import abc

from typing import Iterator


class BusInterface(metaclass=abc.ABCMeta):

    @classmethod
    @abc.abstractmethod
    def open(cls, connection_string: str) -> BusInterface:
        ...

    @abc.abstractmethod
    def read_json_messages(self, bus_name: str) -> Iterator[dict]:
        ...


__all__ = ("BusInterface", )
