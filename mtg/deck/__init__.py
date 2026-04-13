"""

    mtg.deck
    ~~~~~~~~
    Minimal deck module for MTGGoldfish scraping.

    @author: mazz3rr

"""
from __future__ import annotations

import logging
from enum import Enum

from mtg.utils import ParsingError

_log = logging.getLogger(__name__)


class Archetype(Enum):
    """MTG deck archetype classification."""
    AGGRO = "aggro"
    MIDRANGE = "midrange"
    CONTROL = "control"
    COMBO = "combo"
    TEMPO = "tempo"
    RAMP = "ramp"


class Mode(Enum):
    """Game format mode (Best of 1 or 3)."""
    BO1 = "Bo1"
    BO3 = "Bo3"


class InvalidDeck(ParsingError):
    """Raised on invalid deck."""


class CardNotFound(ParsingError):
    """Raised on card not being found."""
