from dataclasses import dataclass

@dataclass
class Bond:

    first_atom_idx: int=0
    second_atom_idx: int=0
    bond_order: int=0
    parent_specie=None