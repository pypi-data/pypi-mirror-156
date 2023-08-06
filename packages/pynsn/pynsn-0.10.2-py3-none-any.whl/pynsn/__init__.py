"""
NonSyNum package

Creating Non-Symbolic Number Displays
"""

__author__ = 'Oliver Lindemann <lindemann@cognitive-psychology.eu>'
__version__ = '0.10.2'

from sys import version_info as _python_version_info
if not(_python_version_info[0] >= 3 and _python_version_info[1] >= 6):
    raise RuntimeError("PyNsN {0} ".format(__version__) +
                      "is not compatible with Python {0}.{1}. ".format(
                                                    _python_version_info[0],
                                                    _python_version_info[1]) +
                      "Please use Python 3.6+.")

from .image._colour import Colour, ImageColours
from . import factory, match
from ._lib.coordinate2D import Coordinate2D
from ._lib.shape import Dot, Rectangle
from ._lib.arrays import DotArray
from ._lib.arrays import RectangleArray
from ._lib.visual_features import VisualFeature
from ._lib import distributions as distr


