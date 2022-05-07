.. currentmodule:: astropy.io.fits

..  _fits_io_cloud:

Obtaining subsets from cloud-hosted FITS files
**********************************************

Astropy offers built-in support to extract data from FITS files stored in the cloud. Specifically, the `astropy.io.fits.open` function accepts a ``use_fsspec`` parameter which allows files to be accessed in an efficient way using the `fsspec <https://filesystem-spec.readthedocs.io>`__ package.
``fsspec`` is an optional dependency of Astropy which supports opening files from a range of remote and distributed storage backends, such as web servers and Amazon or Google Cloud Storage.  This chapter provides details on its use.

.. note::

    The examples in this chapter require the optional dependency ``fsspec``.
    See :ref:`installing-astropy` for details on installing optional dependencies.


Subsetting FITS files hosted on an HTTP web server
==================================================

A common use case for ``fsspec`` is to read subsets of FITS data from a web server via the HTTP protocol.
For example, let's assume you may to retrieve a small cutout from a large image obtained by the Hubble Space Telescope available at the following download link::

    # Download link for a large Hubble archive image (213 MB)
    url = "https://mast.stsci.edu/api/v0.1/Download/file/?uri=mast:HST/product/j8pu0y010_drc.fits"

This file can be opened by passing the url to `astropy.io.fits.open`.  By default, Astropy will download the entire file to your local disc before opening it.  This works fine for small files but tends to require a lot of time and memory for large files.

You can improve the performance for large files by passing the parameters ``use_fsspec=True`` and ``lazy_load_hdus=True`` to `open`, which will cause only the necessary parts of the FITS file to be downloaded.  For example:

.. doctest-remote-data::

    from astropy.io import fits

    # `fits.open` will download the primary header (hdul[0].header)
    with fits.open(url, use_fsspec=True, lazy_load_hdus=True) as hdul:

        # Download a single header
        header = hdul[1].header

        # Download a single image array
        image = hdul[1].data

        # Download a small 10-by-20 pixel cutout using `.section`
        cutout = hdul[2].section[10:20, 30:50]

The example above requires less time than would be required to download the entire file to disc. This is because we are leveraging two "lazy data loading" features available in the Astropy FITS reader:

* The ``lazy_load_hdus=True`` parameter takes care of loading HDU header and data attributes on demand rather than reading all HDUs at once.
* The `ImageHDU.section` property enables a subset of an image array to be read into memory without downloading the entire image. Its use is not necessary for local files, which can be accessed efficiently using memory mapping, but it is beneficial for remote files. See the :ref:`astropy:data-sections` part of the documentation for more details.

.. note::

    The ``lazy_load_hdus`` parameter is set to ``True`` by default.
    You do not need to pass this parameter explicitely, unless you changed its default value in the :ref:`astropy:astropy_config` (which would be unusual).


Subsetting FITS files hosted in Amazon S3 cloud storage
======================================================

The file used in the example above also happens to be available via Amazon cloud storage, where it is stored in a `public S3 bucket <https://registry.opendata.aws/hst/>`__ at the following location::

    s3_uri = "s3://stpubdata/hst/public/j8pu/j8pu0y010/j8pu0y010_drc.fits"

With ``use_fsspec`` enabled, you can access a file stored in Amazon S3 cloud storage in the same way as a file stored on a traditional web server.  For example:

.. doctest-remote-data::
    with fits.open(s3_uri, use_fsspec=True) as hdul:
        cutout = hdul[1].section[10:20, 30:50]

.. note::

    To open ``s3://`` paths, ``fsspec`` requires an additional optional dependency called ``s3fs``.  A ``ModuleNotFoundError`` will be raised if the dependency is missing. See :ref:`installing-astropy` for details on installing optional dependencies.

The example above may be particularly fast if your code is running on a server inside the Amazon cloud.

In some cases you may want to access data stored in an Amazon S3 data bucket that is private or uses the "Requester Pays" feature. You will have to provide a secret access key in this case. You can use the ``fsspec_kwargs`` parameter to pass extra parameters such as access keys to the ``fsspec.open`` function as follows:

.. doctest-skip::

    fsspec_kwargs = {"key": "YOUR-SECRET-KEY-ID",
                     "secret": "YOUR-SECRET-KEY"}
    with fits.open(s3_uri, use_fsspec=True, fsspec_kwargs=fsspec_kwargs) as hdul:
        cutout = hdul[2].section[10:20, 30:50]

It is also possible to pass the secret access key via a configuration file or via environment variables. See the ``s3fs`` documentation for details.

.. note::

    It is possible to access data from public S3 buckets without providing credentials.
    In this case it is necessary to pass the ``fsspec_kwargs={"anon": True}`` parameter
    to `open`.  For convenience, Astropy will pass this parameter by default if a path starts with ``s3://`` and ``fsspec_kwargs`` is unspecified.


Using :class:`~astropy.nddata.Cutout2D` on cloud-hosted FITS files
==================================================================

In the examples above we noted that the `.section` attribute provides an efficient way to obtain a small cutout from a large remote image.  The use of this property requires knowing the exact array (pixel) coordinates for the desired cutout.  It is often useful to obtain cutouts based on the celestial position and size of an object instead.
We can use the `astropy.nddata.Cutout2D` tool to obtain a cutout from the cloud in this way.

Assume you happen to know that the image used in the examples above contains an edge-on galaxy at the following position::

    from astropy.coordinates import SkyCoord
    from astropy import units as u

    # Approximate location of the galaxy
    position = SkyCoord('10h01m41.13s 02d25m20.58s')

    # Approximate size of the galaxy
    size = 5*u.arcsec

Given this sky position, we can use `~astropy.nddata.Cutout2D` in combination with ``use_fsspec=True`` and `.section` as follows:

.. doctest-remote-data::
    from astropy.nddata import Cutout2D
    from astropy.wcs import WCS

    with fits.open(s3_uri, use_fsspec=True) as hdul:
        wcs = WCS(hdul[1].header)
        cutout = Cutout2D(hdul[1].section,  # use `.section` rather than `.data`!
                          position=position,
                          size=size,
                          wcs=wcs)

As a final step, you can plot the cutout using Matplotlib as follows::

    import matplotlib.pyplot as plt
    from astropy.visualization import astropy_mpl_style

    plt.style.use(astropy_mpl_style)
    plt.figure()
    plt.imshow(cutout.data, cmap='gray')
    plt.colorbar()

See :ref:`cutout_images` for more details.
