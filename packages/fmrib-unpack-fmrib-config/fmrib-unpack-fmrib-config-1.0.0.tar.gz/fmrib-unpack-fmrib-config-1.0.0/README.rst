FUNPACK - FMRIB configuration profile
=====================================

.. image:: https://img.shields.io/pypi/v/fmrib-unpack-fmrib-config.svg
   :target: https://pypi.python.org/pypi/fmrib-unpack-fmrib-config/

.. image:: https://anaconda.org/conda-forge/fmrib-unpack-fmrib-config/badges/version.svg
   :target: https://anaconda.org/conda-forge/fmrib-unpack-fmrib-config


**FUNPACK** is a Python library for pre-processing of UK BioBank data. The
``funpack-fmrib-config`` package contains a configuration profile for FUNPACK
which encodes a large set of cleaning and processing rules for a range of UK
BioBank data fields.


FUNPACK depends on ``funpack-fmrib-config``, so if FUNPACK is installed, then
you already have the ``fmrib`` configuration profile, and can use it like so::

    fmrib_unpack -cfg fmrib <output.csv> <input.csv>


Read more about FUNPACK and the FMRIB configuration profile here:

 - https://open.win.ox.ac.uk/pages/fsl/funpack/
 - https://open.win.ox.ac.uk/pages/fsl/funpack/doc/html/fmrib_profile.html
