# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 19:57:55 2018

@author: Jonah.Chen
"""
import sys
import os
from constant import wb_name,path_root,ProjectName
from copy import deepcopy
from Params import Redeem_or_Not,dt_param,amount_ReserveAcount,Batch_ID,POOL_CUT_PERIOD
import pandas as pd
import numpy as np
from abs_util.util_general import get_next_eom,save_to_excel,get_logger
from abs_util.util_cf import *
from dateutil.relativedelta import relativedelta
import datetime
from scipy.stats import bernoulli

logger = get_logger(__name__)

class APCF_adjuster():
    
    def __init__(self,scenarios,scenario_id,apcf_structure,df_ppmt,df_ipmt,dates_recycle_list,pool_cut_date,asset_status):
        
        self.asset_status = asset_status
        self.apcf_structure = apcf_structure
        self.df_ppmt,self.df_ipmt = df_ppmt,df_ipmt
        self.scenario_id = scenario_id
        self.scenario_params = scenarios[scenario_id]   
        self.dates_recycle_list = dates_recycle_list
        self.pool_cut_date = pool_cut_date
        
        self.APCF_adjusted_dict = {}
        
        self.principal_normal_currentTerm,self.interest_normal_currentTerm = {},{}
        self.principal_overdue_1_30_currentTerm,self.interest_overdue_1_30_currentTerm = {},{}        
        self.principal_overdue_31_60_currentTerm,self.interest_overdue_31_60_currentTerm = {},{}    
        self.principal_overdue_61_90_currentTerm,self.interest_overdue_61_90_currentTerm = {},{}    
        self.principal_loss_currentTerm,self.interest_loss_currentTerm = {},{}
        
        self.principal_normal_allTerm,self.interest_normal_allTerm = {},{}
        self.principal_overdue_1_30_allTerm,self.interest_overdue_1_30_allTerm = {},{}
        self.principal_overdue_31_60_allTerm,self.interest_overdue_31_60_allTerm = {},{}    
        self.principal_overdue_61_90_allTerm,self.interest_overdue_61_90_allTerm = {},{}  
        self.principal_loss_allTerm,self.interest_loss_allTerm = {},{}
        
        self.principal_normal_recycle,self.interest_normal_recycle = {},{}        
        self.principal_overdue_1_30_recycle,self.interest_overdue_1_30_recycle = {},{}
        self.principal_overdue_31_60_recycle,self.interest_overdue_31_60_recycle = {},{}
        self.principal_overdue_61_90_recycle,self.interest_overdue_61_90_recycle = {},{}
        self.principal_recovery_recycle,self.interest_recovery_recycle = {},{}
        
        self.principal_ER_recycle,self.interest_ER_recycle = {},{}
        
        self.principal_Redemption_recycle,self.interest_Redemption_recycle = {},{}
        self.principal_Redemption_currentTerm_helper,self.interest_Redemption_currentTerm_helper = {},{}
        
        self.principal_overdue_31_60_currentTerm_helper,self.interest_overdue_31_60_currentTerm_helper = {},{}
        self.principal_overdue_31_60_allTerm_helper,self.interest_overdue_31_60_allTerm_helper = {},{}
        
        self.principal_overdue_61_90_currentTerm_helper,self.interest_overdue_61_90_currentTerm_helper = {},{}
        self.principal_loss_currentTerm_helper,self.interest_loss_currentTerm_helper = {},{}
        
        self.Transition_principal_M1_2_M0,self.Transition_interest_M1_2_M0 = {},{}
        self.Transition_principal_M2_2_M0,self.Transition_interest_M2_2_M0 = {},{}
        self.Transition_principal_M3_2_M0,self.Transition_interest_M3_2_M0 = {},{}
    
        for date_r_index,date_r in enumerate(self.dates_recycle_list):
            
            self.principal_overdue_31_60_currentTerm[date_r],self.interest_overdue_31_60_currentTerm[date_r] = 0,0
            self.principal_overdue_61_90_currentTerm[date_r],self.interest_overdue_61_90_currentTerm[date_r] = 0,0
            self.principal_loss_currentTerm[date_r],self.interest_loss_currentTerm[date_r] = 0,0
            self.principal_overdue_31_60_allTerm[date_r],self.interest_overdue_31_60_allTerm[date_r] = 0,0
            self.principal_overdue_61_90_allTerm[date_r],self.interest_overdue_61_90_allTerm[date_r] = 0,0
            self.principal_loss_allTerm[date_r],self.interest_loss_allTerm[date_r] = 0,0
            
            self.principal_overdue_61_90_currentTerm_helper[date_r],self.interest_overdue_61_90_currentTerm_helper[date_r] = 0,0
            self.principal_loss_currentTerm_helper[date_r],self.interest_loss_currentTerm_helper[date_r] = 0,0
            
            self.principal_overdue_1_30_recycle[date_r],self.interest_overdue_1_30_recycle[date_r] = 0,0
            self.principal_overdue_31_60_recycle[date_r],self.interest_overdue_31_60_recycle[date_r] = 0,0
            self.principal_overdue_61_90_recycle[date_r],self.interest_overdue_61_90_recycle[date_r] = 0,0
            self.principal_ER_recycle[date_r],self.interest_ER_recycle[date_r] = 0,0
            self.principal_Redemption_recycle[date_r],self.interest_Redemption_recycle[date_r] = 0,0
            self.principal_Redemption_currentTerm_helper[date_r],self.interest_Redemption_currentTerm_helper[date_r] = 0,0
            self.principal_recovery_recycle[date_r],self.interest_recovery_recycle[date_r] = 0,0
            
            self.Transition_principal_M1_2_M0[date_r],self.Transition_interest_M1_2_M0[date_r] = pd.DataFrame(),pd.DataFrame()
            self.Transition_principal_M2_2_M0[date_r],self.Transition_interest_M2_2_M0[date_r] = pd.DataFrame(),pd.DataFrame()
            self.Transition_principal_M3_2_M0[date_r],self.Transition_interest_M3_2_M0[date_r] = pd.DataFrame(),pd.DataFrame()
        
    def adjust_APCF(self,OoR):
        logger.info('adjust_APCF for ' + OoR + '...')
        if OoR == 'O':
            logger.info('Redeem_or_Not is {0}'.format(Redeem_or_Not))
        df_ppmt,df_ipmt = deepcopy(self.df_ppmt),deepcopy(self.df_ipmt)
        dates_recycle_list = self.dates_recycle_list
        
        ppmt_M0,ipmt_M0 = df_ppmt,df_ipmt
        ppmt_M1,ipmt_M1 = pd.DataFrame(),pd.DataFrame() 
        
        ppmt_M1_2_M0,ipmt_M1_2_M0,ppmt_M1_2_M2,ipmt_M1_2_M2 = pd.DataFrame(),pd.DataFrame(),pd.DataFrame(),pd.DataFrame()      
        ppmt_M2_2_M0,ipmt_M2_2_M0,ppmt_M2_2_M3,ipmt_M2_2_M3 = pd.DataFrame(),pd.DataFrame(),pd.DataFrame(),pd.DataFrame()    
        ppmt_M3_2_M0,ipmt_M3_2_M0,ppmt_M3_2_D,ipmt_M3_2_D = pd.DataFrame(),pd.DataFrame(),pd.DataFrame(),pd.DataFrame()

#####################################################################################################################
        for date_r_index,date_r in enumerate(dates_recycle_list):
            #logger.info('Adjusting for date_r {0}'.format(date_r)) 
            if date_r_index>0:
                _ppmt_M1_2_M0 = self.Transition_principal_M1_2_M0[dates_recycle_list[date_r_index-1]]
                _ipmt_M1_2_M0 = self.Transition_interest_M1_2_M0[dates_recycle_list[date_r_index-1]]
                self.principal_overdue_1_30_recycle[dates_recycle_list[date_r_index]] = _ppmt_M1_2_M0[date_r].sum() + _ppmt_M1_2_M0[dates_recycle_list[date_r_index-1]].sum()
                self.interest_overdue_1_30_recycle[dates_recycle_list[date_r_index]] = _ipmt_M1_2_M0[date_r].sum() + _ipmt_M1_2_M0[dates_recycle_list[date_r_index-1]].sum()
                _ppmt_M1_2_M0[date_r],_ppmt_M1_2_M0[dates_recycle_list[date_r_index-1]] = 0,0
                _ipmt_M1_2_M0[date_r],_ipmt_M1_2_M0[dates_recycle_list[date_r_index-1]] = 0,0
            if date_r_index>1:
                _ppmt_M2_2_M0 = self.Transition_principal_M2_2_M0[dates_recycle_list[date_r_index-2]]
                _ipmt_M2_2_M0 = self.Transition_interest_M2_2_M0[dates_recycle_list[date_r_index-2]]
                self.principal_overdue_31_60_recycle[dates_recycle_list[date_r_index]] = _ppmt_M2_2_M0[date_r].sum() + _ppmt_M2_2_M0[dates_recycle_list[date_r_index-1]].sum() + _ppmt_M2_2_M0[dates_recycle_list[date_r_index-2]].sum()
                self.interest_overdue_31_60_recycle[dates_recycle_list[date_r_index]] = _ipmt_M2_2_M0[date_r].sum() + _ipmt_M2_2_M0[dates_recycle_list[date_r_index-1]].sum() + _ipmt_M2_2_M0[dates_recycle_list[date_r_index-2]].sum()                                                        
                _ppmt_M2_2_M0[date_r],_ppmt_M2_2_M0[dates_recycle_list[date_r_index-1]],_ppmt_M2_2_M0[dates_recycle_list[date_r_index-2]] = 0,0,0
                _ipmt_M2_2_M0[date_r],_ipmt_M2_2_M0[dates_recycle_list[date_r_index-1]],_ipmt_M2_2_M0[dates_recycle_list[date_r_index-2]] = 0,0,0
            if date_r_index>2:    
                _ppmt_M3_2_M0 = self.Transition_principal_M3_2_M0[dates_recycle_list[date_r_index-3]]
                _ipmt_M3_2_M0 = self.Transition_interest_M3_2_M0[dates_recycle_list[date_r_index-3]]
                self.principal_overdue_61_90_recycle[dates_recycle_list[date_r_index]] = _ppmt_M3_2_M0[date_r].sum() + _ppmt_M3_2_M0[dates_recycle_list[date_r_index-1]].sum() + _ppmt_M3_2_M0[dates_recycle_list[date_r_index-2]].sum() + _ppmt_M3_2_M0[dates_recycle_list[date_r_index-3]].sum()
                self.interest_overdue_61_90_recycle[dates_recycle_list[date_r_index]] = _ipmt_M3_2_M0[date_r].sum() + _ipmt_M3_2_M0[dates_recycle_list[date_r_index-1]].sum() + _ipmt_M3_2_M0[dates_recycle_list[date_r_index-2]].sum() + _ipmt_M3_2_M0[dates_recycle_list[date_r_index-3]].sum()
                _ppmt_M3_2_M0[date_r],_ppmt_M3_2_M0[dates_recycle_list[date_r_index-1]],_ppmt_M3_2_M0[dates_recycle_list[date_r_index-2]],_ppmt_M3_2_M0[dates_recycle_list[date_r_index-3]] = 0,0,0,0
                _ipmt_M3_2_M0[date_r],_ipmt_M3_2_M0[dates_recycle_list[date_r_index-1]],_ipmt_M3_2_M0[dates_recycle_list[date_r_index-2]],_ipmt_M3_2_M0[dates_recycle_list[date_r_index-3]] = 0,0,0,0

            if OoR == 'O' and date_r_index == 0:
                ppmt_M0.to_csv(path_root  + '/DataSource/' +ProjectName+'/' + 'ppmt_M0_pre.csv')
                
            ppmt_M0,ipmt_M0,ppmt_M1,ipmt_M1 = self.transit_Status(ppmt_M0,ipmt_M0,OoR,date_r_index,'M0_2_M1','Overdue')
            
            if OoR == 'O' and date_r_index == 0:
                ppmt_M0.to_csv(path_root  + '/DataSource/' +ProjectName+'/' + 'ppmt_M0_post.csv')
                ppmt_M1.to_csv(path_root  + '/DataSource/' +ProjectName+'/' + 'ppmt_M1.csv')
            
            if date_r_index > 2:
                ppmt_M0 = ppmt_M0.append(_ppmt_M1_2_M0).append(_ppmt_M2_2_M0).append(_ppmt_M3_2_M0,ignore_index=True)
                ipmt_M0 = ipmt_M0.append(_ipmt_M1_2_M0).append(_ipmt_M2_2_M0).append(_ipmt_M3_2_M0,ignore_index=True)
            elif date_r_index > 1:
                ppmt_M0 = ppmt_M0.append(_ppmt_M1_2_M0).append(_ppmt_M2_2_M0,ignore_index=True)
                ipmt_M0 = ipmt_M0.append(_ipmt_M1_2_M0).append(_ipmt_M2_2_M0,ignore_index=True)
            elif date_r_index > 0:
                ppmt_M0 = ppmt_M0.append(_ppmt_M1_2_M0,ignore_index=True)
                ipmt_M0 = ipmt_M0.append(_ipmt_M1_2_M0,ignore_index=True)
            else:pass
            
            #ER
            ppmt_M0_ER,ipmt_M0_ER,ppmt_M0,ipmt_M0 = self.transit_Status(ppmt_M0,ipmt_M0,OoR,date_r_index,'M0_2_ERM0','ER')
            
            self.principal_ER_recycle[date_r] = sum(ppmt_M0_ER[dates_recycle_list[date_r_index:]].sum())
            self.interest_ER_recycle[date_r] = sum(ipmt_M0_ER[dates_recycle_list[date_r_index:]].sum())
            
            self.principal_normal_currentTerm[date_r] = ppmt_M0[date_r].sum()
            self.interest_normal_currentTerm[date_r] = ipmt_M0[date_r].sum()   
            self.principal_normal_allTerm[date_r] = sum(ppmt_M0[dates_recycle_list[date_r_index+1:]].sum())
            self.interest_normal_allTerm[date_r] = sum(ipmt_M0[dates_recycle_list[date_r_index+1:]].sum())
            
            self.principal_normal_recycle[date_r],self.interest_normal_recycle[date_r] = ppmt_M0[date_r].sum(), ipmt_M0[date_r].sum() 
            
            self.principal_overdue_1_30_currentTerm[date_r] = ppmt_M1[date_r].sum()
            self.interest_overdue_1_30_currentTerm[date_r] = ipmt_M1[date_r].sum()            
            self.principal_overdue_1_30_allTerm[date_r] = sum(ppmt_M1[dates_recycle_list[date_r_index:]].sum())
            self.interest_overdue_1_30_allTerm[date_r] = sum(ipmt_M1[dates_recycle_list[date_r_index:]].sum())
            
            ppmt_M1_2_M0,ipmt_M1_2_M0,ppmt_M1_2_M2,ipmt_M1_2_M2 = self.transit_Status(ppmt_M1,ipmt_M1,OoR,date_r_index,'M1_2_M0M2','Overdue')#self.M1_2_M0M2(ppmt_M1,ipmt_M1)
            #Transition M1_2_M0M2
            if  Redeem_or_Not == True :
                if date_r_index == POOL_CUT_PERIOD-1 and OoR == 'O' :#and POOL_CUT_PERIOD-date_r_index>=0 : CAPTURE M2 on first calculation date
                    # Capture assets whcih will become M2 before dt_trust_effective
                    self.principal_Redemption_recycle[dates_recycle_list[date_r_index+1]] += sum(ppmt_M1_2_M2[ppmt_M1_2_M2['PayDay']<dt_param['dt_trust_effective'].day][dates_recycle_list[date_r_index:]].sum())
                    self.interest_Redemption_recycle[dates_recycle_list[date_r_index+1]] += sum(ipmt_M1_2_M2[ipmt_M1_2_M2['PayDay']<dt_param['dt_trust_effective'].day][dates_recycle_list[date_r_index:]].sum())          
                    #logger.info('self.principal_Redemption_recycle part 3 is {0} :'.format(sum(ppmt_M1_2_M2[ppmt_M1_2_M2['PayDay']<dt_param['dt_trust_effective'].day][dates_recycle_list[date_r_index:]].sum())))
                    logger.info('self.principal_Redemption_recycle total is {0:,.2f} :'.format(self.principal_Redemption_recycle[dates_recycle_list[date_r_index+1]]))
                    # Ignore assets which will become M2 after dt_trust_effective
                    ppmt_M1_2_M2,ipmt_M1_2_M2 = deepcopy(ppmt_M1_2_M2[ppmt_M1_2_M2['PayDay']>=dt_param['dt_trust_effective'].day]),deepcopy(ipmt_M1_2_M2[ipmt_M1_2_M2['PayDay']>=dt_param['dt_trust_effective'].day])
                    #Restore the un-captured ppmt_M1_2_M2
                    self.cal_overdue_31_60(date_r_index,ppmt_M1_2_M2,ipmt_M1_2_M2)
                    #save_to_excel(ppmt_M1_2_M2,'post_Redeem_part_3',wb_name)
                else: self.cal_overdue_31_60(date_r_index,ppmt_M1_2_M2,ipmt_M1_2_M2)
            else:self.cal_overdue_31_60(date_r_index,ppmt_M1_2_M2,ipmt_M1_2_M2)
                    
            #logger.info('Transition M2_2_M0M3...')
            ppmt_M2_2_M0,ipmt_M2_2_M0,ppmt_M2_2_M3,ipmt_M2_2_M3 = self.transit_Status(ppmt_M1_2_M2,ipmt_M1_2_M2,OoR,date_r_index,'M2_2_M0M3','Overdue')
            #Transition M2_2_M0M3
            if  Redeem_or_Not == True :
                if date_r_index == POOL_CUT_PERIOD-2 and OoR == 'O':# and POOL_CUT_PERIOD-date_r_index>=0 :CAPTURE M3 on first calculation date
                    self.principal_Redemption_recycle[dates_recycle_list[date_r_index+2]] += sum(ppmt_M2_2_M3[dates_recycle_list[date_r_index:]].sum())
                    self.interest_Redemption_recycle[dates_recycle_list[date_r_index+2]] += sum(ipmt_M2_2_M3[dates_recycle_list[date_r_index:]].sum())          
                    #save_to_excel(ppmt_M2_2_M3,'Redeem_part_2',wb_name)
                    #logger.info('self.principal_Redemption_recycle part 2 is {0} :'.format(sum(ppmt_M2_2_M3[dates_recycle_list[date_r_index:]].sum())))
                    ppmt_M2_2_M3,ipmt_M2_2_M3 = ppmt_M2_2_M3[0:0],ipmt_M2_2_M3[0:0]
                else: self.cal_overdue_61_90(date_r_index,ppmt_M2_2_M3,ipmt_M2_2_M3)
            else:self.cal_overdue_61_90(date_r_index,ppmt_M2_2_M3,ipmt_M2_2_M3)
            
            #logger.info('Transition M3_2_M0L...')
            ppmt_M3_2_M0,ipmt_M3_2_M0,ppmt_M3_2_D,ipmt_M3_2_D = self.transit_Status(ppmt_M2_2_M3,ipmt_M2_2_M3,OoR,date_r_index,'M3_2_M0D','Overdue')     
            #Transition M3_2_M0L
            if  Redeem_or_Not == True :
                if date_r_index == POOL_CUT_PERIOD-3 and OoR == 'O':# and POOL_CUT_PERIOD-date_r_index>=0  :CAPTURE ML on first calculation date
                    self.principal_Redemption_recycle[dates_recycle_list[date_r_index+3]] = sum(ppmt_M3_2_D[dates_recycle_list[date_r_index:]].sum())
                    self.interest_Redemption_recycle[dates_recycle_list[date_r_index+3]] = sum(ipmt_M3_2_D[dates_recycle_list[date_r_index:]].sum())  
                    ppmt_M3_2_D,ipmt_M3_2_D = ppmt_M3_2_D[0:0],ipmt_M3_2_D[0:0]
                elif date_r_index == POOL_CUT_PERIOD-4 and OoR == 'O':
                    self.principal_Redemption_recycle[dates_recycle_list[date_r_index+4]] = sum(ppmt_M3_2_D[dates_recycle_list[date_r_index:]].sum())
                    self.interest_Redemption_recycle[dates_recycle_list[date_r_index+4]] = sum(ipmt_M3_2_D[dates_recycle_list[date_r_index:]].sum())  
                    ppmt_M3_2_D,ipmt_M3_2_D = ppmt_M3_2_D[0:0],ipmt_M3_2_D[0:0]
                else: self.cal_loss(OoR,date_r_index,ppmt_M3_2_D,ipmt_M3_2_D)
            else: self.cal_loss(OoR,date_r_index,ppmt_M3_2_D,ipmt_M3_2_D)
                
            self.Transition_principal_M1_2_M0[date_r],self.Transition_interest_M1_2_M0[date_r] = deepcopy(ppmt_M1_2_M0),deepcopy(ipmt_M1_2_M0)
            self.Transition_principal_M2_2_M0[date_r],self.Transition_interest_M2_2_M0[date_r] = deepcopy(ppmt_M2_2_M0),deepcopy(ipmt_M2_2_M0)
            self.Transition_principal_M3_2_M0[date_r],self.Transition_interest_M3_2_M0[date_r] = deepcopy(ppmt_M3_2_M0),deepcopy(ipmt_M3_2_M0)

            #logger.info('Generating APCF_adjusted_dict for date_r {0} '.format(date_r))
            self.APCF_adjusted_dict[date_r] = [
                                          self.principal_normal_recycle[date_r],self.interest_normal_recycle[date_r],
                                          
                                          self.principal_overdue_1_30_currentTerm[date_r],self.interest_overdue_1_30_currentTerm[date_r],  
                                          self.principal_overdue_31_60_currentTerm[date_r],self.interest_overdue_31_60_currentTerm[date_r],
                                          self.principal_overdue_61_90_currentTerm[date_r],self.interest_overdue_61_90_currentTerm[date_r],
                                          self.principal_loss_currentTerm[date_r],self.interest_loss_currentTerm[date_r],
                                          
                                          self.principal_overdue_1_30_allTerm[date_r],self.interest_overdue_1_30_allTerm[date_r],
                                          self.principal_overdue_31_60_allTerm[date_r],self.interest_overdue_31_60_allTerm[date_r],
                                          self.principal_overdue_61_90_allTerm[date_r],self.interest_overdue_61_90_allTerm[date_r],
                                          self.principal_loss_allTerm[date_r],self.interest_loss_allTerm[date_r],
                                          
                                          self.principal_overdue_1_30_recycle[date_r],self.interest_overdue_1_30_recycle[date_r],
                                          self.principal_overdue_31_60_recycle[date_r],self.interest_overdue_31_60_recycle[date_r],
                                          self.principal_overdue_61_90_recycle[date_r],self.interest_overdue_61_90_recycle[date_r],
                                          self.principal_ER_recycle[date_r],self.interest_ER_recycle[date_r],     
                                          self.principal_Redemption_recycle[date_r],self.interest_Redemption_recycle[date_r],
                                          self.principal_recovery_recycle[date_r],self.interest_recovery_recycle[date_r],
                                          
                                          self.principal_normal_allTerm[date_r],self.interest_normal_allTerm[date_r],
                                          self.principal_normal_currentTerm[date_r],self.interest_normal_currentTerm[date_r],
                                          ]
        
        #logger.info('Saving APCF_adjusted_structure for scenario {0}: '.format(self.scenario_id))
        #save_to_excel(APCF_adjusted_structure,'APCF_adjusted_structure_simulation',wb_name)
        
        return self.gen_APCF_adjusted(OoR)
   
    def transit_Status(self,ppmt_this,ipmt_this,OoR,date_r_index,transition,FLAG):
        #logger.info('Transition'+transition +'...')
        transit_down = deepcopy(self.scenario_params[transition])
        #logger.info('date_r_index is {0},transit_down is {1}'.format(date_r_index,transit_down))
        
        transit_down = self.calc_transit_down(transit_down,transition,date_r_index)
        
        if transition == 'M0_2_M1' and OoR == 'O' and date_r_index == 0:
            logger.info('date_r_index is {0},transit_down is {1}'.format(date_r_index,transit_down))
        
        first_due_period = 'first_due_period_'+OoR
        
        ppmt_this,ipmt_this = ppmt_this.reset_index(drop=True),ipmt_this.reset_index(drop=True)
        
        ppmt_this[FLAG + '_'+str(date_r_index)] = pd.DataFrame(deepcopy(list(bernoulli.rvs(size=len(ppmt_this),p= (1-transit_down)))),columns=['bernollio_col'])            
        
        if transition == 'M0_2_M1' and OoR == 'O' and date_r_index == 0:
            logger.info('counts of ppmt_this_pre is {0}'.format(ppmt_this[FLAG + '_'+str(date_r_index)].count()))
            logger.info('date_r_index is {0},sum of bernollio_col is {1}'.format(date_r_index,ppmt_this[FLAG + '_'+str(date_r_index)].sum()))
        
        if FLAG == 'Overdue':# and transition != 'D_2_RL':   
            ppmt_this[FLAG + '_'+str(date_r_index)] = ppmt_this[FLAG + '_'+str(date_r_index)].where(ppmt_this[first_due_period] <= date_r_index,1)
        
        ipmt_this[FLAG + '_'+str(date_r_index)] = ppmt_this[FLAG + '_'+str(date_r_index)]
        
        # 0 indicates dead ( overdue ), 1 indicates alive ( normal ) 
        ppmt_pre,ipmt_pre = ppmt_this[ppmt_this[FLAG + '_'+str(date_r_index)]==1],ipmt_this[ipmt_this[FLAG + '_'+str(date_r_index)]==1]
        ppmt_next,ipmt_next = ppmt_this[ppmt_this[FLAG + '_'+str(date_r_index)]==0],ipmt_this[ipmt_this[FLAG + '_'+str(date_r_index)]==0]
        
        ppmt_pre,ipmt_pre = ppmt_pre.reset_index(drop=True),ipmt_pre.reset_index(drop=True)
        ppmt_next,ipmt_next = ppmt_next.reset_index(drop=True),ipmt_next.reset_index(drop=True)

        return ppmt_pre,ipmt_pre,ppmt_next,ipmt_next      
    
    def calc_transit_down(self,transit_down,transition,date_r_index):    
        # First month after POOLCUT
        if self.asset_status == '拖欠1-30天贷款':
            if date_r_index > 0:pass
            else: 
                if transition in ['M0_2_M1','M0_2_ERM0']: transit_down = 1
                else: pass
        elif self.asset_status == '拖欠31-60天贷款':
            if date_r_index > 1:pass
            else: 
                if transition in ['M0_2_M1','M0_2_ERM0','M1_2_M0M2']: transit_down = 1
                else: pass
        elif self.asset_status == '拖欠61-90天贷款':
            if date_r_index > 2:pass
            else: 
                if transition in ['M0_2_M1','M0_2_ERM0','M1_2_M0M2','M2_2_M0M3']: transit_down = 1
                else: pass
        elif self.asset_status == '拖欠90天以上贷款':
            if date_r_index > 3:pass
            else: 
                if transition in ['M0_2_M1','M0_2_ERM0','M1_2_M0M2','M2_2_M0M3','M3_2_M0D','D_2_RL']: transit_down = 1
                else: pass
        elif self.asset_status == '正常贷款' : pass
#            if date_r_index > 0:pass
#            else: 
#                if transition == 'M0_2_M1':transit_down *= ((get_next_eom(self.pool_cut_date,0)-self.pool_cut_date).days+1) / get_next_eom(self.pool_cut_date,0).day
#                elif transition == 'M0_2_ERM0':transit_down = 1 - (1-transit_down)*((get_next_eom(self.pool_cut_date,0)-self.pool_cut_date).days+1) / get_next_eom(self.pool_cut_date,0).day
        #logger.info('transit_down is {0} for dates_recycle_list[date_r_index] {1} for M0_2_M1 '.format(transit_down,self.dates_recycle_list[date_r_index]))
        
        return transit_down
        
        
    def gen_APCF_adjusted(self,OoR):
        #logger.info('Generating APCF_adjusted...' )
        df_total_by_date = pd.DataFrame(self.APCF_adjusted_dict)
        APCF_adjusted = pd.DataFrame({'date_recycle': self.dates_recycle_list,
                                         'Normal_recycle_principal': df_total_by_date.transpose()[0],'Normal_recycle_interest': df_total_by_date.transpose()[1],
                                         'Overdue_1_30_recycle_principal': df_total_by_date.transpose()[18],'Overdue_1_30_recycle_interest': df_total_by_date.transpose()[19],
                                         'Overdue_31_60_recycle_principal': df_total_by_date.transpose()[20],'Overdue_31_60_recycle_interest': df_total_by_date.transpose()[21],
                                         'Overdue_61_90_recycle_principal': df_total_by_date.transpose()[22],'Overdue_61_90_recycle_interest': df_total_by_date.transpose()[23],
                                         'ER_recycle_principal': df_total_by_date.transpose()[24],'ER_recycle_interest': df_total_by_date.transpose()[25], 
                                         'Redemption_recycle_principal': df_total_by_date.transpose()[26],'Redemption_recycle_interest': df_total_by_date.transpose()[27],  
                                         'Recovery_recycle_principal': df_total_by_date.transpose()[28],'Recovery_recycle_interest': df_total_by_date.transpose()[29],  
                                         
                                         'principal_overdue_1_30_currentTerm': df_total_by_date.transpose()[2],'interest_overdue_1_30_currentTerm': df_total_by_date.transpose()[3],
                                         'principal_overdue_31_60_currentTerm': df_total_by_date.transpose()[4],'interest_overdue_31_60_currentTerm': df_total_by_date.transpose()[5],
                                         'principal_overdue_61_90_currentTerm': df_total_by_date.transpose()[6],'interest_overdue_61_90_currentTerm': df_total_by_date.transpose()[7],
                                         'principal_loss_currentTerm': df_total_by_date.transpose()[8],'interest_loss_currentTerm': df_total_by_date.transpose()[9],
                                         'principal_overdue_1_30_allTerm': df_total_by_date.transpose()[10],'interest_overdue_1_30_allTerm': df_total_by_date.transpose()[11],
                                         'principal_overdue_31_60_allTerm': df_total_by_date.transpose()[12],'interest_overdue_31_60_allTerm': df_total_by_date.transpose()[13],
                                         'principal_overdue_61_90_allTerm': df_total_by_date.transpose()[14],'interest_overdue_61_90_allTerm': df_total_by_date.transpose()[15],
                                         'principal_loss_allTerm': df_total_by_date.transpose()[16],'interest_loss_allTerm': df_total_by_date.transpose()[17],

                                         'principal_normal_allTerm': df_total_by_date.transpose()[30],'interest_normal_allTerm': df_total_by_date.transpose()[31],
                                         })
    
        APCF_adjusted['total_recycle_principal'] = APCF_adjusted[['ER_recycle_principal','Normal_recycle_principal','Redemption_recycle_principal','Overdue_1_30_recycle_principal','Overdue_31_60_recycle_principal','Overdue_61_90_recycle_principal','Recovery_recycle_principal']].sum(axis=1)
        APCF_adjusted['total_recycle_interest'] = APCF_adjusted[['ER_recycle_interest','Normal_recycle_interest','Redemption_recycle_interest','Overdue_1_30_recycle_interest','Overdue_31_60_recycle_interest','Overdue_61_90_recycle_interest','Recovery_recycle_interest']].sum(axis=1)
       
        APCF_adjusted['total_outstanding_principal'] = APCF_adjusted[['principal_overdue_1_30_allTerm','principal_overdue_31_60_allTerm','principal_overdue_61_90_allTerm','principal_loss_allTerm','principal_normal_allTerm']].sum(axis=1)
        APCF_adjusted['total_outstanding_interest'] = APCF_adjusted[['interest_overdue_1_30_allTerm','interest_overdue_31_60_allTerm','interest_overdue_61_90_allTerm','interest_loss_allTerm','interest_normal_allTerm']].sum(axis=1)
        APCF_adjusted['ReserveAccount'] = amount_ReserveAcount
        
        
        APCF_adjusted_save = APCF_adjusted[['date_recycle','total_recycle_principal',
                                            'Normal_recycle_principal','ER_recycle_principal','Redemption_recycle_principal','Recovery_recycle_principal',
                                            'Overdue_1_30_recycle_principal','Overdue_31_60_recycle_principal','Overdue_61_90_recycle_principal',
                                            'principal_overdue_1_30_currentTerm','principal_overdue_31_60_currentTerm','principal_overdue_61_90_currentTerm','principal_loss_currentTerm',
                                            'principal_overdue_1_30_allTerm','principal_overdue_31_60_allTerm','principal_overdue_61_90_allTerm','principal_loss_allTerm',
                                            'principal_normal_allTerm']]
        
        try:APCF_adjusted_save['Check_Principal'] = APCF_adjusted_save['total_recycle_principal'].cumsum() + APCF_adjusted_save[['principal_overdue_1_30_allTerm','principal_overdue_31_60_allTerm','principal_overdue_61_90_allTerm','principal_loss_allTerm','principal_normal_allTerm']].sum(axis=1) - self.apcf_structure['OutstandingPrincipal'].sum()
        except(KeyError):  APCF_adjusted_save['Check_Principal'] = APCF_adjusted_save['total_recycle_principal'].cumsum() + APCF_adjusted_save[['principal_overdue_1_30_allTerm','principal_overdue_31_60_allTerm','principal_overdue_61_90_allTerm','principal_loss_allTerm','principal_normal_allTerm']].sum(axis=1) - self.apcf_structure['principal'].sum()

        if abs(APCF_adjusted_save['Check_Principal'].sum()) > 0.01:
            logger.info('!!!!!!!!! Principal GAP in Pool !!!!!!!!!'+OoR)
        else: pass #logger.info('Principal Check Passed for '+OoR)
        
        return APCF_adjusted[['date_recycle',
                              'total_recycle_principal','total_recycle_interest',
                              'principal_overdue_1_30_currentTerm','interest_overdue_1_30_currentTerm','principal_overdue_31_60_currentTerm','interest_overdue_31_60_currentTerm',
                              'principal_overdue_61_90_currentTerm','interest_overdue_61_90_currentTerm','principal_loss_currentTerm','interest_loss_currentTerm',
                              'principal_overdue_1_30_allTerm','interest_overdue_1_30_allTerm','principal_overdue_31_60_allTerm','interest_overdue_31_60_allTerm',
                              'principal_overdue_61_90_allTerm','interest_overdue_61_90_allTerm','principal_loss_allTerm','interest_loss_allTerm',
                              'total_outstanding_principal','total_outstanding_interest','ReserveAccount'
                              ]],APCF_adjusted_save
        
    def cal_overdue_31_60(self,date_r_index,ppmt_MM,ipmt_MM):
        #logger.info('len(ppmt_M1_2_M0) is {0},len(ipmt_M1_2_M0) is {1}'.format(len(ppmt_M1_2_M0),len(ipmt_M1_2_M0)))
        if date_r_index >= len(self.dates_recycle_list)-1:pass
        else:
            dates_recycle_list = self.dates_recycle_list
            ppmt_M1_2_M2,ipmt_M1_2_M2 = ppmt_MM,ipmt_MM
            
            for k in self.dates_recycle_list:
                self.principal_overdue_31_60_currentTerm_helper[k] = 0
                self.interest_overdue_31_60_currentTerm_helper[k] = 0
            for overdue_date in dates_recycle_list[date_r_index:]:
                self.principal_overdue_31_60_currentTerm_helper[overdue_date] = ppmt_M1_2_M2[overdue_date].sum()
                self.interest_overdue_31_60_currentTerm_helper[overdue_date] = ipmt_M1_2_M2[overdue_date].sum()
            self.principal_overdue_31_60_currentTerm[dates_recycle_list[date_r_index+1]] = self.principal_overdue_31_60_currentTerm_helper[dates_recycle_list[date_r_index]]+self.principal_overdue_31_60_currentTerm_helper[dates_recycle_list[date_r_index+1]]
            self.interest_overdue_31_60_currentTerm[dates_recycle_list[date_r_index+1]] = self.interest_overdue_31_60_currentTerm_helper[dates_recycle_list[date_r_index]]+self.interest_overdue_31_60_currentTerm_helper[dates_recycle_list[date_r_index+1]]
            self.principal_overdue_31_60_allTerm[dates_recycle_list[date_r_index+1]] = sum(ppmt_M1_2_M2[dates_recycle_list[date_r_index:]].sum())
            self.interest_overdue_31_60_allTerm[dates_recycle_list[date_r_index+1]] = sum(ipmt_M1_2_M2[dates_recycle_list[date_r_index:]].sum())

    def cal_overdue_61_90(self,date_r_index,ppmt_MM,ipmt_MM):
        #logger.info('len(ppmt_M2_2_M0) is {0},len(ipmt_M2_2_M0) is {1}'.format(len(ppmt_M2_2_M0),len(ipmt_M2_2_M0)))
        if date_r_index >= len(self.dates_recycle_list)-2:pass
        else:
            dates_recycle_list = self.dates_recycle_list
            ppmt_M2_2_M3,ipmt_M2_2_M3 = ppmt_MM,ipmt_MM
            
            for k in self.dates_recycle_list:
                self.principal_overdue_61_90_currentTerm_helper[k] = 0
                self.interest_overdue_61_90_currentTerm_helper[k] = 0
            for overdue_date in dates_recycle_list[date_r_index:]:
                self.principal_overdue_61_90_currentTerm_helper[overdue_date] = ppmt_M2_2_M3[overdue_date].sum()
                self.interest_overdue_61_90_currentTerm_helper[overdue_date] = ipmt_M2_2_M3[overdue_date].sum()
            self.principal_overdue_61_90_currentTerm[dates_recycle_list[date_r_index+2]] = sum(self.principal_overdue_61_90_currentTerm_helper[overdue_date] for overdue_date in dates_recycle_list[date_r_index:date_r_index+2])+self.principal_overdue_61_90_currentTerm_helper[dates_recycle_list[date_r_index+2]]
            self.interest_overdue_61_90_currentTerm[dates_recycle_list[date_r_index+2]] = sum(self.interest_overdue_61_90_currentTerm_helper[overdue_date] for overdue_date in dates_recycle_list[date_r_index:date_r_index+2])+self.interest_overdue_61_90_currentTerm_helper[dates_recycle_list[date_r_index+2]]
            self.principal_overdue_61_90_allTerm[dates_recycle_list[date_r_index+2]] = sum(ppmt_M2_2_M3[dates_recycle_list[date_r_index:]].sum())
            self.interest_overdue_61_90_allTerm[dates_recycle_list[date_r_index+2]] = sum(ipmt_M2_2_M3[dates_recycle_list[date_r_index:]].sum())
  
    def cal_loss(self,OoR,date_r_index,ppmt_MM,ipmt_MM):
        #logger.info('len(ppmt_M3_2_D) is {0},len(ipmt_M3_2_D) is {1}'.format(len(ppmt_M3_2_D),len(ipmt_M3_2_D)))
        if date_r_index >= len(self.dates_recycle_list)-3:pass
        else:
            dates_recycle_list = self.dates_recycle_list
            ppmt_M3_2_D,ipmt_M3_2_D = ppmt_MM,ipmt_MM
            
            ppmt_D_2_R,ipmt_D_2_R,ppmt_D_2_L,ipmt_D_2_L = self.transit_Status(ppmt_M3_2_D,ipmt_M3_2_D,OoR,date_r_index,'D_2_RL','Overdue')  
    
            # Recovery
            self.principal_recovery_recycle[dates_recycle_list[date_r_index+3]] = sum(ppmt_D_2_R[dates_recycle_list[date_r_index:]].sum())
            self.interest_recovery_recycle[dates_recycle_list[date_r_index+3]] = sum(ipmt_D_2_R[dates_recycle_list[date_r_index:]].sum())  
            
            # Loss
            for overdue_date in dates_recycle_list[date_r_index:]:
                self.principal_loss_currentTerm_helper[overdue_date] += ppmt_D_2_L[overdue_date].sum()
                self.interest_loss_currentTerm_helper[overdue_date] += ipmt_D_2_L[overdue_date].sum()
            self.principal_loss_currentTerm[dates_recycle_list[date_r_index+3]] = sum(self.principal_loss_currentTerm_helper[overdue_date] for overdue_date in dates_recycle_list[0:date_r_index+3])+self.principal_loss_currentTerm_helper[dates_recycle_list[date_r_index+3]]
            self.interest_loss_currentTerm[dates_recycle_list[date_r_index+3]] = sum(self.interest_loss_currentTerm_helper[overdue_date] for overdue_date in dates_recycle_list[0:date_r_index+3])+self.interest_loss_currentTerm_helper[dates_recycle_list[date_r_index+3]]
            self.principal_loss_allTerm[dates_recycle_list[date_r_index+3]] = self.principal_loss_allTerm[dates_recycle_list[date_r_index+2]] + sum(ppmt_D_2_L[dates_recycle_list[date_r_index:]].sum())
            self.interest_loss_allTerm[dates_recycle_list[date_r_index+3]] = self.interest_loss_allTerm[dates_recycle_list[date_r_index+2]] + sum(ipmt_D_2_L[dates_recycle_list[date_r_index:]].sum())          