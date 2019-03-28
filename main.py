# -*- coding: utf-8 -*-
'''
Spyder Editor

This is a temporary script file.
'''
import sys
sys.path.append("..")
import os
from copy import deepcopy
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import datetime
from constant import *
from Params import *
from abs_util.util_general import *
from abs_util.util_waterfall import run_Accounts,BasicInfo_calculator,CR_calculator,NPV_calculator
from Deal import Deal
from RevolvingDeal import RevolvingDeal
from APCF_adjuster import APCF_adjuster
from Statistics import Statistics
from ReverseSelection import ReverseSelection
from AssetsCashFlow import AssetsCashFlow
from ServiceReport import ServiceReport

logger = get_logger(__name__)

def main(): 
    
    start_time = datetime.datetime.now()
#
    if os.path.isfile(wb_name):
      os.remove(wb_name)
#

    RD = RevolvingDeal(ProjectName,dt_param['dt_pool_cut'],dt_param['dt_trust_effective'],Flag_RevolvingDeal,date_revolving_pools_cut)
#    
    #RD.get_AssetPool(['ABS11_r2201902181346320','ABS11_r2201902181346321','ABS11_r2201902181346322'])#'ABS10left2nd'])#'ABS11_r2201902011521110','ABS11_r2201902011521111','ABS11_r2201902011521112'])#'ABS11_r1201901041147590','ABS11_r1201901041147591','ABS11_r1201901041147592','ABS11_r1201901041147593','ABS11_r1201901041147594','ABS11_r1201901041147595'])#'abs9_rvg6_contract_list_0','abs9_rvg6_contract_list_1','abs9_rvg6_contract_list_2'])#'abs11_rvg1_contract_list_0','abs11_rvg1_contract_list_1','abs11_rvg1_contract_list_2'])
    RD.get_AssetPool(['ABS13_initialpool'])

    #print(RD.asset_pool[:5])
#    RD.select_by_ContractNO('exclude',['ABS11r2_selected_to_Trust_20190203_1time(fyr)']) 
#
#    RD.add_Columns([
#                  [['ProfessionTypeValueTransform'],'Profession','Profession_HC'],
#                  [['UsageTypeValueTransform'],'Usage','Usage_HC'],
#                 # [['abs10_rvg4_contract_list_with_cs','abs10_rvg4_contract_list_without_cs'],'No_Contract','#合同号']
#                  ])
#        
    #RD.asset_pool['Credit_Score'] = RD.asset_pool['Credit_Score_15'].round(3)

    #RS_results = RD.run_ReverseSelection(Targets,RS_Group_d)
    #RS_results.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/AssetsSelected_Final.csv',index=False)
    #RD.asset_pool.rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/check_abs9_default_assets.csv',index=False)
    
