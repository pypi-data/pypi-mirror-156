# coding: utf-8
from typing import Any
from typing import Dict
from typing import Tuple
from typing import Type


class SingletonMeta(type):

    """Метакласс для классов-одиночек.

    Потомки класса с данным метаклассом также будут одиночками. Инициализация
    классов-одиночек (вызов метода ``__init__``) будет выполняться один раз
    при создании.

    .. code-block:: python

       class SingleClass(object):
           __metaclass__ = SingletonMeta
    """

    def __init__(cls, name: str, bases: Tuple[Type], attrs: Dict[str, Any]):
        super(SingletonMeta, cls).__init__(name, bases, attrs)
        cls.instance = None

    def __call__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__call__(*args, **kwargs)

        return cls.instance
