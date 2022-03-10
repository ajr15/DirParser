import os
import pandas as pd

class DirParser:
    """General purpose class to handel files in directory"""

    def __init__(self, file_type):
        self.file_parser = file_type

    def apply_function_to_directory(self, f: callable, path, *args, **kwargs):
        """Method to apply a function (f(path, fname, *args, **kwargs)) on the directory"""
        if not os.path.isdir(path):
            raise ValueError("{} is not a directory. Must provide a dicrectory".format(path))
        outs = []
        for dir, subdir, fnames in os.walk(path):
            for fname in fnames:
                if fname.endswith(self.file_parser.extension):
                    outs.append(f(self.file_parser, os.path.join(dir, subdir), fname, *args, **kwargs))
        return outs

    def read_data(self, path, *args, **kwargs):
        """Method to read all files in the directory"""
        if not os.path.isdir(path):
            raise ValueError("{} is not a directory. Must provide a dicrectory".format(path))
        self.df = pd.DataFrame()
        for dir, subdirs, fnames in os.walk(path):
            for fname in fnames:
                if fname.endswith(self.file_parser.extension):
                    f = self.file_parser(os.path.join(dir, fname))
                    d = f.read_scalar_data(*args, **kwargs)
                    d.update({"dir": dir, "name": os.path.splitext(fname)[0]})
                    self.df = self.df.append(d, ignore_index=True)
        return self.df

    def save_species(self, path, ext, *args, **kwargs):
        """Save all species in files in \'molecule_files\' directory in the path. Using the save_species method in the file parser"""
        if not os.path.isdir(path):
            raise ValueError("{} is not a directory. Must provide a dicrectory".format(path))
        # making directory for molecules
        mol_dir = os.path.join(path, 'molecule_files')
        if not os.path.isdir(mol_dir):
            os.mkdir(mol_dir)
        for dir, subdir, fnames in os.walk(path):
            for fname in fnames:
                if fname.endswith(self.file_parser.extension):
                    f = self.file_parser(os.path.join(dir, fname))
                    mol = f.save_specie(os.path.join(mol_dir, os.path.splitext(fname)[0] + "." + ext), *args, **kwargs)

    def to_csv(self, path):
        """Write data to csv file"""
        self.df.to_csv(path, index=False)