# -*- coding: utf-8 -*-
"""
Created on Thu Jun 28 21:18:06 2018

@author: Jonah.Chen
"""

import sys
import os
from copy import deepcopy
from constant import *
from Params import *
import pandas as pd
import numpy as np
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
import datetime
from Deal import Deal
from AssetsCashFlow import AssetsCashFlow
from APCF_adjuster import APCF_adjuster
from Accounts.AssetPoolAccount import AssetPoolAccount

low_memory=False

logger = get_logger(__name__)

class RevolvingDeal(Deal):
    
    def __init__(self,name,date_pool_cut,date_trust_effective,RevolvingDeal_or_not,date_revolving_pools_cut):
        super().__init__(name,date_pool_cut,date_trust_effective)
        
        self.RevolvingDeal = RevolvingDeal_or_not
        self.date_revolving_pools_cut = date_revolving_pools_cut
        
        logger.info('If it is RevolvingDeal: {0}'.format(self.RevolvingDeal))
        if self.RevolvingDeal == True:
            logger.info('date_revolving_pools_cut: {0}'.format(self.date_revolving_pools_cut))
        
        self.RevolvingPool_PurchaseAmount = {}
        self.total_purchase_amount = {}
        
        self.CDR_all = {}
        self.CDR_R = {}
        
        self.amount_default_all = {}
        self.amount_default_R = {}
        
        self.apcf_adjusted = {}  # Original_adjusted + Revolving_adjusted
        
        self.apcf_revolving_structure = pd.DataFrame()
        self.apcf_revolving,self.df_ppmt,self.df_ipmt = {},{},{}
        self.dates_recycle_list_revolving = {}
        self.apcf_revolving_adjusted = {}
        self.apcf_revolving_adjusted_all = {}
        
        self.APCF_R_adjusted_save = {}
        
        self.df_AP_PAcc_all_DeSimu = pd.DataFrame() 
        
    def get_rAPCF_structure(self):
        
        if self.RevolvingDeal is True:
            logger.info('get_rAPCF_structure...')
            self.apcf_revolving_structure = self.get_rearranged_APCF_structure()
        else:
            logger.info('There is no rAPCF.')
            pass
        #save_to_excel(self.apcf_revolving_structure,'Rearrange_APCF_Structure',wb_name)
        
    def init_rAP_scenarios(self,scenarios):
        for scenario_id in self.scenarios.keys():
            self.CDR_R[scenario_id] = {}
            self.apcf_revolving[scenario_id] = {}
            self.df_ppmt[scenario_id],self.df_ipmt[scenario_id] = {},{}
            self.dates_recycle_list_revolving[scenario_id] = {}
            
            self.apcf_revolving_adjusted[scenario_id] = {}
            self.APCF_R_adjusted_save[scenario_id] = {}
            self.apcf_revolving_adjusted_all[scenario_id] = pd.DataFrame()
            
            self.RevolvingPool_PurchaseAmount[scenario_id] = {}
            self.total_purchase_amount[scenario_id] = 0.0
        
        
    def init_rAP_Acc(self):
        logger.info('init_rAP_Acc...')
                
        self.AP_PAcc_original,self.AP_PAcc_actual = {},{}
        self.AP_PAcc_pay,self.AP_PAcc_buy = {},{}
        self.AP_PAcc_overdue_1_30_currentTerm,self.AP_PAcc_overdue_1_30_allTerm = {},{}
        self.AP_PAcc_overdue_31_60_currentTerm,self.AP_PAcc_overdue_31_60_allTerm = {},{}
        self.AP_PAcc_overdue_61_90_currentTerm,self.AP_PAcc_overdue_61_90_allTerm = {},{}
        self.AP_PAcc_loss_currentTerm,self.AP_PAcc_loss_allTerm = {},{}

        self.AP_IAcc_original,self.AP_IAcc_actual = {},{}
        self.AP_IAcc_pay,self.AP_IAcc_buy = {},{}
        self.AP_IAcc_overdue_1_30_currentTerm,self.AP_IAcc_overdue_1_30_allTerm = {},{}
        self.AP_IAcc_overdue_31_60_currentTerm,self.AP_IAcc_overdue_31_60_allTerm = {},{}
        self.AP_IAcc_overdue_61_90_currentTerm,self.AP_IAcc_overdue_61_90_allTerm = {},{}
        self.AP_IAcc_loss_currentTerm,self.AP_IAcc_loss_allTerm = {},{}
                
        self.AP_PAcc_outstanding,self.AP_IAcc_outstanding = {},{} 
        self.AP_PAcc_reserve = {}
                
        self.AP_PAcc_original_R,self.AP_PAcc_actual_R = {},{}
        self.AP_PAcc_pay_R,self.AP_PAcc_buy_R = {},{}
        self.AP_PAcc_overdue_1_30_currentTerm_R,self.AP_PAcc_overdue_1_30_allTerm_R = {},{}
        self.AP_PAcc_overdue_31_60_currentTerm_R,self.AP_PAcc_overdue_31_60_allTerm_R = {},{}
        self.AP_PAcc_overdue_61_90_currentTerm_R,self.AP_PAcc_overdue_61_90_allTerm_R = {},{}
        self.AP_PAcc_loss_currentTerm_R,self.AP_PAcc_loss_allTerm_R = {},{}

        self.AP_IAcc_original_R,self.AP_IAcc_actual_R = {},{}
        self.AP_IAcc_pay_R,self.AP_IAcc_buy_R = {},{}
        self.AP_IAcc_overdue_1_30_currentTerm_R,self.AP_IAcc_overdue_1_30_allTerm_R = {},{}
        self.AP_IAcc_overdue_31_60_currentTerm_R,self.AP_IAcc_overdue_31_60_allTerm_R = {},{}
        self.AP_IAcc_overdue_61_90_currentTerm_R,self.AP_IAcc_overdue_61_90_allTerm_R = {},{}
        self.AP_IAcc_loss_currentTerm_R,self.AP_IAcc_loss_allTerm_R = {},{}
                
        self.AP_PAcc_outstanding_R,self.AP_IAcc_outstanding_R = {},{} 
        
                
        for scenario_id in self.scenarios.keys():
            
            self.AP_PAcc_original_R[scenario_id],self.AP_PAcc_actual_R[scenario_id] = {},{}
            self.AP_PAcc_pay_R[scenario_id],self.AP_PAcc_buy_R[scenario_id] = {},{}
            self.AP_PAcc_overdue_1_30_currentTerm_R[scenario_id],self.AP_PAcc_overdue_1_30_allTerm_R[scenario_id] = {},{}
            self.AP_PAcc_overdue_31_60_currentTerm_R[scenario_id],self.AP_PAcc_overdue_31_60_allTerm_R[scenario_id] = {},{}
            self.AP_PAcc_overdue_61_90_currentTerm_R[scenario_id],self.AP_PAcc_overdue_61_90_allTerm_R[scenario_id] = {},{}
            self.AP_PAcc_loss_currentTerm_R[scenario_id],self.AP_PAcc_loss_allTerm_R[scenario_id] = {},{}
    
            self.AP_IAcc_original_R[scenario_id],self.AP_IAcc_actual_R[scenario_id] = {},{}
            self.AP_IAcc_pay_R[scenario_id],self.AP_IAcc_buy_R[scenario_id] = {},{}
            self.AP_IAcc_overdue_1_30_currentTerm_R[scenario_id],self.AP_IAcc_overdue_1_30_allTerm_R[scenario_id] = {},{}
            self.AP_IAcc_overdue_31_60_currentTerm_R[scenario_id],self.AP_IAcc_overdue_31_60_allTerm_R[scenario_id] = {},{}
            self.AP_IAcc_overdue_61_90_currentTerm_R[scenario_id],self.AP_IAcc_overdue_61_90_allTerm_R[scenario_id] = {},{}
            self.AP_IAcc_loss_currentTerm_R[scenario_id],self.AP_IAcc_loss_allTerm_R[scenario_id] = {},{}
        
            self.AP_PAcc_outstanding_R[scenario_id],self.AP_IAcc_outstanding_R[scenario_id] = {},{} 
        
        for scenario_id in self.scenarios.keys():
            self.AP_PAcc_original[scenario_id] = deepcopy(self.AP_PAcc_original_O[scenario_id])
            self.AP_PAcc_actual[scenario_id] = deepcopy(self.AP_PAcc_actual_O[scenario_id])
            self.AP_PAcc_pay[scenario_id] = deepcopy(self.AP_PAcc_pay_O[scenario_id])
            self.AP_PAcc_buy[scenario_id] = deepcopy(self.AP_PAcc_buy_O[scenario_id])
            self.AP_PAcc_overdue_1_30_currentTerm[scenario_id] = deepcopy(self.AP_PAcc_overdue_1_30_currentTerm_O[scenario_id])
            self.AP_PAcc_overdue_1_30_allTerm[scenario_id] = deepcopy(self.AP_PAcc_overdue_1_30_allTerm_O[scenario_id])
            self.AP_PAcc_overdue_31_60_currentTerm[scenario_id] = deepcopy(self.AP_PAcc_overdue_31_60_currentTerm_O[scenario_id])
            self.AP_PAcc_overdue_31_60_allTerm[scenario_id] = deepcopy(self.AP_PAcc_overdue_31_60_allTerm_O[scenario_id])
            self.AP_PAcc_overdue_61_90_currentTerm[scenario_id] = deepcopy(self.AP_PAcc_overdue_61_90_currentTerm_O[scenario_id])
            self.AP_PAcc_overdue_61_90_allTerm[scenario_id] = deepcopy(self.AP_PAcc_overdue_61_90_allTerm_O[scenario_id])
            self.AP_PAcc_loss_currentTerm[scenario_id] = deepcopy(self.AP_PAcc_loss_currentTerm_O[scenario_id])
            self.AP_PAcc_loss_allTerm[scenario_id] = deepcopy(self.AP_PAcc_loss_allTerm_O[scenario_id])

            self.AP_IAcc_original[scenario_id] = deepcopy(self.AP_IAcc_original_O[scenario_id])                 
            self.AP_IAcc_actual[scenario_id] = deepcopy(self.AP_IAcc_actual_O[scenario_id])
            self.AP_IAcc_pay[scenario_id] = deepcopy(self.AP_IAcc_pay_O[scenario_id])
            self.AP_IAcc_buy[scenario_id] = deepcopy(self.AP_IAcc_buy_O[scenario_id])
            self.AP_IAcc_overdue_1_30_currentTerm[scenario_id] = deepcopy(self.AP_IAcc_overdue_1_30_currentTerm_O[scenario_id])
            self.AP_IAcc_overdue_1_30_allTerm[scenario_id] = deepcopy(self.AP_IAcc_overdue_1_30_allTerm_O[scenario_id])
            self.AP_IAcc_overdue_31_60_currentTerm[scenario_id] = deepcopy(self.AP_IAcc_overdue_31_60_currentTerm_O[scenario_id])
            self.AP_IAcc_overdue_31_60_allTerm[scenario_id] = deepcopy(self.AP_IAcc_overdue_31_60_allTerm_O[scenario_id])
            self.AP_IAcc_overdue_61_90_currentTerm[scenario_id] = deepcopy(self.AP_IAcc_overdue_61_90_currentTerm_O[scenario_id])
            self.AP_IAcc_overdue_61_90_allTerm[scenario_id] = deepcopy(self.AP_IAcc_overdue_61_90_allTerm_O[scenario_id])
            self.AP_IAcc_loss_currentTerm[scenario_id] = deepcopy(self.AP_IAcc_loss_currentTerm_O[scenario_id])
            self.AP_IAcc_loss_allTerm[scenario_id] = deepcopy(self.AP_IAcc_loss_allTerm_O[scenario_id])
                        
            self.AP_PAcc_outstanding,self.AP_IAcc_outstanding = deepcopy(self.AP_PAcc_outstanding_O),deepcopy(self.AP_IAcc_outstanding_O)
            self.AP_PAcc_reserve = deepcopy(self.AP_PAcc_reserve_O)
            self.amount_default_all = deepcopy(self.amount_default_O)
            
        logger.info('init_rAP_Acc is done.')
