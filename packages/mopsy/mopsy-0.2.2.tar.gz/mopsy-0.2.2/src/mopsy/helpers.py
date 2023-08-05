from statistics import mean, median
from .utils import get_matrix_type

from typing import List, Union, Callable, Any
import numpy
import scipy

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"


def colsum(
    mat: Union[numpy.ndarray, scipy.sparse.spmatrix], group: list = None
) -> numpy.ndarray:
    """apply colsum

    Args:
        mat (Union[numpy.ndarray, scipy.sparse.spmatrix]): matrix
        group (list, optional): group variable. Defaults to None.

    Returns:
        numpy.ndarray: matrix
    """
    return apply(sum, mat, group=group, axis=1)


def rowsum(
    mat: Union[numpy.ndarray, scipy.sparse.spmatrix], group: list = None
) -> numpy.ndarray:
    """apply rowsum

    Args:
        mat (Union[numpy.ndarray, scipy.sparse.spmatrix]): matrix
        group (list, optional): group variable. Defaults to None.

    Returns:
        numpy.ndarray: matrix
    """
    return apply(sum, mat, group=group, axis=0)


def colmean(
    mat: Union[numpy.ndarray, scipy.sparse.spmatrix], group: list = None
) -> numpy.ndarray:
    """apply colmean

    Args:
        mat (Union[numpy.ndarray, scipy.sparse.spmatrix]): matrix
        group (list, optional): group variable. Defaults to None.

    Returns:
        numpy.ndarray: matrix
    """
    return apply(mean, mat, group=group, axis=1)


def rowmean(
    mat: Union[numpy.ndarray, scipy.sparse.spmatrix], group: list = None
) -> numpy.ndarray:
    """apply rowmean

    Args:
        mat (Union[numpy.ndarray, scipy.sparse.spmatrix]): matrix
        group (list, optional): group variable. Defaults to None.

    Returns:
        numpy.ndarray: matrix
    """
    return apply(mean, mat, group=group, axis=0)


def colmedian(
    mat: Union[numpy.ndarray, scipy.sparse.spmatrix], group: list = None
) -> numpy.ndarray:
    """apply colmedian

    Args:
        mat (Union[numpy.ndarray, scipy.sparse.spmatrix]): matrix
        group (list, optional): group variable. Defaults to None.

    Returns:
        numpy.ndarray: matrix
    """
    return apply(median, mat, group=group, axis=1)


def rowmedian(
    mat: Union[numpy.ndarray, scipy.sparse.spmatrix], group: list = None
) -> numpy.ndarray:
    """apply rowmedian

    Args:
        mat (Union[numpy.ndarray, scipy.sparse.spmatrix]): matrix
        group (list, optional): group variable. Defaults to None.

    Returns:
        numpy.ndarray: matrix
    """
    return apply(median, mat, group=group, axis=0)


def apply(
    func: Callable[[list], Any],
    mat: Union[numpy.ndarray, scipy.sparse.spmatrix],
    axis: int,
    group: list = None,
):
    """a generic apply function

    Args:
        func (Callable): function to be called.
        mat (Union[numpy.ndarray, scipy.sparse.spmatrix]): matrix
        group (list, optional): group variable. Defaults to None.
        axis (int): 0 for rows, 1 for columns.

    Returns:
        numpy.ndarray: matrix
    """
    tmat = get_matrix_type(mat)
    return tmat.apply(func, group=group, axis=axis)


def multi_apply(
    funcs: List[Callable[[list], Any]],
    mat: Union[numpy.ndarray, scipy.sparse.spmatrix],
    axis: int,
    group: list = None,
):
    """Apply multiple functions, the first axis
        of the ndarray specifies the results of the inputs functions in
        the same order

    Args:
        funcs (List[Callable[[list], Any]]): functions to be called.
        mat (Union[numpy.ndarray, scipy.sparse.spmatrix]): matrix
        group (list, optional): group variable. Defaults to None.
        axis (int): 0 for rows, 1 for columns.

    Returns:
        numpy.ndarray: matrix
    """
    tmat = get_matrix_type(mat)
    return tmat.multi_apply(funcs, group=group, axis=axis)
