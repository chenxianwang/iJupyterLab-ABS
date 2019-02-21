# -*- coding: utf-8 -*-
"""
Created on Thu Jun 21 14:55:13 2018

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

class BondPrinAccount():
    
    def __init__(self,name_bond,Bonds):
        self.name_bond = name_bond
        self.bondinfo = Bonds[name_bond]
        self.balance = {}
        self.receive = {}
    
    def pay_then_ToNext(self,date_pay,amount_available,amount_reserve):
                    
        if self.bondinfo['amount'] == 0:
            self.balance[date_pay] = 0
            self.receive[date_pay] = 0
            return amount_available,amount_reserve
        
        elif amount_available < -0.0001:
            if self.name_bond != 'EE':
                logger.info('self.bondinfo[amount] of {0} is {1}'.format(self.name_bond,self.bondinfo['amount']))
                logger.info('amount_available for {0} on {1} is {2}: '.format(self.name_bond,date_pay,amount_available))
            #sys.exit("!!!!!!!!!    Can not cover payment      !!!!!!!")
            #self.bondinfo['amount'] -= amount_available
            self.balance[date_pay] = self.bondinfo['amount']
            self.receive[date_pay] = 0 #-amount_available
            
            amount_reserve += amount_available
            amount_available = 0
            
            return amount_available,amount_reserve
        
        elif self.bondinfo['amount'] >= amount_available:
            self.bondinfo['amount'] -= amount_available
            self.balance[date_pay] = self.bondinfo['amount']
            self.receive[date_pay] = amount_available
            return 0,amount_reserve
        else: 
            #logger.info('date_pay for {0} is {1}'.format(self.name_bond,date_pay))
            self.receive[date_pay] = self.bondinfo['amount']
            self.bondinfo['amount'] = 0
            self.balance[date_pay] = self.bondinfo['amount']
            
            if amount_available < self.receive[date_pay] :
                logger.info('amount_available is {0}, receive[date_pay] is {1}'.format(amount_available,receive[date_pay]))
            
            return amount_available - self.receive[date_pay],amount_reserve
           
    def iBalance(self,date_pay):
        #logger.info('date_pay for {0} is {1}'.format(self.name_bond,date_pay))
        try:
            return self.bondinfo['amount'] if (date_pay==dates_pay[0])|(not self.balance) else self.balance[date_pay+relativedelta(months= -1)]
        except(KeyError):
            return 0
