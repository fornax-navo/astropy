from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename

from numpy.testing import assert_array_equal



def test_image_subset():
    # test0.fits is a 2D image with shape (40, 40)
    fn = get_pkg_data_filename('data/test0.fits')
    with fits.open(fn) as f:
        assert_array_equal(f[1].data[0], f[1].subset[0])
        assert_array_equal(f[1].data[(0,1)], f[1].subset[(0,1)])
        #assert_array_equal(f[1].data[(0,1), (2,3)], f[1].subset[(0,1), (2,3)])

        assert_array_equal(f[1].data[:], f[1].subset[:])
        assert_array_equal(f[1].data[:, :], f[1].subset[:, :])

        assert_array_equal(f[1].data[0:10], f[1].subset[0:10])
        assert_array_equal(f[1].data[0:5, 10:15], f[1].subset[0:5, 10:15])
        assert_array_equal(f[1].data[-10:, -20:], f[1].subset[-10:, -20:])


def test_cube_subset():
    # arange.fits is a 3D array with shape (7, 10, 11)
    fn = get_pkg_data_filename('data/arange.fits')
    # TODO: add tests