#            logger.info('''oAP_ACC accounts consist of:  
#            Principal Collection Accounts:
#            self.AP_PAcc_original_R,self.AP_PAcc_actual_R,self.AP_PAcc_pay_R,self.AP_PAcc_buy_R. 
#            and self.AP_PAcc_original,self.AP_PAcc_actual,self.AP_PAcc_pay,self.AP_PAcc_buy.
#            
#            self.AP_PAcc_actual_R = [['ER_recycle_principal','Normal_recycle_principal','Redemption_recycle_principal',
#                                      'Overdue_1_30_recycle_principal','Overdue_31_60_recycle_principal','Overdue_61_90_recycle_principal',
#                                      'Recovery_recycle_principal']].sum(axis=1)
#            
#            self.AP_PAcc_original = self.AP_PAcc_original_O + self.AP_PAcc_original_R,
#            self.AP_PAcc_actual = self.AP_PAcc_actual_O + self.AP_PAcc_actual_R,
#            self.AP_PAcc_pay = self.AP_PAcc_pay_O + self.AP_PAcc_pay_R,
#            self.AP_PAcc_buy = self.AP_PAcc_buy_O + self.AP_PAcc_buy_R. 
#            
#            The same type of accounts are also created for Interest Collection.''')
            
    def prepare_revolving_pool(self,scenario_id,which_revolving_pool,purchase_amount,apcf_revolving_structure):
        
        self.RevolvingPool_PurchaseAmount[scenario_id][which_revolving_pool] = purchase_amount
        self.total_purchase_amount[scenario_id] += purchase_amount
        
        logger.info('purchase_amount for scenario_id {0} and Revolving pool {1} is :{2:,.2f}'.format(scenario_id,which_revolving_pool,purchase_amount))
        #logger.info('Total purchase_amount is {0}'.format(self.total_purchase_amount[scenario_id]))
        
        apcf_revolving_structure['OutstandingPrincipal'] = purchase_amount * apcf_revolving_structure['OutstandingPrincipal_Proportion']
        last_term = int((apcf_revolving_structure['Term_Remain'] + apcf_revolving_structure['first_due_period_R']).max())
        self.dates_recycle_list_revolving[scenario_id][which_revolving_pool] = [self.date_revolving_pools_cut[which_revolving_pool-1] + relativedelta(months=i) - datetime.timedelta(days=1) for i in range(1,last_term+1+3)] #for recycle DefaultAssets
        #logger.info('self.dates_recycle_list_revolving[0] is {0}'.format(dates_recycle_list_revolving[0]))
        for d_r in self.dates_recycle_list_revolving[scenario_id][which_revolving_pool]:
            apcf_revolving_structure[d_r] = 0
        
        self.apcf_revolving[scenario_id][which_revolving_pool],self.df_ppmt[scenario_id][which_revolving_pool],self.df_ipmt[scenario_id][which_revolving_pool] = cash_flow_collection(apcf_revolving_structure,self.dates_recycle_list_revolving[scenario_id][which_revolving_pool],'first_due_period_R','Revolving'+str(which_revolving_pool),wb_name)
        #save_to_excel(apcf_revolving_structure,'Revolving_APCF_Structure_' + str(which_revolving_pool),wb_name)
        #save_to_excel(self.apcf_revolving[scenario_id][which_revolving_pool],'rAPCF_' + scenario_id + str(which_revolving_pool),wb_name)


                    #logger.info('self.AP_PAcc_actual[scenario_id][k] for date {0} is {1}'.format(datetime.date(2018,8,31),self.AP_PAcc_actual[scenario_id][datetime.date(2018,8,31)]))
    def adjusted_all_rAP(self,scenario_id):
        if self.RevolvingDeal is not True:
            pass
        else:
 
            for which_revolving_pool in range(1,len(self.date_revolving_pools_cut) + 1):
                if self.apcf_revolving_adjusted_all[scenario_id].empty :
                    self.apcf_revolving_adjusted_all[scenario_id] = self.apcf_revolving_adjusted[scenario_id][which_revolving_pool][['date_recycle','total_recycle_principal','principal_loss_allTerm','total_outstanding_principal']]
                else: 
                    self.apcf_revolving_adjusted_all[scenario_id] = self.apcf_revolving_adjusted_all[scenario_id].merge(self.apcf_revolving_adjusted[scenario_id][which_revolving_pool][['date_recycle','total_recycle_principal','principal_loss_allTerm','total_outstanding_principal']],left_on = 'date_recycle',right_on = 'date_recycle', how = 'outer')
            #logger.info('self.AP_PAcc_loss_allTerm[scenario_id][dates_recycle_list_revolving[-1]] on dates_recycle_list_revolving[-1] {0} is {1}'.format(dates_recycle_list_revolving[-1],self.AP_PAcc_loss_allTerm[scenario_id][dates_recycle_list_revolving[-1]]))
            #logger.info('sum([self.AP_PAcc_original[scenario_id][k] for k in dates_recycle])] is {0}'.format(sum([self.AP_PAcc_original[scenario_id][k] for k in dates_recycle])))
                    
    def CDR_calc_R(self,scenario_id):
        if self.RevolvingDeal is not True:
            pass
        else:

                for which_revolving_pool in range(1,len(self.date_revolving_pools_cut) + 1):    
                    self.CDR_R[scenario_id][scenario_id+'_R'+str(which_revolving_pool)] =  [self.AP_PAcc_loss_allTerm_R[scenario_id][which_revolving_pool][self.dates_recycle_list_revolving[scenario_id][which_revolving_pool][-1]],
                                                                                              self.RevolvingPool_PurchaseAmount[scenario_id][which_revolving_pool],
                                                                                              self.AP_PAcc_loss_allTerm_R[scenario_id][which_revolving_pool][self.dates_recycle_list_revolving[scenario_id][which_revolving_pool][-1]]/self.RevolvingPool_PurchaseAmount[scenario_id][which_revolving_pool]
                                                                                              ]  
                    logger.info('CDR for {0} is: {1:.4%} for Revolving Pool {2} '.format(scenario_id,self.CDR_R[scenario_id][scenario_id+'_R'+str(which_revolving_pool)][2],which_revolving_pool))
                    self.amount_default_all[scenario_id] += deepcopy(self.AP_PAcc_loss_allTerm_R[scenario_id][which_revolving_pool][self.dates_recycle_list_revolving[scenario_id][which_revolving_pool][-1]])
                
    def CDR_calc_All(self,scenario_id):
        
        self.CDR_all[scenario_id+'_All'] =  [self.amount_default_all[scenario_id],
                                             (amount_total_issuance+sum([self.RevolvingPool_PurchaseAmount[scenario_id][r] for r in range(1,nbr_revolving_pools+1)])),
                                             self.amount_default_all[scenario_id] / (amount_total_issuance+sum([self.RevolvingPool_PurchaseAmount[scenario_id][r] for r in range(1,nbr_revolving_pools+1)]))
                                             ]  
        logger.info('CDR_all for {0} is: {1:.4%} '.format(scenario_id,self.CDR_all[scenario_id+'_All'][2]))



    def prepare_PurchaseAmount(self,for_which_revolving_pool,scenario_id):
        amount_principal = self.AP_PAcc_actual[scenario_id][dates_recycle[for_which_revolving_pool - 1]]
        amount_interest = self.AP_IAcc_actual[scenario_id][dates_recycle[for_which_revolving_pool - 1]]
        #logger.info('amount_interest for Revolving Pool {0} is {1}'.format(for_which_revolving_pool,amount_interest))
        
        amount_principal_reserve = 0
        amount_interest_reserve = 0  
        amount_interest_reserve += amount_interest * fees['tax']['rate']
        #logger.info('amount_interest_reserve for tax of Revolving Pool {0} is {1}'.format(for_which_revolving_pool,amount_interest_reserve))
        
