from .mops import Mops
from .nops import Nops

from scipy import sparse as sp
import numpy as np
from statistics import mean

from typing import Callable, Any, Iterator, Tuple

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


class Sops(Mops):
    """Sops, Sparse Matrix Operation Class"""

    def __init__(self, mat: sp.spmatrix) -> None:
        """Initialize the class from a scipy sparse matrix.

        Args:
            mat (scipy.sparse.spmatrix): a scipy sparse matrix
        """
        super().__init__(mat)

    def iter(self, group: list = None, axis: int = 0) -> Iterator[Tuple]:
        """an Iterator over groups and an axis

        Args:
            group (list, optional): group variable. Defaults to None.
            axis (int, optional): 0 for rows, 1 for columns. Defaults to 0.

        Yields:
            tuple (str, matrix): of group and the submatrix
        """
        mat = self.matrix.tocsr() if axis == 0 else self.matrix.tocsc()

        if group is None:
            yield (group, self)
        else:
            idx_groups = self.groupby_indices(group)
            for k, v in idx_groups.items():
                if axis == 0:
                    yield (
                        k,
                        Sops(
                            mat[
                                v,
                            ]
                        ),
                    )
                else:
                    yield (k, Sops(mat[:, v]))

    def _apply(self, func: Callable[[list], Any], axis: int = 0) -> np.ndarray:
        """Apply a function over the matrix

        Args:
            func (Callable): function to apply over row or col wise vectors
            axis (int, optional): 0 for rows, 1 for columns. Defaults to 0.

        Returns:
            numpy.ndarray: a dense vector
        """

        if func in [sum, mean, min, max]:
            mat = None
            if func == sum:
                mat = self.matrix.sum(axis=axis)
            elif func == mean:
                mat = self.matrix.mean(axis=axis)
            elif func == min:
                mat = self.matrix.min(axis=axis)
            elif func == max:
                mat = self.matrix.max(axis=axis)

            # flatten
            tmat = mat.getA1()
            return tmat if axis == 0 else tmat.T
        else:
            dense_mat = Nops(self.matrix.toarray())
            return dense_mat._apply(func, axis)
