from abc import ABC, abstractclassmethod
from ..Base.Specie import Specie
import os

class FileParser (ABC):

    """Abstract file parser"""

    def __init__(self, path):
        if not hasattr(self, "extension"):
            raise NotImplementedError("Undefined extension for this file parser. Please define an extension and rerun.")
        if path.endswith(self.extension):
            if os.path.isfile(path):
                self.path = path
            else:
                raise FileNotFoundError("Supplied path {} doesn't exist".format(path))
        else:
            raise ValueError("Illegal file extension for supplied file.")

    @abstractclassmethod
    def read_scalar_data(self):
        """Reads scalar data from file to a dictionary"""
        pass

    @abstractclassmethod
    def read_specie(self):
        """Method to read Specie (Molecule or Structure) from the file"""
        pass

    @abstractclassmethod
    def write_file(self, specie: Specie, kwdict: dict):
        """Method to write the file type, given keywords dictionary and a specie."""
        raise NotImplementedError("Write file method is not implemented for this structure")

    def save_specie(self, specie_path):
        """Method to save a specie data to standard format (xyz, cif...)"""
        # reading molecule
        specie = self.read_specie()
        specie.save_to_file(specie_path)