########################################################################        
        for fee_name in ['trustee']:
            #logger.info('amount_interest_reserve_calc_basis for trustee fee of Revolving Pool {0} is {1}'.format(for_which_revolving_pool,amount_total_issuance if for_which_revolving_pool==1 else self.AP_PAcc_outstanding[scenario_id][dates_recycle[for_which_revolving_pool - 2]]+self.RevolvingPool_PurchaseAmount[scenario_id][for_which_revolving_pool - 1]))
            amount_interest_reserve += self.reserve_for_fee(dates_pay[for_which_revolving_pool - 1],fee_name,
                                            amount_total_issuance if for_which_revolving_pool==1 else self.AP_PAcc_outstanding[scenario_id][dates_recycle[for_which_revolving_pool - 2]]+self.RevolvingPool_PurchaseAmount[scenario_id][for_which_revolving_pool - 1],
                                            scenario_id
                                            )
        #logger.info('amount_interest_reserve_calc_basis for custodian fee of Revolving Pool {0} is {1}'.format(for_which_revolving_pool,self.AP_PAcc_outstanding[scenario_id][dates_recycle[for_which_revolving_pool - 1]]))
        for fee_name in ['custodian']:
            amount_interest_reserve += self.reserve_for_fee(dates_pay[for_which_revolving_pool - 1],fee_name,
                                            self.AP_PAcc_outstanding[scenario_id][dates_recycle[for_which_revolving_pool - 1]],
                                            scenario_id
                                            )
            
        for fee_name in ['servicer']:
            amount_interest_reserve += self.reserve_for_fee(dates_pay[for_which_revolving_pool - 1],fee_name,
                                            amount_total_issuance if for_which_revolving_pool==1 else self.AP_PAcc_outstanding[scenario_id][dates_recycle[for_which_revolving_pool - 2]],
                                            scenario_id
                                            )
            
        for fee_name in ['A','B']:
            amount_interest_reserve += self.reserve_for_fee(dates_pay[for_which_revolving_pool - 1],fee_name,Bonds[fee_name]['amount'],scenario_id)
        
        #logger.info('amount_interest_reserve for all fee of Revolving Pool {0} is {1}'.format(for_which_revolving_pool,amount_interest_reserve))
        #logger.info('calc basis for Revolving Pool {0} is {1}'.format(for_which_revolving_pool,sum([self.AP_PAcc_original[scenario_id][k] for k in dates_recycle if dates_recycle.index(k) >= for_which_revolving_pool - 1])))
        
        self.AP_PAcc_pay[scenario_id][dates_recycle[for_which_revolving_pool - 1]] = amount_principal_reserve
        self.AP_PAcc_buy[scenario_id][dates_recycle[for_which_revolving_pool - 1]] = amount_principal - amount_principal_reserve
        
        self.AP_IAcc_pay[scenario_id][dates_recycle[for_which_revolving_pool - 1]] = amount_interest_reserve
        self.AP_IAcc_buy[scenario_id][dates_recycle[for_which_revolving_pool - 1]] = amount_interest - amount_interest_reserve
        
        return (amount_principal - amount_principal_reserve) + (amount_interest - amount_interest_reserve)

    def reserve_for_fee(self,date_pay,fee_name,basis,scenario_id):
        
        period_range = (fees[fee_name]['dates_to_calc'][dates_pay.index(date_pay)+1]  - fees[fee_name]['dates_to_calc'][dates_pay.index(date_pay)]).days     
        if (date_pay == dates_pay[0]) and (fee_name in ['trustee','custodian','servicer']): 
             period_range += 1   
        else:pass
        amt_reserve = basis * fees[fee_name]['rate'] * period_range / days_in_a_year
        return  amt_reserve   
    
    def update_rAP_acc(self,scenario_id,which_revolving_pool):
        
        logger.info('update_rAP_acc for revolving pool '+ str(which_revolving_pool) + '...')
        _AP_Acc = AssetPoolAccount(self.apcf_revolving[scenario_id][which_revolving_pool],self.apcf_revolving_adjusted[scenario_id][which_revolving_pool])
        _principal_available = _AP_Acc.available_principal()
        self.AP_PAcc_original_R[scenario_id][which_revolving_pool] = _principal_available[0]
        self.AP_PAcc_actual_R[scenario_id][which_revolving_pool] = _principal_available[1]                
        self.AP_PAcc_pay_R[scenario_id][which_revolving_pool] = _principal_available[2]
        self.AP_PAcc_buy_R[scenario_id][which_revolving_pool] = _principal_available[3]
        self.AP_PAcc_overdue_1_30_currentTerm_R[scenario_id][which_revolving_pool] = _principal_available[4]
        self.AP_PAcc_overdue_1_30_allTerm_R[scenario_id][which_revolving_pool] = _principal_available[5]
        self.AP_PAcc_overdue_31_60_currentTerm_R[scenario_id][which_revolving_pool] = _principal_available[6]
        self.AP_PAcc_overdue_31_60_allTerm_R[scenario_id][which_revolving_pool] = _principal_available[7]
        self.AP_PAcc_overdue_61_90_currentTerm_R[scenario_id][which_revolving_pool] = _principal_available[8]
        self.AP_PAcc_overdue_61_90_allTerm_R[scenario_id][which_revolving_pool] = _principal_available[9]
        self.AP_PAcc_loss_currentTerm_R[scenario_id][which_revolving_pool] = _principal_available[10]
        self.AP_PAcc_loss_allTerm_R[scenario_id][which_revolving_pool] = _principal_available[11]
        self.AP_PAcc_outstanding_R[scenario_id][which_revolving_pool] = _principal_available[12]
        
        _interest_available = _AP_Acc.available_interest()
        self.AP_IAcc_original_R[scenario_id][which_revolving_pool] = _interest_available[0]
        self.AP_IAcc_actual_R[scenario_id][which_revolving_pool] = _interest_available[1]                
        self.AP_IAcc_pay_R[scenario_id][which_revolving_pool] = _interest_available[2]
        self.AP_IAcc_buy_R[scenario_id][which_revolving_pool] = _interest_available[3]
        self.AP_IAcc_overdue_1_30_currentTerm_R[scenario_id][which_revolving_pool] = _interest_available[4]
        self.AP_IAcc_overdue_1_30_allTerm_R[scenario_id][which_revolving_pool] = _interest_available[5]
        self.AP_IAcc_overdue_31_60_currentTerm_R[scenario_id][which_revolving_pool] = _interest_available[6]
        self.AP_IAcc_overdue_31_60_allTerm_R[scenario_id][which_revolving_pool] = _interest_available[7]
        self.AP_IAcc_overdue_61_90_currentTerm_R[scenario_id][which_revolving_pool] = _interest_available[8]
        self.AP_IAcc_overdue_61_90_allTerm_R[scenario_id][which_revolving_pool] = _interest_available[9]
        self.AP_IAcc_loss_currentTerm_R[scenario_id][which_revolving_pool] = _interest_available[10]
        self.AP_IAcc_loss_allTerm_R[scenario_id][which_revolving_pool] = _interest_available[11]
        self.AP_IAcc_outstanding_R[scenario_id][which_revolving_pool] = _interest_available[12]
        
        #logger.info('self.AP_PAcc_actual_R[scenario_id][which_revolving_pool][k] for date {0} is {1}'.format(datetime.date(2018,8,31),self.AP_PAcc_actual_R[scenario_id][which_revolving_pool][datetime.date(2018,8,31)]))
        #TODO: Check why AP_PAcc_pay has all keys
        for k in dates_recycle:
            self.AP_PAcc_original[scenario_id][k] += self.AP_PAcc_original_R[scenario_id][which_revolving_pool][k]
            self.AP_PAcc_actual[scenario_id][k] += self.AP_PAcc_actual_R[scenario_id][which_revolving_pool][k]
            self.AP_PAcc_pay[scenario_id][k] += self.AP_PAcc_pay_R[scenario_id][which_revolving_pool][k]
            self.AP_PAcc_buy[scenario_id][k] += self.AP_PAcc_buy_R[scenario_id][which_revolving_pool][k]
            self.AP_PAcc_overdue_1_30_currentTerm[scenario_id][k] += self.AP_PAcc_overdue_1_30_currentTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_PAcc_overdue_1_30_allTerm[scenario_id][k] += self.AP_PAcc_overdue_1_30_allTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_PAcc_overdue_31_60_currentTerm[scenario_id][k] += self.AP_PAcc_overdue_31_60_currentTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_PAcc_overdue_31_60_allTerm[scenario_id][k] += self.AP_PAcc_overdue_31_60_allTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_PAcc_overdue_61_90_currentTerm[scenario_id][k] += self.AP_PAcc_overdue_61_90_currentTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_PAcc_overdue_61_90_allTerm[scenario_id][k] += self.AP_PAcc_overdue_61_90_allTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_PAcc_loss_currentTerm[scenario_id][k] += self.AP_PAcc_loss_currentTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_PAcc_loss_allTerm[scenario_id][k] += self.AP_PAcc_loss_allTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_PAcc_outstanding[scenario_id][k] += self.AP_PAcc_outstanding_R[scenario_id][which_revolving_pool][k]
            
            self.AP_PAcc_reserve[scenario_id][k] = amount_ReserveAcount

            self.AP_IAcc_original[scenario_id][k] += self.AP_IAcc_original_R[scenario_id][which_revolving_pool][k]                        
            self.AP_IAcc_actual[scenario_id][k] += self.AP_IAcc_actual_R[scenario_id][which_revolving_pool][k]
            self.AP_IAcc_pay[scenario_id][k] += self.AP_IAcc_pay_R[scenario_id][which_revolving_pool][k]
            self.AP_IAcc_buy[scenario_id][k] += self.AP_IAcc_buy_R[scenario_id][which_revolving_pool][k]
            self.AP_IAcc_overdue_1_30_currentTerm[scenario_id][k] += self.AP_IAcc_overdue_1_30_currentTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_IAcc_overdue_1_30_allTerm[scenario_id][k] += self.AP_IAcc_overdue_1_30_allTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_IAcc_overdue_31_60_currentTerm[scenario_id][k] += self.AP_IAcc_overdue_31_60_currentTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_IAcc_overdue_31_60_allTerm[scenario_id][k] += self.AP_IAcc_overdue_31_60_allTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_IAcc_overdue_61_90_currentTerm[scenario_id][k] += self.AP_IAcc_overdue_61_90_currentTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_IAcc_overdue_61_90_allTerm[scenario_id][k] += self.AP_IAcc_overdue_61_90_allTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_IAcc_loss_currentTerm[scenario_id][k] += self.AP_IAcc_loss_currentTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_IAcc_loss_allTerm[scenario_id][k] += self.AP_IAcc_loss_allTerm_R[scenario_id][which_revolving_pool][k]
            self.AP_IAcc_outstanding[scenario_id][k] += self.AP_IAcc_outstanding_R[scenario_id][which_revolving_pool][k]