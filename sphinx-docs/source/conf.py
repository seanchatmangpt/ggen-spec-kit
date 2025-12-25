# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

import os
import sys
from pathlib import Path

# Add project root to path for autodoc
sys.path.insert(0, str(Path(__file__).parents[2] / "src"))

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

project = 'Specify CLI'
copyright = '2025, Sean Chatman'
author = 'Sean Chatman'
release = '0.0.25'
version = '0.0.25'

# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

extensions = [
    # Sphinx built-in extensions
    'sphinx.ext.autodoc',           # Auto-generate documentation from docstrings
    'sphinx.ext.autosummary',       # Generate summary tables
    'sphinx.ext.intersphinx',       # Link to other projects' documentation
    'sphinx.ext.viewcode',          # Add links to highlighted source code
    'sphinx.ext.githubpages',       # Publish to GitHub Pages
    'sphinx.ext.napoleon',          # Support for NumPy and Google style docstrings
    'sphinx.ext.todo',              # Support for TODO items
    'sphinx.ext.coverage',          # Check documentation coverage
    'sphinx.ext.ifconfig',          # Conditional content
    'sphinx.ext.extlinks',          # Markup for external links

    # Third-party extensions
    'sphinx_autodoc_typehints',     # Better type hints support
    'sphinx_copybutton',            # Add copy button to code blocks
    'sphinxcontrib.mermaid',        # Mermaid diagrams support
    'myst_parser',                  # Markdown support
]

# Autosummary settings
autosummary_generate = True
autosummary_generate_overwrite = True
autosummary_imported_members = False

# Autodoc settings
autodoc_default_options = {
    'members': True,
    'member-order': 'bysource',
    'special-members': '__init__',
    'undoc-members': True,
    'exclude-members': '__weakref__',
    'show-inheritance': True,
}

# Type hints configuration
autodoc_typehints = 'description'
autodoc_typehints_description_target = 'documented'
always_document_param_types = True
typehints_fully_qualified = False
typehints_document_rtype = True

# Napoleon settings (NumPy and Google docstrings)
napoleon_google_docstring = True
napoleon_numpy_docstring = True
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = False
napoleon_include_special_with_doc = True
napoleon_use_admonition_for_examples = True
napoleon_use_admonition_for_notes = True
napoleon_use_admonition_for_references = True
napoleon_use_ivar = True
napoleon_use_param = True
napoleon_use_rtype = True
napoleon_type_aliases = None
napoleon_attr_annotations = True

# Mermaid configuration
mermaid_version = "latest"
mermaid_init_js = "mermaid.initialize({startOnLoad:true, theme:'neutral'});"

# MyST Parser settings (Markdown support)
myst_enable_extensions = [
    "colon_fence",
    "deflist",
    "fieldlist",
    "html_admonition",
    "html_image",
    "linkify",
    "replacements",
    "smartquotes",
    "substitution",
    "tasklist",
]

# External links
extlinks = {
    'issue': ('https://github.com/github/spec-kit/issues/%s', 'issue %s'),
    'pr': ('https://github.com/github/spec-kit/pull/%s', 'PR %s'),
}

# Templates and static files
templates_path = ['_templates']
html_static_path = ['_static']
exclude_patterns = []

language = 'en'

# Source file suffixes
source_suffix = {
    '.rst': 'restructuredtext',
    '.md': 'markdown',
}

# The master toctree document
master_doc = 'index'

# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output

html_theme = 'sphinx_rtd_theme'

html_theme_options = {
    'analytics_id': '',
    'logo_only': False,
    'display_version': True,
    'prev_next_buttons_location': 'bottom',
    'style_external_links': True,
    'style_nav_header_background': '#2980B9',
    'collapse_navigation': False,
    'sticky_navigation': True,
    'navigation_depth': 4,
    'includehidden': True,
    'titles_only': False,
}

html_context = {
    "display_github": True,
    "github_user": "github",
    "github_repo": "spec-kit",
    "github_version": "main",
    "conf_py_path": "/sphinx-docs/source/",
}

html_title = f"{project} v{version} Documentation"
html_short_title = project
html_logo = None
html_favicon = None

# Custom CSS files
html_css_files = [
    'custom.css',
]

# Custom JavaScript files
html_js_files = []

# -- Options for LaTeX output ------------------------------------------------

latex_elements = {
    'papersize': 'letterpaper',
    'pointsize': '10pt',
    'preamble': '',
    'figure_align': 'htbp',
}

latex_documents = [
    (master_doc, 'SpecifyCLI.tex', f'{project} Documentation',
     author, 'manual'),
]

# -- Options for manual page output ------------------------------------------

man_pages = [
    (master_doc, 'specify', f'{project} Documentation',
     [author], 1)
]

# -- Options for Texinfo output ----------------------------------------------

texinfo_documents = [
    (master_doc, 'SpecifyCLI', f'{project} Documentation',
     author, 'SpecifyCLI', 'RDF-first specification development toolkit',
     'Miscellaneous'),
]

# -- Options for Epub output -------------------------------------------------

epub_title = project
epub_exclude_files = ['search.html']

# -- Options for intersphinx extension ---------------------------------------
# https://www.sphinx-doc.org/en/master/usage/extensions/intersphinx.html#configuration

intersphinx_mapping = {
    'python': ('https://docs.python.org/3', None),
    'typer': ('https://typer.tiangolo.com', None),
    'httpx': ('https://www.python-httpx.org', None),
    'rdflib': ('https://rdflib.readthedocs.io/en/stable', None),
}

# -- Options for todo extension ----------------------------------------------

todo_include_todos = True
todo_emit_warnings = False

# -- Additional configuration ------------------------------------------------

# If true, the current module name will be prepended to all description
# unit titles (such as .. function::).
add_module_names = True

# If true, sectionauthor and moduleauthor directives will be shown in the
# output. They are ignored by default.
show_authors = True

# The name of the Pygments (syntax highlighting) style to use.
pygments_style = 'sphinx'

# A list of ignored prefixes for module index sorting.
modindex_common_prefix = ['specify_cli.']

# -- Custom domain configuration ---------------------------------------------

# Support for documenting RDF/Turtle specifications
primary_domain = 'py'

# -- Copybutton configuration ------------------------------------------------

copybutton_prompt_text = r">>> |\.\.\. |\$ |In \[\d*\]: | {2,5}\.\.\.: | {5,8}: "
copybutton_prompt_is_regexp = True
copybutton_remove_prompts = True
copybutton_line_continuation_character = "\\"
copybutton_here_doc_delimiter = "EOT"

# -- Auto-generated API documentation ----------------------------------------

# Run sphinx-apidoc automatically when building docs
def run_apidoc(_):
    """Generate API documentation from docstrings."""
    from pathlib import Path
    import subprocess

    source_dir = Path(__file__).parents[2] / "src" / "specify_cli"
    output_dir = Path(__file__).parent / "api"

    # Create output directory
    output_dir.mkdir(exist_ok=True)

    # Run sphinx-apidoc
    subprocess.run([
        "sphinx-apidoc",
        "-f",           # Force overwrite
        "-e",           # Put each module on its own page
        "-M",           # Put module documentation before submodule documentation
        "-T",           # Don't create table of contents file
        "--implicit-namespaces",  # Interpret module paths as namespace packages
        "-o", str(output_dir),
        str(source_dir),
        str(source_dir / "**/*_test.py"),  # Exclude test files
        str(source_dir / "**/tests"),       # Exclude test directories
    ], check=True)

def setup(app):
    """Sphinx setup hook."""
    app.connect('builder-inited', run_apidoc)
