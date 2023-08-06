"""Serialize Python classes as Python code.

Import the package::

   import exportpy

This is the complete API reference:

.. autosummary::
   :toctree: .

   dataclass_to_py
"""

__version__ = "0.0.1"  # denote a pre-release for 0.1.0 with 0.1a1

from ._core import dataclass_to_py  # noqa
