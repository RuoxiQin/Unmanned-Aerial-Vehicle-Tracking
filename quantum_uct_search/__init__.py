#!/usr/bin/python
#-*-coding:utf-8-*-
'''this algorithm search the region using analogy of quantum'''

import test_tools
import UAV_search_algorithem
from Components.Base import Base
from Components.Plane import Plane
from Components.Intruder import Intruder
import uct_search_algorithm
__all__ = ['PartnerPreference', 'ProbabilityGrid', 'QuantumSimulator',
           'QuantumUCTControl', 'tools']
