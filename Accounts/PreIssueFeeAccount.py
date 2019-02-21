# -*- coding: utf-8 -*-
"""
Created on Fri Jun 22 12:57:52 2018

@author: Jonah.Chen
"""

import sys
import os
from constant import *
from Params import *
import pandas as pd
import numpy as np
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
import datetime

logger = get_logger(__name__)

class PreIssueFeeAccount():
    
    def __init__(self,name_fee,fees):
        self.name_fee = name_fee
        self.feeinfo = fees[name_fee]
        self.receive = {}
    
    def pay(self,date_pay,basis):
        
        return 0