from .FileParser import FileParser
from ..base.Molecule import Molecule


class OrcaIn (FileParser):

    """A file parser for ORCA standard input files"""

    extension = "inp"

    def __init__(self, path):
        if not hasattr(self, "extension"):
            raise NotImplementedError("Undefined extension for this file parser. Please define an extension and rerun.")
        if path.endswith(self.extension):
            self.path = path
        else:
            raise ValueError("Illegal file extension for supplied file.")


    def read_scalar_data(self):
        """Reads scalar data from file to a dictionary"""
        raise NotImplementedError

    def read_specie(self):
        """Method to read Specie (Molecule or Structure) from the file"""
        raise NotImplementedError

    @staticmethod
    def _check_kwdict(kwdict: dict) -> None:
        if not "input_text" in kwdict:
            raise ValueError("Must set input_text key with text to put above the coordinate section")
        if not "mult" in kwdict:
            raise ValueError("Must set mult key with multiplicity value of molecule")
        if not "charge" in kwdict:
            raise ValueError("Must set charge key with charge of molecule")

    
    @staticmethod
    def _mol_to_input_text(molecule: Molecule) -> str:
        s = ""
        for atom in molecule.atoms:
            s += "{}\t{:.4f}\t{:.4f}\t{:.4f}\n".format(atom.symbol, *atom.coordinates)
        return s


    def write_file(self, specie: Molecule, kwdict: dict):
        """Method to write the file type, given keywords dictionary and a specie."""
        self._check_kwdict(kwdict)
        with open(self.path, "w") as f:
            # writing input text
            f.write(kwdict["input_text"])
            if not kwdict["input_text"].endswith("\n"):
                f.write("\n")
            # writing molecule
            f.write("* xyz {} {}\n".format(kwdict["charge"], kwdict["mult"]))
            f.write(self._mol_to_input_text(specie))
            f.write("*")