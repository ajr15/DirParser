import openbabel as ob
from ..Base.Molecule import Molecule
from ..Base.Atom import Atom
from ..Base.Bond import Bond

def ob_read_file_to_molecule(filename):    
    """Method to use openbabel for reading molecule files into standard molecule dictionary (atom_symbols, atom_coords, bondmap)"""
    obmol = ob.OBMol(); conv = ob.OBConversion()
    conv.ReadFile(obmol, filename)
    return obmol_to_molecule(obmol)

def obmol_to_molecule(obmol: ob.OBMol):
    atoms = []
    for atom in ob.OBMolAtomIter(obmol):
        element = ob.OBElementTable().GetSymbol(atom.GetAtomicNum())
        coord = [atom.GetX(), atom.GetY(), atom.GetZ()]
        atoms.append(Atom(element,coord))
    mol = Molecule(atoms)
    for bond in ob.OBMolBondIter(obmol):
        bond = Bond(bond.GetBeginAtomIdx() - 1, bond.GetEndAtomIdx() - 1, bond.GetBO())
        mol.add_bond(bond)
    return mol

def molecule_to_obmol(molecule: Molecule):
    obmol = ob.OBMol()
    for atom in molecule.atoms:
        obatom = ob.OBAtom()
        obatom.SetAtomicNum(ob.OBElementTable().GetAtomicNum(atom.symbol))
        if not len(atom.coordinates) == 0:
            coord_vec = ob.vector3(*atom.coordinates)
            obatom.SetVector(coord_vec)
        obmol.InsertAtom(obatom)
    for bond in molecule.bonds:
        obmol.AddBond(bond.first_atom_idx + 1, bond.second_atom_idx + 1, bond.bond_order)
    return obmol