from dataclasses import dataclass
from typing import Optional
import numpy as np

@dataclass
class Atom:

    symbol: str = ""
    coordinates: Optional[np.ndarray] = None
    parent_specie = None
