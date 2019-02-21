# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 18:10:32 2018

@author: Jonah.Chen
"""

import sys
import os
from constant import *
import pandas as pd
import numpy as np
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
import datetime


class TaxAccount():
    
    def __init__(self,name_fee,fees):
        self.name_fee = name_fee
        self.feeinfo = fees[name_fee]
        self.receive = {}
        
    def pay(self,day_pay,basis):
       
         self.receive[day_pay] = basis * self.feeinfo['rate']
         return self.receive[day_pay]
