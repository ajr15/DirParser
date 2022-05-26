from .FileParser import FileParser
from ..base.Structure import Structure
from ..utils.pymatgen import structure_to_pmt_structure
from pymatgen.core.periodic_table import Element
from pymatgen.io.lammps.data import LammpsData
import os

class LammpsIn (FileParser):
    
    """A file parser for LAMMPS standard input files"""
    extension = ""

    def __init__(self, path):
        if not hasattr(self, "extension"):
            raise NotImplementedError("Undefined extension for this file parser. Please define an extension and rerun.")
        if path.endswith(self.extension):
            self.path = path
        else:
            raise ValueError("Illegal file extension for supplied file.")

    def read_scalar_data(self):
        """Reads scalar data from file to a dictionary"""
        raise NotImplementedError("read_scalar_data is not implemented feature for MOPAC input files")

    def read_specie(self):
        """Method to read specie list (atom_symbols key), cartesian coordinates (atom_coords key) and bond information (bondmap key) to a dictionary"""
        raise NotImplementedError("read_specie is not implemented feature for MOPAC input files")

    def _check_kwdict(self, kwdict: dict):
        pass

    @staticmethod
    def write_data_file(struct: Structure, data_file_path: str):
        """Method to make a LAMMPS data file for structure description"""
        # using pymatgen's implementation for LAMMPS data files
        # writing it ourselves is a bit envolving...
        pmt = structure_to_pmt_structure(struct)
        lmp_data = LammpsData.from_structure(pmt)
        #lmp_data.write_file(data_file_path)
        # building atom type dictionary
        atom_type_dict = {}
        for atom in struct.atoms:
            if not atom.symbol in atom_type_dict:
                atom_type_dict[atom.symbol] = len(atom_type_dict)
        # writing file
        with open(data_file_path, "w") as f:
            # must start with description line
            f.write("DATA FOR INPUT STRUCTURE\n")
            # mandatory empty line
            f.write("\n")
            # writing number of atoms
            f.write("{} atoms\n".format(len(struct.atoms)))   
            # extra blank line
            f.write("\n")
            # writing number of atom types
            f.write("{} atom types\n".format(len(atom_type_dict)))
			# defining crystal with pymatgen
            f.write("\n" + lmp_data.box.get_string(6) + "\n\n")
            # writing atom type masses
            f.write("Masses\n\n")
            for k, v in atom_type_dict.items():
                f.write("{} {}\n".format(v + 1, Element(k).atomic_mass))
            # madatory empty line
            f.write("\n")
            # writing the structure
            f.write("Atoms\n\n")
            for i, atom in enumerate(struct.atoms):
                f.write("{}\t{}\t{}\t{}\t{}\n".format(i + 1, atom_type_dict[atom.symbol] + 1, *atom.coordinates))
            f.write("\n")
			
    def write_file(self, struct: Structure, kwdict: dict):
        """Method to write the LAMMPS input file. given a structure and a keywords dictionary"""
        # setting defaults for top kwargs
        default_top_kwargs = {"units": "metal", "atom_style": "atomic"}
        for k in default_top_kwargs:
            if k in kwdict:
                default_top_kwargs[k] = kwdict[k]
        # writing data file
        data_file_path = self.path + ".data"
        self.write_data_file(struct, data_file_path)
        # writing input file
        with open(self.path, "w") as f:
            # writing init keywords from default dictionary
            for k, v in default_top_kwargs.items():
                f.write("{} {}\n".format(k, v))
            f.write("box tilt large\n")
            # writing lattice 
            #vector_sizes = list(struct.lattice.vectors[0]) + list(struct.lattice.vectors[1]) + list(struct.lattice.vectors[2])
            #f.write("""lattice custom 1 a1 {} {} {} a2 {} {} {} a3 {} {} {} basis 0.0 0.0 0.0\n""".format(*vector_sizes))
            # reading structure from file
            f.write("read_data {}\n".format(os.path.abspath(data_file_path)))
            # writing rest of the input file
            f.write(kwdict["input_string"])
