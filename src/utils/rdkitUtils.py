from ..FileParser.FileParser import FileParser
from rdkit.Chem import rdchem, PeriodicTable
from rdkit.rdgeom import Point3D

def file_to_rdmol(fobject: FileParser):
    moldict = fobject._read_mol_dict()
    rdmol = rdchem.RWMol(rdchem.Mol())
    conf = rdchem.Conformer()
    # setting atom symbols
    for atom in moldict["atom_symbols"]:
        rdmol.AddAtom(rdchem.Atom(PeriodicTable.GetAtomicNumber(atom)))
    # setting coordinates (if available)
    if not moldict["atom_coords"] is None:
        for i, coord in enumerate(moldict["atom_coords"]):
            conf.SetAtomPosition(i, Point3D(*coord))
    # setting bonds (if available)
    elif not moldict["bondmap"] is None:
        for bond in moldict["bondmap"]:
            rdmol.AddBond(bond[0], bond[1], rdchem.BondType.values[bond[2]])
    else:
        raise RuntimeError("Could not find any coordinates or bond information for the molecule")
    # getting molecule + conformer
    rdmol = rdmol.GetMol()
    rdmol.AddConformer(conf)
    return rdmol
