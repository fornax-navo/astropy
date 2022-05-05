.. currentmodule:: astropy.io.fits

..  _fits_io_cloud:

Working with FITS files in the cloud
************************************

**PLACEHOLDER FOR MORE DETAILED DOCUMENTATION**

The :func:`open` function supports a ``use_fsspec`` argument which allows file paths to be opened using the `fsspec <https://filesystem-spec.readthedocs.io>`__ package.  This package supports a range of remote and distributed storage backends, such as Amazon and Google Cloud Storage. The ``use_fsspec`` parameter automatically defaults to ``True`` if a file path is passed which starts with prefix ``s3://`` for Amazon S3 storage or ``gs://``
for Google Cloud storage. For example, we can open a Hubble Space Telescope image hosted in the Hubble data archive's public S3 bucket as follows:

.. doctest-remote-data::

    >>> uri = "s3://stpubdata/hst/public/j8pu/j8pu0y010/j8pu0y010_drc.fits"
    >>> with fits.open(uri, use_fsspec=True) as hdul:
    ...    data = hdul[1].section[10:12, 20:22]

Note that we accessed the data using the `.section` attribute rather than the `.data` attribute.  Using `.section` ensures that only the necessary subset of the FITS image is downloaded.  The use of `.section` enables small cutouts to obtained from remote FITS files in a way that is *significantly* faster than downloading the entire file.

