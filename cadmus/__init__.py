"""cadmus package

This package intentionally avoids importing submodules at package import time to
prevent side-effects and optional dependency failures when tooling imports the
package (for example during smoke tests). Import submodules explicitly where
needed, e.g. `from cadmus.parsing import pdf_to_text`.

The original `__init__` eagerly imported many submodules which caused
ImportError/IndentationError during package import. Keep this file minimal and
safe.
"""

# Public package metadata
__version__ = "0.3.16"
__all__ = []
