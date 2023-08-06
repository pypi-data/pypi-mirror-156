#Project module
#Third party module
import numpy as np
#Python module
from dataclasses import dataclass
from datetime import datetime as dt
from enum import Enum
import logging

log = logging.getLogger()

@dataclass
class DescriptionTICData:
    dateTime: dt
    timeSlice: float
    delay: float
    countChannel: int
    countSlice: int
    threshold: np.ndarray

@dataclass
class DescriptionDevice:
    name: str
    channelFrom: int
    channelTo: int
    

@dataclass
class RawTICData:
    descriptionTICData: DescriptionTICData
    matrix: np.ndarray