# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 16:58:37 2018

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

class FeesAccount():
    
    def __init__(self,name_fee,fees):
        self.name_fee = name_fee
        self.feeinfo = fees[name_fee]
        self.receive = {}
    
    def pay(self,date_pay,basis):
        
        period_range = (self.feeinfo['dates_to_calc'][dates_pay.index(date_pay)+1]  - self.feeinfo['dates_to_calc'][dates_pay.index(date_pay)]).days     
        if (date_pay == dates_pay[0]) and (self.name_fee in ['trustee','custodian','servicer']): 
            period_range += 1   
        else:pass
        self.receive[date_pay] = basis * self.feeinfo['rate'] * period_range / days_in_a_year
        return  self.receive[date_pay]        