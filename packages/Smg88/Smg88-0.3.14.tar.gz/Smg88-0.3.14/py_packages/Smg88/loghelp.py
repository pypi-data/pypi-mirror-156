"""This module adds supportive functions and classes for logging to the Smg88 package
Supports Smg88.events, Smg88.coms, Smg88.security

Should Include:
Syntactic sugar for logging
"""

from datetime import datetime
from enum import Enum, auto, unique
import logging
import loghelp
from typing import Any
from typehelp import *


from . import errors


class Serializer(object, metaclass=type):
    """This class is used to define a protocol for serialization

    """

    def si_str(thing: Any) -> str:
        """Serializes anything into a good, proper format :)
        """
        return str(thing)

    def T_Serializable(thing: Any, /, *, istype: bool = False) -> bool:
        """Checks weather the type of some thing is seralizable

        Args:
            thing (Any): Thing to check serializability
            istype (bool): Weather to call 'type' on 'thing' or to treat 'thing' as a type already

        Returns:
            bool: True if serializable, False if not
        """
        if istype:
            return type(thing) is str
        else:
            return thing is str


def s_jsonify():
    ...


class EnumParent(Enum):
    def _generate_next_value_(name, start, count, last_values):
        return f"{name}"


def now():
    return datetime.now().strftime("%d/%m/%Y %H:%M:%S")


def callbacknamed(
    name: o_str = ...
):
    if name is ...:
        # TODO add warning for using decorator without given name
        errors.InappropriateRequest(
            "Name not given to callbacknamed decorator constructor")

    def __decoratorfunction(
        func: o_Callable = ...
    ):
        if func is ...:
            # TODO add warning for using func decorator without a given function ??
            raise errors.InappropriateRequest(
                "WTF? Decorator used without given function?")
        func.__name__ = name  # type: ignore
        return func
    return __decoratorfunction
