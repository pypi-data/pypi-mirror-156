"""Basis stuff"""

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

ic.configureOutput(includeContext=True)
rand = random.rand


def LOL() -> NoReturn:
  """This function just lists all persistent imports. This way pycharm
  will not remove them when optimizing imports!"""
  return [
    Floor,
    Max,
    Ceil,
    Sort,
    Int32,
    oh,
    int32,
    rand,
    jp,
    array,
    ndarray,
    random,
    Tensor,
    ImageQt,
    to_pil_image,
    Adam,
    Rand,
    Device,
    NoReturn,
    Float32,
    ArgSort,
    Un,
    Lin,
    Min,
    F,
    Cat,
    Oh,
    J,
    Sum, ]

#
# def fail():
#   """Where is the duplicate?"""
#   return [
#     to_pil_image,
#     Adam,
#     Rand,
#     Device,
#     NoReturn,
#     Float32,
#     ArgSort,
#     Un,
#     Lin,
#     Min,
#     F,
#     Cat,
#     Oh,
#     J,
#     Sum,
#   ]
