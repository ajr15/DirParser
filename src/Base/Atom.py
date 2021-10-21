from dataclasses import dataclass
from typing import List
from .Specie import Specie
import numpy as np

@dataclass
class Atom:

    symbol: str = ""
    coordinates: np.array = np.array()
    parent_specie: Specie = Specie()
