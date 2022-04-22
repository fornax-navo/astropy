from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename

from numpy.testing import assert_array_equal

import pytest

INDEXING_PATTERNS = [
    None,
    0,
    -1,
    slice(None, None),
    (slice(None, None), slice(None, None)),
    slice(1, 3),
    slice(-5, -2),
    (1, slice(2, 4)),
    (-2, slice(3, 5)),
    (slice(1, 2), 3),
    (slice(2, 3), -1),
    (slice(0, 5), slice(10, 15)),
    (slice(-10, None), slice(-20, None)),
    (0, 1)
]

INDEXING_PATTERNS_3D = [
    (0, 1, 2),
    (-1, -1, -1)
]

# TODO: test indexing with tuples, e.g. (0,1) or ((0,1), (2,3))
# first number in the index is the dimension
# e.g. assert_array_equal(f[1].data[(0,1), (2,3)], f[1].subset[(0,1), (2,3)])


def test_image_subset():
    # test0.fits[1] is a 2D image with shape (40, 40)
    fn = get_pkg_data_filename('data/test0.fits')
    with fits.open(fn) as f:
        for idx in INDEXING_PATTERNS:
            assert_array_equal(f[1].data[idx], f[1].subset[idx])

def test_cube_subset():
    # arange.fits[0] is a 3D array with shape (7, 10, 11)
    fn = get_pkg_data_filename('data/arange.fits')
    with fits.open(fn) as f:
        for idx in INDEXING_PATTERNS + INDEXING_PATTERNS_3D:
            assert_array_equal(f[0].data[idx], f[0].subset[idx])
