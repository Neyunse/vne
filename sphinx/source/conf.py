#from sphinxawesome_theme import ThemeOptions, __version__
from dataclasses import asdict
import sys
# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'VNengine'
copyright = '2025, Neyunse'
author = 'Neyunse'

sys.path.insert(0, '../..')
from vne._version import __version__
version = release = __version__
GitHubPage = "https://github.com/neyunse/vne"

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = []

templates_path = ['_templates']
exclude_patterns = []
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.autosummary',
    'myst_parser',
    'sphinx_design'
]
autosummary_generate = True
autosummary_imported_members = True
# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_title = project
html_theme = "shibuya"
html_last_updated_fmt = ""
html_use_index = False  # Don't create index
html_domain_indices = False  # Don't need module indices
html_copy_source = False  # Don't need sources
#html_logo = ""
#html_favicon = "assets/favicon-128x128.png"
#html_baseurl = ""
html_extra_path = ["robots.txt", "_redirects"]
html_permalinks_icon = '<span>#</span>'
html_static_path = ['_static']
 
exclude_patterns = ["public", "includes", "**/includes", "jupyter_execute"]
substitutions = [
    ":tocdepth: 3",
    " ",
    ".. meta::",
    "   :author: neyunse",
    ".. |rst| replace:: reStructuredText",
    ".. |product| replace:: VNEngine",
    f".. |current| replace:: {__version__}",
]
rst_prolog = "\n".join(substitutions)

 
html_baseurl = "https://neyunse.github.io/vne/"

source_suffix = {
    '.rst': 'restructuredtext',
    '.txt': 'restructuredtext',
    '.md': 'markdown',
}

html_theme_options = {
    "nav_links": [
        {
            "title": "Quickstart",
            "url": "quickstart"
        },
        {
            "title": "Changelog",
            "url": "changelog"
        },
    ],
    "github_url": "https://github.com/Neyunse/vne",
    "discussion_url": "https://github.com/Neyunse/vne/discussions",
}

