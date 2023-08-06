# torchcuts - A set of shortcuts to common functions from PyTorch and Numpy

Instead of:
~~~
X = torch.ones((7, 7)).to(torch.float32)
~~~

Use torchcuts!

~~~
X = J((7, 7)).to(Float32)
~~~

torchcuts includes a collection of functions mainly from PyTorch and numpy. To avoid namespace collisions, torch functions are capitalized:
~~~
Float32 == torch.float32
float32 == numpy.float32
~~~

## Installation

You can find the latest version on pypi: https://pypi.org/project/torchcuts/
To install, simply run:

~~~
pip install torchcuts
~~~

## Content
Below you can see the import statements
~~~
from typing import NoReturn

import torch.functional as F
from PIL.ImageQt import ImageQt
from icecream import ic
from numpy import array as array
from numpy import int32 as int32
from numpy import ndarray
from numpy import ones as jp
from numpy import random as random
from numpy import zeros as oh
from torch import Tensor
from torch import argsort as ArgSort
from torch import cat as Cat
from torch import ceil as Ceil
from torch import device as Device
from torch import float32 as Float32
from torch import floor as Floor
from torch import int32 as Int32
from torch import linspace as Lin
from torch import max as Max
from torch import min as Min
from torch import ones as J
from torch import rand as Rand
from torch import sort as Sort
from torch import sum as Sum
from torch import unsqueeze as Un
from torch import zeros as Oh
from torch.optim import Adam
from torchvision.transforms.functional import to_pil_image
~~~

## Bonus functions
As this is a work in progress, no bonus functions are yet implemented.