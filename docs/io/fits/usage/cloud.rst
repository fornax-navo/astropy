.. currentmodule:: astropy.io.fits

..  _fits_io_cloud:

Obtaining cutouts from cloud-hosted FITS files
**********************************************

Astropy offers built-in support to open and extract data from FITS files stored in the cloud. Specifically, the `astropy.io.fits.open` function accepts a ``use_fsspec`` parameter which allows file paths to be opened using the `fsspec <https://filesystem-spec.readthedocs.io>`__ package.
``fsspec`` is an optional dependency of Astropy which supports opening files from a range of remote and distributed storage backends, such as Amazon and Google Cloud Storage.  This chapter provides details on its use.


Accessing FITS files hosted on a traditional webserver
======================================================

For the purpose of this example, we pre-selected an image obtained by the Hubble Space Telescope which can be obtained from the Hubble Data Archive at the following download link::

    >>> archive_url = "https://mast.stsci.edu/api/v0.1/Download/file/?uri=mast:HST/product/j8pu0y010_drc.fits"

We can open this file by passing its url to `astropy.io.fits.open`.  The important part is to make sure we use the `use_fsspec=True` parameter, which takes care of downloading only the parts required rather than downloading the entire file:

.. doctest-remote-data::

    from astropy.io import fits
    with fits.open(archive_url, use_fsspec=True) as hdul:
        cutout = hdul[1].section[10:13, 20:22]

This example obtained a tiny 2-by-3 pixel cutout of the image data.  You should find that this example runs very fast; much faster than downloading the entire file to disk.  This is because we used the `astropy.io.fits.ImageHDU.section` property to access the image values.

`.section` is a special property which enables a subset of an image array to be read into memory without downloading the entire file.  We could have obtained the same values using the `.data` attribute (e.g., `hdul[1].data[10:13, 20:22]`), but it would have triggered AstroPy to download the entire image. This generally requires a lot more time and memory.
See the :ref:`astropy:data-sections` section of the documentation for more details.


.. note::

    The `use_fsspec=True` option requires the optional dependency `fsspec`.
    See the Astropy installation instructions for details.


.. note::

    If you pass a path with prefix `http://` or `https://`, Astropy's default
    behavior is to download the file to local disc entirely before opening it.
    You must pass the `use_fsspec=True` parameter to access the file in a more
    efficient way.


Accessing FITS files hosted in Amazon S3 cloud storage
======================================================

The file used in the example above also happens to be available via Amazon cloud storage, where it is stored in a `public S3 bucket <https://registry.opendata.aws/hst/>`__ at the following location::

    s3_uri = "s3://stpubdata/hst/public/j8pu/j8pu0y010/j8pu0y010_drc.fits"

We can obtain the exact same values from Amazon S3 cloud storage in the same way.  This may be faster if your code is running inside the Amazon cloud:

.. doctest-remote-data::
    with fits.open(s3_uri, use_fsspec=True) as hdul:
        cutout = hdul[1].section[10:13, 20:22]

In some cases you may want to access data stored in the Amazon S3 cloud from a data bucket that is private or uses the "Requester Pays" feature. In this case, you will have to provide a secret access key via a configuration file, environment variables, or parameters. You can use the `fsspec_kwargs` parameter to pass such extra parameters to the ``fsspec`` library as follows:

.. doctest-skip::

    fsspec_kwargs = {"key": "YOUR-KEY-ID",
                     "secret": "YOUR-SECRET-KEY"}
    with fits.open(s3_uri, use_fsspec=True, fsspec_kwargs=fsspec_kwargs) as hdul:
        cutout = hdul[2].section[10:13, 20:22]

.. note::

    Opening ``s3://`` paths requires the optional dependency ``s3fs`` to be installed
    in addition to ``fsspec``.  See the Astropy installation instructions for details.


.. note::

    It is possible to access data from public S3 buckets without providing credentials.
    In this case it is necessary to pass the `fsspec_kwargs={"anon": True}` setting
    to `astropy.io.fits.open`.  Fortunately, this is the default behavior for paths
    starting with prefix ``s3://``.


Using Cutout2D on cloud-hosted FITS files
=========================================

The `.section` attribute requires knowledge of the array coordinates.  It is often useful to obtain cutouts based on the celestial position and size on an object instead.
We can use the `Cutout2D` tool to obtain a cutout from the cloud in this way.

The image in the example above contains an edge-on galaxy at the following position::

    from astropy.coordinates import SkyCoord
    from astropy import units as u

    # Approximate location of the galaxy
    position = SkyCoord('10h01m41.13s 02d25m20.58s')
    # Approximate size of the galaxy
    size = 5*u.arcsec

We can use the `Cutout2D` tool in combination with `use_fsspec=True` and `.section` as follows:

.. doctest-remote-data::
    from astropy.nddata import Cutout2D
    from astropy.wcs import WCS

    with fits.open(s3_uri, use_fsspec=True) as hdul:
        wcs = WCS(hdul[1].header)
        cutout = Cutout2D(hdul[1].section,
                        position=position,
                        size=size,
                        wcs=wcs)

Again, note that we passed the .section property to the cutout tool (rather than .data) to avoid downloading unncessary data.

As a final step, we can plot the cutout obtained using Matplotlib as follows::

    import matplotlib.pyplot as plt
    from astropy.visualization import astropy_mpl_style
    plt.style.use(astropy_mpl_style)
    plt.figure()
    plt.imshow(cutout.data, cmap='gray')
    plt.colorbar()

We successfully obtained a small cutout of a large FITS image without downloading the entire file locally.
