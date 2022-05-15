from .FileParser import FileParser
from ..utils.openbabel import obmol_to_mol_dict, ob_read_file_to_mol_dict
from ..base.Molecule import Molecule
import openbabel as ob
import subprocess
import os
from typing import List

class MopacIn:
    
    """A file parser for MOPAC standard input files"""
    extension = "mop"

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
        if not "top_kwds" in kwdict.keys():
            raise ValueError("Keywords dictionary must contain top_kwds entry for top keywords, value is a list of strings")
        if not "bottom_kwds" in kwdict.keys():
            raise ValueError("Keywords dictionary must contain bottom_kwds entry for bottom keywords, value is a list of strings")

    def write_file(self, molecule: Molecule, kwdict: dict):
        """internal write method. takes molecule dict (atom_symbols, atom_coords, bondmap) and kwdict (top_kwds, bottom_kwds)"""
        self._check_kwdict(kwdict)
        with open(self.path, "w") as f:
            # writing top part
            if not kwdict['top_kwds'] is None:
                top_string = ""
                for word in kwdict['top_kwds']:
                    top_string += " " + word
                top_string += "\n"
                f.write(top_string)
                f.write("title\n")
                f.write("\n")

            # writing coords and atoms
            for atom in molecule.atoms:
                s = atom.symbol
                for c in atom.coordinates:
                    s += " " + str(round(c, 4)) + " 1"
                s += "\n"
                f.write(s)

            # writing bottom part
            if not kwdict['bottom_kwds'] is None:
                bottom_string = ""
                for word in kwdict['bottom_kwds']:
                    bottom_string += " " + word
                f.write("\n")
                f.write(bottom_string)