#    RD.asset_pool[RD.asset_pool['LoanRemainTerm'] > 240].rename(columns = Header_Rename_REVERSE).to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/Exclude part 2.csv',index=False)

    #RD.run_Stat(Distribution_By_Category,Distribution_By_Bins)
        
    #RD.asset_pool['first_due_date_after_pool_cut'] = RD.asset_pool['first_due_date_after_pool_cut'].where(RD.asset_pool['first_due_date_after_pool_cut'] != '3000/01/01','2019/01/01')
    #RD.asset_pool = RD.asset_pool[RD.asset_pool['Amount_Outstanding_yuan']>0]
    
    RD.init_oAP_Acc()
    
    for asset_status in all_asset_status:
        if len(RD.asset_pool[(RD.asset_pool['贷款状态'] == asset_status)]) == 0:
            logger.info('No Assets to calc for {0}'.format(asset_status))
            continue
        else:
            logger.info('Collecting CF for asset_status {0}'.format(asset_status))   
            RD.get_oAPCF(asset_status,
                         asset_status_calcDate_BackMonth[asset_status]['BackMonth'],
                         asset_status_calcDate_BackMonth[asset_status]['calcDate']
                         )
            
            save_to_excel(RD.apcf_original[asset_status],'cf_o',wb_name)
            #save_to_excel(RD.df_ppmt[asset_status],'df_ppmt',wb_name)
            #save_to_excel(RD.apcf_original_structure[asset_status],'cf_o_structure',wb_name)
    
    scenarios = {}
    scenarios['best'] = {'M0_2_ERM0':0.99,'M0_2_M1':0.022,'M1_2_M0M2':0.5,'M2_2_M0M3':0.6,'M3_2_M0D':0.7,'D_2_RL':0.8,'scenario_weight':0.7} 
    #scenarios['worst'] = {'M0_2_ERM0':0.99,'M0_2_M1':0.05,'M1_2_M0M2':0.5,'M2_2_M0M3':0.7,'M3_2_M0D':0.7,'D_2_RL':0.99,'scenario_weight':0.3} 

    RD.init_oAP_scenarios(scenarios)
    
    for asset_status in all_asset_status:
        if len(RD.asset_pool[(RD.asset_pool['贷款状态'] == asset_status)]) == 0:
            logger.info('No Assets to calc for {0}'.format(asset_status))
            continue
        else:
            for scenario_id in scenarios.keys():
                logger.info('get_adjust_oAPCF_simulation for {0}...'.format(scenario_id))
                
                for _sim in range(simulation_times):#
                    logger.info('simulator index is {0}'.format(_sim))
                    RD.adjust_oAPCF(scenario_id,asset_status,asset_status_calcDate_BackMonth[asset_status]['calcDate'])
                    save_to_excel(RD.APCF_adjusted_save[asset_status][scenario_id],'cf_O_adjusted_'+scenario_id,wb_name)

                    ######### create RD.APCF_adjusted_save[asset_status][scenario_id][_sim] to descope this function
                    RD.update_oAP_Acc(scenario_id,asset_status)
    
    for scenario_id in scenarios.keys():
        
        RD.oAP_Acc_DeSimulation(scenario_id,simulation_times)
        save_to_excel(RD.df_AP_PAcc_actual_O_DeSimu[scenario_id],'De-Sim_'+scenario_id,wb_name)
        
        logger.info('CDR_calc_O...for {0}...'.format(scenario_id))
        RD.CDR_calc_O(scenario_id)
    save_to_excel(pd.DataFrame.from_dict(RD.CDR_O),'RnR&CDR',wb_name)
##            
#########
    RD.get_rAPCF_structure()
    
    RD.init_rAP_scenarios(scenarios)
    
    RD.init_rAP_Acc()

    for scenario_id in scenarios.keys():
        logger.info('forcast_Revolving_APCF for scenario_id {0}...'.format(scenario_id))  
        if RD.RevolvingDeal is not True:
            pass
        else:
                for which_revolving_pool in range(1,len(RD.date_revolving_pools_cut) + 1):
                    #logger.info('forcast_Revolving_APCF for which_revolving_pool {0}...'.format(which_revolving_pool))
                    purchase_amount = RD.prepare_PurchaseAmount(which_revolving_pool,scenario_id)
                    apcf_revolving_structure = deepcopy(RD.apcf_revolving_structure)
                    
                    RD.prepare_revolving_pool(scenario_id,which_revolving_pool,purchase_amount,apcf_revolving_structure)

                    APCFa = APCF_adjuster(RD.scenarios,scenario_id,RD.apcf_revolving[scenario_id][which_revolving_pool],
                                          RD.df_ppmt[scenario_id][which_revolving_pool],RD.df_ipmt[scenario_id][which_revolving_pool],
                                          RD.dates_recycle_list_revolving[scenario_id][which_revolving_pool],date_revolving_pools_cut[which_revolving_pool-1],asset_status_for_revolving)
                    RD.apcf_revolving_adjusted[scenario_id][which_revolving_pool],RD.APCF_R_adjusted_save[scenario_id][which_revolving_pool] = APCFa.adjust_APCF('R')
                    #save_to_excel(self.apcf_revolving_adjusted[scenario_id][which_revolving_pool],'rAPCFa_' + scenario_id + str(which_revolving_pool),wb_name)
            
                    RD.update_rAP_acc(scenario_id,which_revolving_pool)
    
    for scenario_id in scenarios.keys():
        logger.info('forcast_Revolving_APCF for scenario_id {0}...'.format(scenario_id)) 
        RD.adjusted_all_rAP(scenario_id)    
        
        save_to_excel(pd.DataFrame.from_dict(RD.apcf_revolving_adjusted_all[scenario_id]),'Adjusted_all_rAP',wb_name)

    
    for scenario_id in scenarios.keys():
        logger.info('forcast_Revolving_APCF for scenario_id {0}...'.format(scenario_id))  
        RD.CDR_calc_R(scenario_id)
        save_to_excel(pd.DataFrame.from_dict(RD.CDR_R[scenario_id]),'RnR&CDR',wb_name)
        
    for scenario_id in scenarios.keys():
        RD.CDR_calc_All(scenario_id)
        
    save_to_excel(pd.DataFrame.from_dict(RD.CDR_all),'RnR&CDR',wb_name)
        
    RD.get_AP_pay_buy_allocation()    
        
    RD.init_Liability_Acc(fees)
