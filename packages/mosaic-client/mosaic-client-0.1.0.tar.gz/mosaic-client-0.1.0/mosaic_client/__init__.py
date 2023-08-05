"""
This module contains functions for working with the SOAP interfaces provided by E-PIX and gPAS - services
provided as part of the MOSAIC suite by the THS Greifswald.
"""

__version__ = '0.1.0'

from . import epix, gpas
from .model import (
    IdentifierDomain,
    Identifier,
    Contact,
    FullContact,
    Identity,
    Source,
    FullIdentity,
    Person,
    ResponseEntry,
    BatchResponseEntry,
    BatchRequestConfig,
)
