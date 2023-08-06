"""This moduke contains utilities.

.. currentmodule:: marketplace.app.utils
.. moduleauthor:: Pablo de Andres, Pranjali Singh (Fraunhofer IWM)
"""

import re
from functools import wraps


def check_capability_availability(capability):
    """Decorator for checking that a certain app supports a given capability.

    Args:
        capability (str): capability that should be in capabilities
    """

    @wraps(capability)
    def wrapper(instance, *args, **kwargs):
        if capability.__name__ not in instance.capabilities:
            raise NotImplementedError("The app does not support this capability.")
        return capability(instance, *args, **kwargs)

    return wrapper


def camel_to_snake(name):
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()
