from dataclasses import dataclass
from .Specie import Specie
from .Atom import Atom
from .Lattice import Lattice
from typing import List

class Structure (Specie):
    """Representation of structure in 3D lattice.
    ARGS:
        - atoms (List[Atom]): list of atoms in the structure
        - lattice (Lattice): Lattice structure"""

    
    def __init__(self, atoms: List[Atom]=[], lattice: Lattice=Lattice()):
        self.lattice = lattice
        super().__init__(atoms)

    
    def save_to_file(self):
        raise NotImplementedError()
    
