from .FileParser import FileParser
from ..Base.Atom import Atom
from ..Base.Molecule import Molecule
from ..Base.Specie import Specie
import re
import numpy as np

class MopacOut (FileParser):
    """A file parser for MOPAC standard output files"""
    extension = "out"

    def read_scalar_data(self):
        """Method to read basic properties from MOPAC output.
        ARGS:
            NONE
        RETURNS:
            (dict) dictionary with properties
                    {
                        "singlet_energy": (float) energy of singlet excited state,
                        "triplet_energy": (float) energy of triplet excited state,
                        "homo_lumo_gap": (float) HOMO-LUMO gap energy,
                        "ionization_energy": (float) ionization energy,
                        "total_energy": (float) total energy of the molecule,
                        "runtime": (float, seconds) total computation time,
                        "finished_normally": (bool) if computation was finished successfully,
                        "converged": (bool) if the computation converged
                    }"""
        outdict = {
                    "singlet_energy": None,
                    "triplet_energy": None,
                    "homo_lumo_gap": None,
                    "ionization_energy": None,
                    "total_energy": None,
                    "runtime": None,
                    "finished_normally": False, 
                    "converged": False
                  }

        with open(self.path, "r") as f:
            ESandETBlock = False
            OxyStateBlock = False

            for line in f.readlines():
                wordsvec = re.split(r" |\t|\n", line)
                wordsvec = list(filter(lambda a: a != '', wordsvec))
                if len(wordsvec) == 0:
                    continue

                if line == "  STATE       ENERGY (EV)        Q.N.  SPIN   SYMMETRY              POLARIZATION\n":
                    ESandETBlock = True
                    continue
                if ESandETBlock and (len(wordsvec) == 6 or len(wordsvec) == 9):
                    if wordsvec[4] == "SINGLET":
                        outdict["singlet_energy"] = float(wordsvec[2])
                        continue
                    elif wordsvec[4] == "TRIPLET":
                        outdict["triplet_energy"] = float(wordsvec[2])
                        continue

                if not outdict["singlet_energy"] == None and not outdict["triplet_energy"] == None and ESandETBlock:
                    ESandETBlock = False
                    continue
                
                if "HERBERTS TEST WAS SATISFIED IN BFGS" in line:
                    outdict["converged"] = True
                if "* JOB ENDED NORMALLY *" in line:
                    outdict["finished_normally"] = True
                if "TOTAL JOB TIME" in line:
                    outdict["runtime"] = float(wordsvec[-2])

                try:
                    if wordsvec[0] + wordsvec[1] == "IONIZATIONPOTENTIAL":
                        outdict["ionization_energy"] = float(wordsvec[3])
                        continue
                    elif wordsvec[0] + wordsvec[1] == "HOMOLUMO":
                        outdict["homo_lumo_gap"] = float(wordsvec[-1])
                        continue
                    elif wordsvec[0] + wordsvec[1] == "TOTALENERGY":
                        outdict["total_energy"] = float(wordsvec[3])
                        continue
                except IndexError:
                    continue
        return outdict


    def read_specie(self):
        """Method to read specie list (atom_symbols key), cartesian coordinates (atom_coords key) and bond information (bondmap key) to a dictionary"""
        outdict = {
                    "atom_symbols": None,
                    "atom_coords": None,
                    "bondmap": None
                  }

        with open(self.path, "r") as f:
            CoordsBlock = False
            for line in f.readlines():
                wordsvec = re.split(r" |\t|\n", line)
                wordsvec = list(filter(lambda a: a != '', wordsvec))
                if len(wordsvec) == 0:
                    continue

                if "".join(wordsvec) == "CARTESIANCOORDINATES":
                    CoordsBlock = True
                    outdict["atom_coords"] = []
                    outdict["atom_symbols"] = []
                    continue

                if CoordsBlock and not len(wordsvec) == 5:
                    CoordsBlock = False
                    continue

                if CoordsBlock and not wordsvec[0] == "NO.":
                    outdict["atom_symbols"].append(wordsvec[1])
                    outdict["atom_coords"].append([float(x) for x in wordsvec[2:]])
                    continue
        # creating Molecule object
        atoms = [Atom(s, np.array(c)) for s, c in zip(outdict["atom_symbols"], outdict["atom_coords"])]
        return Molecule(atoms)

    def read_frequency_dict(self):
        """Method to read frequency data from mopac output file.
        ARGS:
            NONE
        RETURNS:
            (dict) dictionary with frequency information. contains:
                - frequencies (List[float]): list of vibrational frequencies
                - effective_masses (List[float]): list of vibration effective mass
                - force_constants (List[float]): force constant for the vibration"""
        outdict = {
                    "frequencies": None,
                    "effective_masses": None,
                    "force_constants": None
                  }

        with open(self.path, "r") as f:
            VibBlock = False
            for line in f.readlines():
                wordsvec = re.split(r" |\t|\n", line)
                wordsvec = list(filter(lambda a: a != '', wordsvec))
                if len(wordsvec) == 0:
                    continue
                if "DESCRIPTION OF VIBRATIONS" in line:
                    VibBlock = True
                    outdict["frequencies"] = []
                    outdict["effective_masses"] = []
                    outdict["force_constants"] = []
                    continue

                if VibBlock and "FORCE CONSTANT IN CARTESIAN COORDINATES (Millidynes/A)" in line:
                    VibBlock = False
                    continue

                if VibBlock:
                    if wordsvec[0] == "FREQUENCY":
                        outdict["frequencies"].append(float(wordsvec[1]))
                    elif wordsvec[0] + wordsvec[1] == "EFFECTIVEMASS":
                        try:
                            outdict["effective_masses"].append(float(wordsvec[2]))
                        except:
                            continue
                    elif wordsvec[0] + wordsvec[1] == "FORCECONSTANT":
                        outdict["force_constants"].append(float(wordsvec[2]))
                
            return outdict

    def write_file(self, specie: Specie, kwdict: dict):
        return super().write_file()


