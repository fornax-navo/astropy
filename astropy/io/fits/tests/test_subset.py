from astropy.io import fits
from astropy.utils.data import get_pkg_data_filename

from numpy.testing import assert_array_equal



def test_subset():
    fn = get_pkg_data_filename('data/test0.fits')
    with fits.open(fn) as f:
        assert_array_equal(f[1].data[:], f[1].subset[:])
        assert_array_equal(f[1].data[:, :], f[1].subset[:, :])
        assert_array_equal(f[1].data[0:10], f[1].subset[0:10])
        assert_array_equal(f[1].data[0:5, 10:15], f[1].subset[0:5, 10:15])
        assert_array_equal(f[1].data[-10:, -20:], f[1].subset[-10:, -20:])
