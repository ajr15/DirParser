from .FileParser import FileParser
from ..Base.Molecule import Molecule
from ..Base.Atom import Atom
import pandas as pd
import numpy as np
from typing import List

class OrcaIn (FileParser):

    """A file parser for ORCA standard input files"""

    def read_scalar_data(self):
        """Reads scalar data from file to a dictionary"""
        raise NotImplementedError

    def read_specie(self):
        """Method to read Specie (Molecule or Structure) from the file"""
        raise NotImplementedError

    def write_file(self, specie: Molecule, kwdict: dict):
        """Method to write the file type, given keywords dictionary and a specie."""
        
        pass
