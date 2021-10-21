from pymatgen.core import Structure as pmtStructure
from pymatgen.core import Lattice as pmtLattice
from pymatgen.core import PeriodicSite as pmtSite
from ..Base.Structure import Structure
from ..Base.Lattice import Lattice
from ..Base.Atom import Atom


def pmt_struct_to_structure(pmt_struct: pmtStructure):
    """Method to convert pymatgen.Structure element to internal Structure element"""
    lat = Lattice(pmt_struct.lattice.matrix)
    atoms = []
    for site in pmt_struct.sites:
        atoms.append(Atom(site.species, site.coords))
    return Structure(atoms, lat)


def structure_to_pmt_structure(structure: Structure):
    """Method to convert internal Structure element to pymatgen Structure element"""
    lat = pmtLattice(structure.lattice)
    sites = []
    for atom in structure.atoms:
        sites.append(pmtSite(
            atom.symbol,
            atom.coordinates,
            lat,
            coords_are_cartesian=True
        ))
    return pmtStructure.from_sites(sites)


def read_structure_from_cif(cif_file: str):
    struct = pmtStructure.from_file(cif_file)
    return pmt_struct_to_structure(struct)