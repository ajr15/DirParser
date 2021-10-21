import openbabel as ob

def ob_read_file_to_mol_dict(filename):    
    """Method to use openbabel for reading molecule files into standard molecule dictionary (atom_symbols, atom_coords, bondmap)"""
    mol = ob.OBMol(); conv = ob.OBConversion()
    conv.ReadFile(mol, filename)

    atoms = []; coords = []
    for atom in ob.OBMolAtomIter(mol):
        element = ob.OBElementTable().GetSymbol(atom.GetAtomicNum())
        coord = [atom.GetX(), atom.GetY(), atom.GetZ()]
        atoms.append(element); coords.append(coord)

    bondmap = []
    for bond in ob.OBMolBondIter(mol):
        vec = [bond.GetBeginAtomIdx() - 1, bond.GetEndAtomIdx() - 1, bond.GetBO()]
        bondmap.append(vec)

    return {"atom_symbols": atoms,
            "atom_coords":coords,
            "bondmap": bondmap}

def obmol_to_mol_dict(obmol):
    atoms = []; coords = []
    for atom in ob.OBMolAtomIter(obmol):
        element = ob.OBElementTable().GetSymbol(atom.GetAtomicNum())
        coord = [atom.GetX(), atom.GetY(), atom.GetZ()]
        atoms.append(element); coords.append(coord)

    bondmap = []
    for bond in ob.OBMolBondIter(obmol):
        vec = [bond.GetBeginAtomIdx() - 1, bond.GetEndAtomIdx() - 1, bond.GetBO()]
        bondmap.append(vec)

    return {"atom_symbols": atoms,
            "atom_coords":coords,
            "bondmap": bondmap}
