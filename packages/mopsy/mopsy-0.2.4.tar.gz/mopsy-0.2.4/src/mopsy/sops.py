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

    def __init__(self, mat: sp.spmatrix, non_zero: bool = False) -> None:
        """Initialize the class from a scipy sparse matrix.

        Args:
            mat (scipy.sparse.spmatrix): a scipy sparse matrix
            non_zero (bool): filter zero values ?
        """
        super().__init__(mat, non_zero=non_zero)

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
                            ],
                            self.non_zero,
                        ),
                    )
                else:
                    yield (k, Sops(mat[:, v], self.non_zero))

    def _apply(self, func: Callable[[list], Any], axis: int = 0) -> np.ndarray:
        """Apply a function over the matrix

        Args:
            func (Callable): function to apply over row or col wise vectors
            axis (int, optional): 0 for rows, 1 for columns. Defaults to 0.

        Returns:
            numpy.ndarray: a dense vector
        """
        mat = self.matrix.tocsc() if axis == 0 else self.matrix.tocsr()
        if self.non_zero:
            # reduction along an axis
            fmat = np.zeros(mat.shape[1] if axis == 0 else mat.shape[0])
            for i in range(len(mat.indptr) - 1):
                start_idx = mat.indptr[i]
                end_idx = mat.indptr[i + 1]
                if start_idx == end_idx:
                    fmat[i] = 0
                else:
                    mslice = mat.data[slice(start_idx, end_idx)]
                    fmat[i] = 0 if len(mslice) == 0 else func(mslice)

            return fmat if axis == 0 else fmat.T
        else:
            if func in [sum, mean, min, max]:
                if func == sum:
                    mat = mat.sum(axis=axis)
                elif func == mean:
                    mat = mat.mean(axis=axis)
                elif func == min:
                    mat = mat.min(axis=axis).todense()
                elif func == max:
                    mat = mat.max(axis=axis).todense()

                # flatten
                tmat = mat.getA1()
                return tmat if axis == 0 else tmat.T
            else:
                dense_mat = Nops(self.matrix.toarray(), self.non_zero)
                return dense_mat._apply(func, axis)