#   
    #RD.run_WaterFall()    # RD.waterfall[scenario_id] is available
    for scenario_id in scenarios.keys():
        logger.info('scenario_id is {0}'.format(scenario_id))
        RD.waterfall[scenario_id],RD.reserveAccount_used[scenario_id] = run_Accounts(RD.AP_PAcc_original[scenario_id],RD.AP_PAcc_actual[scenario_id],
                                                   RD.AP_PAcc_pay[scenario_id],RD.AP_PAcc_buy[scenario_id],
                                                   RD.AP_IAcc_original[scenario_id],RD.AP_IAcc_actual[scenario_id],
                                                   RD.AP_IAcc_pay[scenario_id],RD.AP_IAcc_buy[scenario_id],
                                                   RD.AP_PAcc_outstanding[scenario_id],RD.AP_PAcc_reserve[scenario_id],#self.AP_PAcc_loss_allTerm[scenario_id],
                                                   scenario_id,RD.RevolvingDeal,RD.Liability_Acc,RD.RevolvingPool_PurchaseAmount
                                                   )
         
        RD.wf_BasicInfo[scenario_id] = deepcopy(BasicInfo_calculator(RD.waterfall[scenario_id],dt_param,Bonds))
        RD.wf_CoverRatio[scenario_id] = deepcopy(CR_calculator(RD.waterfall[scenario_id],RD.AP_PAcc_pay[scenario_id],RD.AP_IAcc_pay[scenario_id]))
        RD.wf_NPVs[scenario_id] = deepcopy(NPV_calculator(RD.waterfall[scenario_id],RD.AP_PAcc_pay[scenario_id],RD.AP_IAcc_pay[scenario_id]))
        RD.reserveAccount_used[scenario_id] = pd.DataFrame.from_dict(RD.reserveAccount_used[scenario_id])
    
    
    for scenario_id in scenarios.keys():
        logger.info('Saving results for scenario {0} '.format(scenario_id))
        save_to_excel(RD.waterfall[scenario_id],scenario_id,wb_name)
        save_to_excel(RD.wf_BasicInfo[scenario_id],scenario_id,wb_name)
        save_to_excel(RD.wf_CoverRatio[scenario_id],scenario_id,wb_name)
        save_to_excel(RD.wf_NPVs[scenario_id],scenario_id,wb_name)
        save_to_excel(RD.reserveAccount_used[scenario_id],scenario_id,wb_name)
        save_to_excel(RD.AP_pay_buy_allocation[scenario_id],scenario_id,wb_name)
    
    RnR = RD.cal_RnR()
    logger.info('RnR is: %s' % RnR)
    save_to_excel(pd.DataFrame({'RnR':[RnR]}),'RnR&CDR',wb_name)
#    
    end_time = datetime.datetime.now()   
    time_elapsed = end_time - start_time
    logger.info('Time: %0.4f' % time_elapsed.total_seconds())


if __name__ == '__main__':
    main()
