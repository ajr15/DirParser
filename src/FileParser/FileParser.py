from abc import ABC, abstractclassmethod
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
    def _read_mol_dict(self):
        """Method to read specie list (atom_symbols key), cartesian coordinates (atom_coords key) and bond information (bondmap key) to a dictionary"""
        pass

    def _read_lattice_vectors(self):
        """Method to read lattice vectors (for solid state calculations)"""
        raise NotImplementedError("The method _read_lattice_vectors needs to be implemented for solid-state parsing")

    def save_specie(self, specie_path):
        """Method to save a specie data to standard format (xyz, cif...)"""
        # reading molecule
        moldict = self._read_mol_dict()
        if specie_path.endswith('.xyz'):
            with open(specie_path, "w") as f:
                f.write(str(len(moldict["atom_symbols"])) + "\r")
                f.write("ORCA OUT FILE\r")
                for s, coords in zip(moldict["atom_symbols"], moldict["atom_coords"]):
                    string = " ".join([s] + [str(x) for x in coords]) + "\r"
                    f.write(string)
        else:
            raise NotImplementedError("Currently there is support only for XYZ files")
