from dataclasses import dataclass
from .Specie import Specie
from .Atom import Atom
from .Bond import Bond
from typing import List

class Molecule (Specie):
    """Representation of a molecule.
    ARGS:
        - atoms (List[Atom]): list of atoms in the structure
        - lattice (Lattice): Lattice structure"""

    def __init__(self, atoms: List[Atom]=[], bonds: List[Bond]=[]):
        self.bonds = bonds
        for bond in bonds:
            bond.parent_specie = self
        super().__init__(atoms)

    
    def save_to_file(self, path):
        if path.endswith('.xyz'):
            with open(path, "w") as f:
                f.write(str(len(self.atoms)) + "\r")
                f.write("GENERATED FROM PYTHON\r")
                for atom in self.atoms:
                    string = " ".join([atom.symbol] + [str(x) for x in atom.coordinates]) + "\r"
                    f.write(string)
        else:
            raise NotImplementedError("Currently there is support only for XYZ files")
