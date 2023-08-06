"""
dflow_hello
dflow demo OP
"""
import sys
if sys.version_info < (3, 10):
    from importlib_metadata import version
else:
    from importlib.metadata import version
from .hello import Hello

__version__ = version("dflow_hello")
