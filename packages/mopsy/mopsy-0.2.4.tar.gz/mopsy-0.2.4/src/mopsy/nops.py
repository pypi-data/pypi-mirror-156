from typing import Any, Iterator, Tuple, Type
from .mops import Mops

import numpy as np

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


class Nops(Mops):
    """Internal representation for numpy arrays"""

    def __init__(self, mat: np.ndarray, non_zero: bool = False) -> None:
        """Intialize with a numpy matrix

        Args:
            mat (numpy.ndarray): numpy matrix
            non_zero (bool): filter zero values ?
        """
        super().__init__(mat, non_zero=non_zero)

    def iter(self, group=None, axis=0) -> Iterator[Tuple]:
        """an Iterator over groups and an axis

        Args:
            group (list, optional): group variable. Defaults to None.
            axis (int, optional): 0 for rows, 1 for columns. Defaults to 0.

        Yields:
            tuple (str, Nops): of group and the submatrix
        """
        mat = self.matrix

        if group is None:
            yield (group, self)
        else:
            idx_groups = self.groupby_indices(group)
            for k, v in idx_groups.items():
                if axis == 0:
                    yield (
                        k,
                        Nops(
                            mat[
                                v,
                            ],
                            self.non_zero,
                        ),
                    )
                else:
                    yield (k, Nops(mat[:, v], self.non_zero))
