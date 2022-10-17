from .FileParser import FileParser
import re
from ..base.Structure import Structure
from ..base.Lattice import Lattice
from ..base.Atom import Atom
import numpy as np

class QeOut (FileParser):

    extension = "out"

    def read_scalar_data(self) -> dict:
        """Reads scalar data from file to a dictionary"""
        res = {}
        with open(self.path, "r") as f:
            for line in f.readlines():
                if "!" in line and 'total energy' in line:
                    # take the last "total energy line"
                    res['total_energy'] = float(re.findall(r'[\d|.|,|-]+', line)[0])
        return res


    def read_specie(self) -> Structure:
        """Method to read Structure from the file"""
        with open(self.path, "r") as f:
            FinalCoordsBlock = False
            CartesianBlock = False
            CellParamsBlock = False
            AtomPosBlock = False
            CoordsAreCartesian = False
            atoms = []
            cell_vectors = []
            for line in f.readlines():
                if FinalCoordsBlock is True:
                    if len(line) > 1 and not 'End' in line:
                        specie = re.findall(r'[A-Za-z]+', line)[0]
                        coords = np.array([float(c) for c in re.findall(r'[\d|.|,|-]+', line)[:3]])
                        atoms.append(Atom(specie, coords))
                    else:
                        FinalCoordsBlock = False
                if 'celldm(1)' in line:
                    param_a = float(re.findall(r'[\d|.|,|-]+', line)[1]) * 0.529177 # correction (for some reason the a parameter is scaled) TODO: FIND OUT WHY
                if CellParamsBlock is True:
                    if len(line) > 1:
                        vec = np.array([float(c) * param_a for c in re.findall(r'[\d|.|,|-]+', line)[1:]])
                        cell_vectors.append(vec)
                    else:
                        CellParamsBlock = False
                if CartesianBlock:
                    if len(line) > 1:
                        if not 'site' in line:
                            vec = [w for w in line.split() if not w == '']
                            atoms.append(Atom(vec[1], np.array([float(c) for c in vec[6:9]])))
                    else:
                        if blank_line_counter > 0:
                            blank_line_counter -= 1
                        if blank_line_counter <= 0:
                            CartesianBlock = False
                if "crystal axes" in line :
                  CellParamsBlock = True
                  cell_vectors = []
                if 'ATOMIC_POSITIONS' in line:
                    FinalCoordsBlock = True
                    CoordsAreCartesian = False
                    atoms = []
                if "Cartesian axes" in line:
                    CartesianBlock = True
                    CoordsAreCartesian = True
                    atoms = []
                    blank_line_counter = 1
            mat = np.array(cell_vectors)
            for atom in atoms:
                atom.coordinates = np.matmul(mat, np.transpose(atom.coordinates))
            lat = Lattice(cell_vectors)
            return Structure(atoms, lat)


    def write_file(self, specie: Structure, kwdict: dict):
        """Method to write the file type, given keywords dictionary and a specie."""
        raise NotImplementedError("Write file method is not implemented for this file")
