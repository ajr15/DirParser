from abc import ABC, abstractclassmethod
from .Atom import Atom
from typing import List
from copy import copy


class Specie (ABC):
    
    def __init__(self, atoms: List[Atom]=[]):
        self.atoms = [copy(atom) for atom in atoms] # copying list to prevent overriding problems
        for atom in self.atoms:
            atom.parent_specie = self

    @abstractclassmethod
    def save_to_file(self):
        """Method to save the specie to a file"""
        pass

    def get_atom_types(self) -> List[str]:
        """Method to get the atom types in the specie, returns a list with atomic symbols"""
        res = set()
        for atom in self.atoms:
            res.add(atom.symbol)
        return list(res)