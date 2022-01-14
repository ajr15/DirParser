from dataclasses import dataclass
from .Specie import Specie
from .Atom import Atom
from .Bond import Bond
from typing import List, Optional
import numpy as np

class Molecule (Specie):
    """Representation of a molecule.
    ARGS:
        - atoms (List[Atom]): list of atoms in the structure
        - lattice (Lattice): Lattice structure"""

    def __init__(self, atoms: Optional[List[Atom]]=None, bonds: Optional[List[Bond]]=None):
        if bonds is None:
            self.bonds = []
        else:
            self.bonds = bonds
        if atoms is None:
            atoms = []
        for bond in self.bonds:
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

    
    def add_bond(self, bond: Bond):
        bond.parent_specie = self
        self.bonds.append(bond)

    def centralize_coordinates(self):
        """Method to make the center of the molecule at (0, 0, 0)"""
        center = np.mean([a.coordinates for a in self.atoms], axis=0)
        self.move_by_vector(np.negative(center))


    def move_by_vector(self, vector: np.ndarray):
        for atom in self.atoms:
            atom.coordinates = atom.coordinates + vector

    
    def get_neighbors(self, atom_idx: int):
        """Method to get the neighbors of atom.
        ARGS:
            - atom_idx (int): atom index in molecule
        RETURNS
            (List[int]) list of neighbor indicis"""
        neighbors = []
        for bond in self.bonds:
            if atom_idx == bond.first_atom_idx:
                neighbors.append(bond.second_atom_idx)
            elif atom_idx == bond.second_atom_idx:
                neighbors.append(bond.first_atom_idx)
        return neighbors

    
    def join(self, molecule):
        """Method to join two molecules"""
        for atom in molecule.atoms:
            self.atoms.append(atom)
        for bond in molecule.bonds:
            self.add_bond(Bond(bond.first_atom_idx + len(self.atoms) - len(molecule.atoms),
                                bond.second_atom_idx + len(self.atoms) - len(molecule.atoms),
                                bond.bond_order))