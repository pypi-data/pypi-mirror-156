"""torchcuts creates a convenient namespace for commonly used functions
from PyTorch and numpy. For example:
Instead of writing torch.ones((7, 7)).to(torch.float32)
Write: J((7, 7)).to(Float32)
Shortcuts from torch are capitalized in contrast to from numpy:
Float32 == torch.float32
float32 == numpy.float32
"""

from ._base import *
