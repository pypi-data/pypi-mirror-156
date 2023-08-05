from abc import ABC, abstractmethod

from ..types import Device


class BaseAdapter(ABC):
    """
    Abstract class for dral generator adapters

    Every adapter should inherit from this class and implement convert method.
    It should return data structure used by dral generator:
    {
      "device": {
        "name": "",
        "description": ""
        "peripherals": [
          {
            "name": "",
            "description": "",
            "address": "",
            "registers": [
              {
                "name": "",
                "description": "",
                "offset": "",
                "size": "",
                "access": "",
                "resetValue": "",
                "fields": [
                  {
                    "name": "",
                    "description": "",
                    "position": "",
                    "mask": "",
                    "width": ""
                  }
                ]
              }
            ]
          }
        ]
      }
    }

    ...

    Methods
    -------
    convert()
        Returns data structure used by d-ral generator
    """
    def __init__(self) -> None:
        pass


    @abstractmethod
    def convert(self) -> Device:
        pass
