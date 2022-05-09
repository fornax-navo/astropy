.. currentmodule:: astropy.io.fits

..  _fits_io_cloud:

Obtaining subsets from cloud-hosted FITS files
**********************************************

Astropy offers support for extracting data from FITS files stored in the cloud.
Specifically, the `astropy.io.fits.open` function accepts the ``use_fsspec``
and ``fsspec_kwargs`` parameters, which allow remote files to be accessed in an
efficient way using the `fsspec <https://filesystem-spec.readthedocs.io>`__
package.  ``fsspec`` is an optional dependency of Astropy which supports reading
files from a range of remote and distributed storage backends, such as Amazon
and Google Cloud Storage.  This chapter explains its use.

.. note::

    The examples in this chapter require the optional dependency ``fsspec``.
    See :ref:`installing-astropy` for details on installing optional dependencies.


Subsetting FITS files hosted on an HTTP web server
==================================================

A common use case for ``fsspec`` is to read subsets of FITS data from a web
server via the HTTP protocol.  For example, let's assume you want to retrieve
data from a large image obtained by the Hubble Space Telescope available at
the following url::

    # Download link for a large Hubble archive image (213 MB)
    url = "https://mast.stsci.edu/api/v0.1/Download/file/?uri=mast:HST/product/j8pu0y010_drc.fits"

This file can be opened by passing the url to `astropy.io.fits.open`.
By default, Astropy will download the entire file to local disc before opening
it.  This works fine for small files but tends to require a lot of time and
memory for large files.

You can improve the performance for large files by passing the parameters
``use_fsspec=True`` and ``lazy_load_hdus=True`` to `open`.  This will make
Astropy download only the necessary parts of the FITS file.  For example:

.. doctest-remote-data::

    from astropy.io import fits

    # `fits.open` will download the primary header
    with fits.open(url, use_fsspec=True, lazy_load_hdus=True) as hdul:

        # Download a single header
        header = hdul[1].header

        # Download a single data array
        image = hdul[1].data

        # Download a small 10-by-20 pixel cutout
        cutout = hdul[2].section[10:20, 30:50]

The example above requires less time and memory than would be required to
download the entire file. This is because the example leverages two *lazy
data loading* features available in Astropy:

1. The ``lazy_load_hdus`` parameter takes care of loading HDU header and data
   attributes on demand rather than reading all HDUs at once.  This parameter
   is set to ``True`` by default. You do not need to pass it explicitely,
   unless you changed its default value in the :ref:`astropy:astropy_config`.
2. The `ImageHDU.section` property enables a subset of an image array to be
   read into memory without downloading the entire image. See the
   :ref:`astropy:data-sections` part of the documentation for more details.

See the :ref:`astropy:optimizing_fsspec` section for additional tips on
achieving the best performance with remote files.

.. note::

    The `.section` feature is only available for uncompressed FITS image
    extensions.  Attempting to use `.section` on a compressed image will yield
    an `AttributeError`.


Subsetting FITS files hosted in Amazon S3 cloud storage
======================================================

The FITS file used in the example above also happens to be available via
Amazon cloud storage, where it is stored in a
`public S3 bucket <https://registry.opendata.aws/hst/>`__ at the following
location::

    s3_uri = "s3://stpubdata/hst/public/j8pu/j8pu0y010/j8pu0y010_drc.fits"

With ``use_fsspec`` enabled, you can obtain a small cutout from a file stored
in Amazon S3 cloud storage in the same way as above.  For example:

.. doctest-remote-data::
    # Download a small 10-by-20 pixel cutout
    with fits.open(s3_uri, use_fsspec=True, fsspec_kwargs={"anon": True}) as hdul:
        cutout = hdul[1].section[10:20, 30:50]


.. note::

    To open ``s3://`` paths, ``fsspec`` requires an optional dependency called
    ``s3fs``.  A ``ModuleNotFoundError`` will be raised if this dependency is
    missing. See :ref:`installing-astropy` for details on installing optional
    dependencies.

