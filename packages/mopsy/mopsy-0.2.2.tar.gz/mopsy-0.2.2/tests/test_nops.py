import numpy as np
from mopsy.nops import Nops
from scipy.sparse import eye

__author__ = "jkanche"
__copyright__ = "jkanche"
__license__ = "MIT"

mat = eye(5).toarray()
group = ["col1", "col2", "col1", "col2", "col2"]


def test_init():
    tmat = Nops(mat)
    assert tmat is not None


def test_group_iter_rows():
    tmat = Nops(mat)

    groups = tmat.iter(group, axis=0)
    assert sum(1 for _ in groups) == 2


def test_group_iter_cols():
    tmat = Nops(mat)

    groups = tmat.iter(group, axis=1)
    assert sum(1 for _ in groups) == 2


def test_group_apply_rows():
    tmat = Nops(mat)
    rmat = tmat.apply(sum, group=group, axis=0)
    assert rmat.shape[0] == 2
    assert rmat.shape[1] == 5
    assert rmat[0, :].flatten().tolist() == [1.0, 0.0, 1.0, 0.0, 0.0]
    assert rmat[1, :].flatten().tolist() == [0.0, 1.0, 0.0, 1.0, 1.0]


def test_group_apply_cols():
    tmat = Nops(mat)
    rmat = tmat.apply(sum, group=group, axis=1)
    assert rmat.shape[0] == 5
    assert rmat.shape[1] == 2
    assert rmat[:, 0].flatten().tolist() == [1.0, 0.0, 1.0, 0.0, 0.0]
    assert rmat[:, 1].flatten().tolist() == [0.0, 1.0, 0.0, 1.0, 1.0]


def test_group_apply_row_None():
    tmat = Nops(mat)
    rmat = tmat.apply(sum, group=None, axis=0)
    assert rmat is not None
    assert rmat.shape[0] == 1
    assert rmat.shape[1] == 5
    assert rmat[
        :,
    ].flatten().tolist() == [1.0, 1.0, 1.0, 1.0, 1.0]


def test_group_apply_col_None():
    tmat = Nops(mat)
    rmat = tmat.apply(sum, group=None, axis=1)
    assert rmat is not None
    assert rmat.shape[0] == 5
    assert rmat.shape[1] == 1
    assert rmat[
        :,
    ].flatten().tolist() == [1.0, 1.0, 1.0, 1.0, 1.0]


def test_multi_apply_rows_None():
    tmat = Nops(mat)
    rmat = tmat.multi_apply([np.sum, np.mean], axis=0)
    print(rmat.shape)
    assert rmat is not None
    assert rmat.shape[0] == 2
    assert rmat.shape[1] == 1
    assert rmat.shape[2] == 5
    assert rmat[:, 0].tolist() == [
        [1.0, 1.0, 1.0, 1.0, 1.0],
        [0.2, 0.2, 0.2, 0.2, 0.2],
    ]


def test_multi_apply_cols_None():
    tmat = Nops(mat)
    rmat = tmat.multi_apply([np.sum, np.mean], axis=1)
    print(rmat.shape)
    assert rmat is not None
    assert rmat.shape[0] == 2
    assert rmat.shape[1] == 5
    assert rmat.shape[2] == 1
    assert rmat[:, 0].tolist() == [[1.0], [0.2]]


def test_multi_apply_rows():
    tmat = Nops(mat)
    rmat = tmat.multi_apply([np.sum, np.mean], group=group, axis=0)
    print(rmat.shape)
    print(rmat)
    assert rmat is not None
    assert rmat.shape[0] == 2
    assert rmat.shape[1] == 2
    assert rmat.shape[2] == 5
    assert rmat[:, 0].tolist() == [
        [1.0, 0.0, 1.0, 0.0, 0.0],
        [0.5, 0.0, 0.5, 0.0, 0.0],
    ]


def test_multi_apply_cols():
    tmat = Nops(mat)
    rmat = tmat.multi_apply([np.sum, np.mean], group=group, axis=1)
    print(rmat.shape)
    print(rmat)
    assert rmat is not None
    assert rmat.shape[0] == 2
    assert rmat.shape[1] == 5
    assert rmat.shape[2] == 2
    assert rmat[:, 0].tolist() == [[1.0, 0.0], [0.5, 0.0]]
