import numpy as np


class Lattice:

    def __init__(self, vectors: np.array=np.array([])):
        # checking if valid vector sizes inserted
        if not len(vectors.size) == 2 or not vectors.size[0] == 3 or not vectors.size[1] == 3:
            raise ValueError("Invalid lattice vectors! must by a numpy array with size (3, 3)")
        else:
            self.vectors = vectors

    

    @property
    def a(self):
        return np.linalg.norm(self.vectors[0])

    @property
    def b(self):
        return np.linalg.norm(self.vectors[1])

    @property
    def c(self):
        return np.linalg.norm(self.vectors[2])

    def get_primitive_vectors(self):
        """Calculate the primitive (normalized) vectors of the lattice"""
        return self.vectors / np.array([self.a, self.b, self.c])

    def reduce_coordinates(self, cartesian_coords: np.array):
        """Reduce cartesian coordinates to fractional coordinates"""
        return cartesian_coords / np.array([self.a, self.b, self.c])