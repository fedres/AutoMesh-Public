# Sphinx configuration for MeshMind-AFID documentation

project = 'MeshMind-AFID'
copyright = '2026, MeshMind Team'
author = 'MeshMind Team'
version = '0.2.0'
release = '0.2.0'

# Extensions
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.viewcode',
    'sphinx.ext.intersphinx',
    'myst_parser',
]

# Source files
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# Theme
html_theme = 'sphinx_rtd_theme'

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'undoc-members': True,
    'show-inheritance': True,
}

# Napoleon settings (Google/NumPy docstring support)
napoleon_google_docstring = True
napoleon_numpy_docstring = True

# Intersphinx
intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'numpy': ('https://numpy.org/doc/stable/', None),
}
