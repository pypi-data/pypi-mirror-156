# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
import os
import sys
sys.path.insert(0, os.path.abspath('.'))
sys.path.insert(0, os.path.abspath('..'))

# -- Project information -----------------------------------------------------

project = 'PyPlr'
copyright = '2021, Joel T. Martin and Manuel Spitschan'
author = 'Joel T. Martin and Manuel Spitschan'

# The full version, including alpha/beta/rc tags
release = 'v1.0'


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = ["sphinxcontrib.napoleon", "sphinx.ext.autodoc", "sphinx_autodoc_typehints", "nbsphinx"]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = ['_build', 'Thumbs.db', '.DS_Store']

typehints_document_rtype=False
typehints_use_rtype=False
# -- Options for HTML output -------------------------------------------------
smart_quotes = False
# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'alabaster'
html_logo = '../logo/orange_eye.png'
html_theme_options = {
    'github_user': 'PyPlr',
    'github_repo': 'cvd_pupillometry',
    'extra_nav_links': {
        'PyPi': 'https://pypi.org/project/pyplr/', 
        'Publication':'https://link.springer.com/article/10.3758/s13428-021-01759-3'
    },
    'description': 'A Python software for researching the pupillary light reflex.'
}
# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