Note that we used the ``fsspec_kwargs`` parameter in the example above to pass
extra arguments to the `fsspec.open` function.  Specifically, we passed the
``anon=True`` parameter to indicate that we want to retrieve data in an
anonymous way without providing Amazon cloud credentials.
For convenience, Astropy will pass ``anon=True`` by default if a path starts
with ``s3://`` and ``fsspec_kwargs`` is unspecified.

In some cases you may want to access data stored in an Amazon S3 data bucket
that is private or uses the "Requester Pays" feature. You will have to provide
a secret access key in this case. You can use the ``fsspec_kwargs`` parameter
to provide your key as follows:

.. doctest-skip::

    fsspec_kwargs = {"key": "YOUR-SECRET-KEY-ID",
                     "secret": "YOUR-SECRET-KEY"}
    with fits.open(s3_uri, use_fsspec=True, fsspec_kwargs=fsspec_kwargs) as hdul:
        cutout = hdul[2].section[10:20, 30:50]

.. warning::

    Including secret access keys inside Python code is dangerous because you
    may accidentally end up revealing your keys when you share your code with
    others. A better practice is to store your access keys via a configuration
    file or environment variables. See the ``s3fs`` documentation for guidance.


..  Obtaining the cutout from Amazon S3 in this way may be particularly performant if your code is running on a server in the same Amazon cloud region as the data.


Using :class:`~astropy.nddata.Cutout2D` with cloud-hosted FITS files
====================================================================

In the examples above we used the `.section` attribute to download small
cutouts given a set of pixel coordinates. For astronomical images it is
often more convenient to obtain cutouts based on a sky position and angular
size rather than array coordinates. For this reason, Astropy provides the
`astropy.nddata.Cutout2D` tool which makes it easy to obtain cutouts informed
by the image's World Coordinate System (`~astropy.wcs.WCS`).

For example, assume you happen to know that the image used in the examples
above contains a nice edge-on galaxy at the following position::

    from astropy.coordinates import SkyCoord
    from astropy import units as u

    # Approximate location of the galaxy
    position = SkyCoord('10h01m41.13s 02d25m20.58s')

    # Approximate size of the galaxy
    size = 5*u.arcsec

Given this sky position, we can use `~astropy.nddata.Cutout2D` in combination
with ``use_fsspec=True`` and `.section` as follows:

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


..  _optimizing_fsspec:

Tips for improving the performance of subsetting data from remote FITS files
============================================================================

The performance of the ``use_fsspec=True`` mode depends on two key factors:
the structure of the FITS file and the configuration of ``fsspec``.

Matching the FITS file structure
--------------------------------

The order in which multi-dimensional data is organized inside FITS files plays
a major role in the subsetting performance.

Astropy uses the row-major order for indexing FITS data. This means that the
right-most axis is the one that varies the fastest inside the file.
The data for this dimension tends to be located in contiguous regions of the
file and is therefore the easiest to extract.
For example, in the case of a 2D image, the slice ``.section[0, :]`` can be
obtained by downloading one contiguous region of bytes from the file.
In contrast, the slice ``.section[:, 0]`` requires accessing bytes spread
across the entire image array.

Obtaining slices of data that are well matched to the internal layout of
the FITS file generally yields the best performance.
If subsetting performance is very important to you, you may have to consider
transforming your FITS data to modify the order of the dimensions such
that they match your slicing patterns.

Configuring the ``fsspec`` block size and download strategy
-----------------------------------------------------------

The ``fsspec`` package supports different data reading and caching strategies
which aim to minimize the number of network requests.  In general the package
will attempt to download data in large contiguous blocks, similar to the
*read ahead* strategy that is employed when operating systems load local files.

You can tune the performance of ``fsspec``'s download strategy by passing custom
``block_size`` and ``cache_type`` parameters to `fsspec.open`.  You can pass
these parameters via the ``fsspec_kwargs`` argument of `astropy.io.fits.open`.

See the `fsspec documentation <https://filesystem-spec.readthedocs.io>`__
for more information on its options.
