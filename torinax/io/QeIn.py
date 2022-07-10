from .FileParser import FileParser
from ..base.Structure import Structure
from ..utils.pymatgen import structure_to_pmt_structure
from pymatgen.core import Element
from copy import deepcopy
import re

def gen_prefix():
    with open('/home/shaharpit/utils/job.count', "r") as f:
        prefix = int(f.read())
    with open('/home/shaharpit/utils/job.count', "w") as f:
        f.write(str(prefix + 1))
    return prefix

class QeIn (FileParser):

    """Parser for Quantum ESPRESSO input files"""

    extension = "in"

    def __init__(self, path):
        if not hasattr(self, "extension"):
            raise NotImplementedError("Undefined extension for this file parser. Please define an extension and rerun.")
        if not path.endswith(self.extension):
            raise ValueError("Illegal file extension for supplied file.")
        self.path = path

    def read_scalar_data(self):
        """Reads scalar data from file to a dictionary"""
        raise NotImplementedError()

    def read_specie(self):
        """Method to read Specie (Molecule or Structure) from the file"""
        raise NotImplementedError()

    @staticmethod
    def _correct_keywords_dict(struct: Structure, d: dict) -> dict:
        '''method to autocorrect and check input keywords dict. Returns corrected dict.'''
        Dict = deepcopy(d)
        if not 'CONTROL' in Dict.keys():
            Dict['CONTROL'] = dict()
        if not 'prefix' in Dict['CONTROL'].keys():
            Dict['CONTROL']['prefix'] = gen_prefix()
        if not 'ELECTRONS' in Dict.keys():
            Dict['ELECTRONS'] = dict()
        if not 'SYSTEM' in Dict.keys():
            Dict['SYSTEM'] = dict()
        if not 'ibrav' in Dict['SYSTEM'].keys():
            Dict['SYSTEM']['ibrav'] = 0
            Dict['CELL_PARAMETERS'] = struct.lattice.matrix
        else:
            Dict['CELL_PARAMETERS'] = []
        Dict['SYSTEM']['nat'] = len(struct.species)
        Dict['SYSTEM']['ntyp'] = len(struct.types_of_specie)
        if not 'ATOMIC_SPECIES' in Dict.keys():
            raise ValueError('keywords_dict must contain an \'ATOMIC_SPECIES\' entry as a dict with species (keys) and potentials (values)')
        if not 'IONS' in Dict.keys():
            Dict['IONS'] = dict()
        if not 'CELL' in Dict.keys():
            Dict['CELL'] = dict()
        if not 'K_POINTS' in Dict.keys():
            raise ValueError('keywords_dict must contain an \'K_POINTS\' entry as a dict with \'type\' and \'vec\' keys')
        return Dict

    def write_file(self, struct: Structure, keywords: dict):
        '''method to generate input for QE calculation'''
        # converting to pymatgen structure - to fit with legacy code
        struct = structure_to_pmt_structure(struct)
        # TODO: add particular explanation on keywords_dict
        keywords_dict = self._correct_keywords_dict(struct, keywords)
        with open(self.path, "w") as f:
            for key in ['CONTROL', 'SYSTEM', 'ELECTRONS', 'IONS', 'CELL']:
                f.write("&" + key + "\n")
                for k, v in keywords_dict[key].items():
                    if type(v) is str:
                        s = "\t" + k + "=\'" + v + '\',\n'
                    elif type(v) is bool:
                        if v:
                            s = "\t" + k + "=.TRUE,\n"
                        else:
                            s = "\t" + k + "=.FALSE,\n"
                    else:
                        s = "\t" + k + "=" + str(v) + ',\n'
                    f.write(s)
                f.write("/\n\n")
            f.write("ATOMIC_SPECIES\n")
            for key, value in keywords_dict["ATOMIC_SPECIES"].items():
                mass = Element(re.findall(r'[A-Za-z]+', key)[0]).atomic_mass.real
                f.write(key + " " + str(mass) + " " + value + "\n")
            f.write("\nATOMIC_POSITIONS crystal\n")
            strs = []
            for site in struct.sites:
                strs.append(site.specie.symbol + " " + str(round(site.a, 4)) + " " + str(round(site.b, 4)) + " " + str(round(site.c, 4)))
            if 'ATOMIC_POSITIONS' in keywords_dict:
                for idx, vec in enumerate(keywords_dict['ATOMIC_POSITIONS']):
                    for v in vec:
                        strs[idx] = strs[idx] + " " + str(int(v))
            for string in strs:
                f.write(string + "\n")
            f.write(f"\nK_POINTS {keywords_dict['K_POINTS']['type']}\n")
            s = ""
            for v in keywords_dict['K_POINTS']['vec']:
                s = s + str(v) + " "
            f.write("\t" + s + "\n")
            if not keywords_dict['CELL_PARAMETERS'] == []:
                f.write("\nCELL_PARAMETERS {angstrom}")
            for vec in keywords_dict['CELL_PARAMETERS']:
                s = ""
                for v in vec:
                    s = s + str(round(v, 4)) + " "
                f.write("\n\t" + s)

