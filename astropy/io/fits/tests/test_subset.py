"""
TODO
====

* Add test for treatment of optional fsspec dependency.

* Add indexing tests with specified dimensions, e.g.:
    (0,1) or ((0,1), (2,3))
  first number in each tuple is the dimension.

* Add indexing tests with newaxis at the front, e.g.:
    (None, None, 0),
    (None, None, slice(None)),

* Test with AstroPy's ImageCutout tool?
"""
from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename

import numpy as np
from numpy.testing import assert_array_equal, assert_allclose
import pytest


INDEXING_PATTERNS = [
    0,
    -1,
    None,
    ...,
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
    (0, 1),
    (2, ...),
    (..., 3),
    (..., slice(1, 2)),
    (0, None, None),
    (slice(None), None, None),
]

INDEXING_PATTERNS_3D = [
    (0, 1, 2),
    (-1, -1, -1),
    (..., 1, 2),
    (0, ..., 2),
    (1, 2, ...),
    (1, None, 3)
]


def test_subset_from_image():
    """Verifies the correctness of indexing an image via `.subset`."""
    # test0.fits[1] is a 2D image with shape (40, 40)
    fn = get_pkg_data_filename('data/test0.fits')
    with fits.open(fn) as f:
        for idx in INDEXING_PATTERNS:
            assert_array_equal(f[1].data[idx], f[1].subset[idx])


def test_subset_from_cube():
    """Verifies the correctness of indexing an cube via `.subset`."""
    # arange.fits[0] is a 3D array with shape (7, 10, 11)
    fn = get_pkg_data_filename('data/arange.fits')
    with fits.open(fn) as f:
        for idx in INDEXING_PATTERNS + INDEXING_PATTERNS_3D:
            assert_array_equal(f[0].data[idx], f[0].subset[idx])


def test_subset_compressed_image():
    """The `.subset` feature should not work with compressed images.

    It is important to verify that an exception is raised when attempting
    to `.subset` from a compressed image, to prevent incorrect (i.e., compressed)
    data being returned.
    """
    # comp.fits[1] is a compressed image with shape (440, 300)
    fn = get_pkg_data_filename('data/comp.fits')
    with fits.open(fn) as f:
        with pytest.raises(AttributeError) as excinfo:
            f[1].subset[1,2]
        assert "'CompImageHDU' object has no attribute 'subset'" in str(excinfo.value)


@pytest.mark.remote_data
def test_subset_from_s3():
    """Test `.subset` with an S3-hosted FITS file."""
    uri = f"s3://stpubdata/hst/public/j8pu/j8pu0y010/j8pu0y010_drc.fits"
    # Expected array was obtained by downloading the file locally and executing:
    # with fits.open(local_path) as hdulist:
    #     hdulist[1].data[1000:1002, 2000:2003]
    expected = np.array([[ 0.00545289,  0.0051066,  -0.00034149],
                         [ 0.00120684,  0.00782754,  0.00546404]])
    with fits.open(uri) as f:
        assert_allclose(f[1].subset[1000:1002, 2000:2003], expected, atol=1e-7)
