# -*- coding: utf-8 -*-
"""
Created on Mon Jun 18 16:48:57 2018

@author: Jonah.Chen
"""

import pandas as pd
import numpy as np
from copy import deepcopy
import datetime
from abs_util.util_general import *
from abs_util.util_cf import *
from abs_util.util_sr import *
from dateutil.relativedelta import relativedelta
from Params import *
from Accounts.BondPrinAccount import BondPrinAccount
from Accounts.FeesAccount import FeesAccount
from Accounts.TaxAccount import TaxAccount

logger = get_logger(__name__)

def run_Accounts(princ_original,princ_actual,princ_pay,princ_buy,
                 int_original,int_actual,int_pay,int_buy,
                 princ_outstanding,princ_reserve,#princ_loss,
                 scenario_id,RevolvingDeal,Liability_Acc,RevolvingPool_PurchaseAmount = None
                 ): # Initalizing BondsCashFlow
    
    logger.info('run_Accounts...')
    principal_to_pay = deepcopy(princ_pay)
    principal_reserve = deepcopy(princ_reserve)
    principal_outstanding = deepcopy(princ_outstanding)
    interest_actual = deepcopy(int_actual)
    interest_to_pay = deepcopy(int_pay)
    #TODO:When to use deepcopy
    #tranches_ABC = deepcopy(Bonds)
    reserveAccount_used = {}
    
    #preissue_FAcc = FeesAccount('pre_issue',fees)
    tax_Acc = deepcopy(Liability_Acc['tax_Acc'])
    trustee_FAcc = deepcopy(Liability_Acc['trustee_FAcc'])
    custodian_FAcc = deepcopy(Liability_Acc['custodian_FAcc'])
    servicer_FAcc = deepcopy(Liability_Acc['servicer_FAcc'])
    #pre_issue_FAcc = Liability_Acc[]
    #pay_interest_service_FAcc = Liability_Acc[]
    
    A_IAcc = deepcopy(Liability_Acc['A_IAcc'])
    B_IAcc = deepcopy(Liability_Acc['B_IAcc'])
    C_IAcc = deepcopy(Liability_Acc['C_IAcc'])

    A_PAcc = deepcopy(Liability_Acc['A_PAcc'])
    B_PAcc = deepcopy(Liability_Acc['B_PAcc'])
    C_PAcc = deepcopy(Liability_Acc['C_PAcc'])
    EE_Acc = deepcopy(Liability_Acc['EE_Acc'])

    #preissue_FAcc
    for date_pay_index,date_pay in enumerate(dates_pay):
        
        #logger.info('calc bais for {0} is {1}'.format(date_pay,sum([principal_actual[k] for k in principal_actual.keys() if k > date_pay + relativedelta(months= -1)]) - RevolvingPool_PurchaseAmount[date_pay_index+1]))
        #logger.info('calc tax bais for {0} is {1}'.format(date_pay,interest_actual[dates_recycle[date_pay_index]]))
        pay_for_fee = tax_Acc.pay(date_pay,interest_actual[dates_recycle[date_pay_index]])#,0][B_PAcc.iBalance(date_pay) == 0])
        #logger.info('pay_for_fee for {0} is {1}'.format(date_pay,pay_for_fee))
        #logger.info('principal_actual is {0}'.format(sum([principal_actual[k] for k in principal_actual.keys()])))

        ########################################################################################
        if date_pay_index==0 :
            calc_basis_for_fee_trustee = amount_total_issuance
        elif date_pay_index <= nbr_revolving_pools:
            if RevolvingDeal is True:
                purchase_RevolvingPool = deepcopy(RevolvingPool_PurchaseAmount[scenario_id])
                calc_basis_for_fee_trustee = principal_outstanding[dates_recycle[date_pay_index-1]]+purchase_RevolvingPool[date_pay_index]
            else:calc_basis_for_fee_trustee = principal_outstanding[dates_recycle[date_pay_index-1]]
        else:
            calc_basis_for_fee_trustee = principal_outstanding[dates_recycle[date_pay_index-1]]
        #logger.info('')
        pay_for_fee += trustee_FAcc.pay(date_pay,calc_basis_for_fee_trustee)
        #######################################################################################
        calc_basis_for_fee_custodian = principal_outstanding[dates_recycle[date_pay_index]]
        pay_for_fee += custodian_FAcc.pay(date_pay,calc_basis_for_fee_custodian)
        #######################################################################################
        if date_pay_index==0 :
            calc_basis_for_fee_servicer = amount_total_issuance
        else:
            calc_basis_for_fee_servicer = principal_outstanding[dates_recycle[date_pay_index-1]]            
        pay_for_fee += servicer_FAcc.pay(date_pay,calc_basis_for_fee_servicer)
        #######################################################################################
        #logger.info('pay_for_fee for {0} is {1}'.format(date_pay,pay_for_fee))
        pay_for_fee += A_IAcc.pay(date_pay,A_PAcc.iBalance(date_pay))
        pay_for_fee += B_IAcc.pay(date_pay,B_PAcc.iBalance(date_pay))
        pay_for_fee += C_IAcc.pay(date_pay,C_PAcc.iBalance(date_pay))
        
        #logger.info('pay_for_fee for {0} is {1}'.format(date_pay,pay_for_fee))
        #logger.info('pay_for_fee for {0} is {1}'.format(date_pay,interest_actual[dates_recycle[date_pay_index]]))
        
        interest_transfer_to_prin = interest_to_pay[dates_recycle[date_pay_index]] - pay_for_fee
        #logger.info('interest_transfer_to_prin on {0} is {1}'.format(date_pay,interest_transfer_to_prin))
        if (A_PAcc.iBalance(date_pay) + B_PAcc.iBalance(date_pay) + C_PAcc.iBalance(date_pay)>0) and (interest_transfer_to_prin < -0.00001) :
            logger.info('interest_transfer_to_prin on {0} is less than 0: {1}'.format(date_pay,interest_transfer_to_prin))
        
        principal_to_pay[dates_recycle[date_pay_index]] += interest_transfer_to_prin
        #logger.info('principal_to_pay[dates_recycle[date_pay_index]] on {0} is {1}'.format(date_pay,principal_to_pay[dates_recycle[date_pay_index]]))
        available_for_prin = deepcopy(principal_to_pay[dates_recycle[date_pay_index]])
        reserved = deepcopy(principal_reserve[dates_recycle[date_pay_index]])
        
        available_for_prin,reserved = A_PAcc.pay_then_ToNext(date_pay,available_for_prin,reserved)
        available_for_prin,reserved = B_PAcc.pay_then_ToNext(date_pay,available_for_prin,reserved)
        available_for_prin,reserved = C_PAcc.pay_then_ToNext(date_pay,available_for_prin,reserved)
        available_for_prin,reserved = EE_Acc.pay_then_ToNext(date_pay,available_for_prin,reserved)
        #logger.info('Loop Done for {0}'.format(date_pay))    
        if reserved < principal_reserve[dates_recycle[date_pay_index]]:
            #logger.info('reserveAccount_used for {0},the amount used is {1}'.format(date_pay,principal_reserve[dates_recycle[date_pay_index]] - reserved)) 
            reserveAccount_used[date_pay] = [principal_reserve[dates_recycle[date_pay_index]] - reserved]
            principal_reserve[dates_recycle[date_pay_index]] = reserved
    

    
    AP_PAcc_reserve_wf = pd.DataFrame(list(principal_reserve.items()), columns=['date_recycle', 'principal_reserve_remain'])
    AP_PAcc_reserve_wf['date_pay'] = dates_pay
    
    A_Principal_wf = pd.DataFrame(list(A_PAcc.receive.items()), columns=['date_pay', 'amount_pay_A_principal'])
    B_Principal_wf = pd.DataFrame(list(B_PAcc.receive.items()), columns=['date_pay', 'amount_pay_B_principal'])
    C_Principal_wf = pd.DataFrame(list(C_PAcc.receive.items()), columns=['date_pay', 'amount_pay_C_principal'])
    EE_wf = pd.DataFrame(list(EE_Acc.receive.items()), columns=['date_pay', 'amount_pay_EE_principal'])
    
    A_Interest_wf = pd.DataFrame(list(A_IAcc.receive.items()), columns=['date_pay', 'amount_pay_A_interest'])
    B_Interest_wf = pd.DataFrame(list(B_IAcc.receive.items()), columns=['date_pay', 'amount_pay_B_interest'])
    C_Interest_wf = pd.DataFrame(list(C_IAcc.receive.items()), columns=['date_pay', 'amount_pay_C_interest'])
    servicer_fee_wf = pd.DataFrame(list(servicer_FAcc.receive.items()), columns=['date_pay', 'fee_servicer'])
    tax_wf = pd.DataFrame(list(tax_Acc.receive.items()), columns=['date_pay', 'fee_tax'])
    trustee_wf = pd.DataFrame(list(trustee_FAcc.receive.items()), columns=['date_pay', 'fee_trustee'])
    custodian_wf = pd.DataFrame(list(custodian_FAcc.receive.items()), columns=['date_pay', 'fee_custodian'])
    
    A_Balance_wf = pd.DataFrame(list(A_PAcc.balance.items()), columns=['date_pay', 'amount_outstanding_A_principal'])
    B_Balance_wf = pd.DataFrame(list(B_PAcc.balance.items()), columns=['date_pay', 'amount_outstanding_B_principal'])
    C_Balance_wf = pd.DataFrame(list(C_PAcc.balance.items()), columns=['date_pay', 'amount_outstanding_C_principal'])
    EE_Balance_wf = pd.DataFrame(list(EE_Acc.balance.items()), columns=['date_pay', 'amount_outstanding_EE_principal'])
                    
    wf = A_Principal_wf\
              .merge(B_Principal_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(C_Principal_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(EE_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(A_Interest_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(B_Interest_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(C_Interest_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(servicer_fee_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(tax_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(trustee_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(custodian_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(A_Balance_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(B_Balance_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(C_Balance_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(EE_Balance_wf,left_on='date_pay',right_on='date_pay',how='outer')\
              .merge(AP_PAcc_reserve_wf,left_on='date_pay',right_on='date_pay',how='outer')#\
                    
    
    #logger.info('actual principal payment is {0}'.format(sum(wf[['amount_pay_A_principal','amount_pay_B_principal','amount_pay_C_principal']].sum())))
    #save_to_excel(wf,'wf',wb_name)

    #return wf[wf['principal_recycle_total']>0],reserveAccount_used
    return wf,reserveAccount_used

def BasicInfo_calculator(waterfall,dt_param,tranches_ABC):
    
    #logger.info('BasicInfo_calculator...')
    tranches_cf = deepcopy(waterfall)
    dt_param = dt_param

    tranches_cf['years_interest_calc_this_period'] = (tranches_cf['date_pay'] - (tranches_cf['date_pay']+relativedelta(months= -1))).dt.days/days_in_a_year
    tranches_cf['years_interest_calc_cumulative'] = tranches_cf['years_interest_calc_this_period'].cumsum()
    name_tranche = ['A','B','C']
        
    WA_term = []
    date_maturity_predict = []
    maturity_term = []
    
    for _tranche_index,_tranche_name in enumerate(name_tranche):
        if tranches_cf['amount_outstanding_' + _tranche_name + '_principal'].min() == 0:
            WA_term.append(sum(tranches_cf['amount_pay_' + _tranche_name + '_principal'] * tranches_cf['years_interest_calc_cumulative']) / sum(tranches_cf['amount_pay_' + _tranche_name + '_principal']))
            date_maturity_predict.append(tranches_cf.iloc[tranches_cf['amount_outstanding_' + _tranche_name + '_principal'].idxmin()]['date_pay'])
            maturity_term.append((date_maturity_predict[_tranche_index] - dt_param['dt_trust_effective']).days / days_in_a_year )
        else:
            logger.info('tranche {0} Default. '.format(_tranche_name))
            WA_term.append('Default')
            date_maturity_predict.append('Default')
            maturity_term.append('Default')
    
    tranche_basic_info = pd.DataFrame({'name_tranche':name_tranche,
                                       'WA_term':WA_term,
                                       'date_maturity_predict':date_maturity_predict,
                                       'maturity_term':maturity_term,
                                      })

    return tranche_basic_info

def CR_calculator(waterfall,princ_pay,interest_pay):
    tranches_cf = deepcopy(waterfall)
    principal_to_pay = deepcopy(princ_pay)
    interest_to_pay = deepcopy(interest_pay)
    
    actual_to_pay = sum(principal_to_pay[k] for k in principal_to_pay.keys()) + sum(interest_to_pay[k] for k in interest_to_pay.keys())
    Cover_ratio_Senior = actual_to_pay / sum(tranches_cf[['amount_pay_A_principal','amount_pay_A_interest']].sum())
    Cover_ratio_Mezz = (actual_to_pay - sum(tranches_cf[['amount_pay_A_principal','amount_pay_A_interest']].sum()) ) / sum(tranches_cf[['amount_pay_B_principal','amount_pay_B_interest']].sum())
    
    CoverRation = pd.DataFrame({'Cover_ratio_Senior':[Cover_ratio_Senior],
                                'Cover_ratio_Mezz':[Cover_ratio_Mezz]
                                })
                               
    return CoverRation                           

def NPV_calculator(waterfall,princ_list,interest_list):
    tranches_cf = deepcopy(waterfall)
    principal = deepcopy(princ_list)
    interest = deepcopy(interest_list)
    
    actual_recycle = [principal[k] + interest[k] for k in dates_recycle]
    NPV_asset_pool = np.npv(rate_discount / 12,actual_recycle) / (1 + rate_discount / 12 )
    
    actual_pay_to_Originator = tranches_cf['amount_pay_C_principal'] + tranches_cf['amount_pay_C_interest'] + tranches_cf['amount_pay_EE_principal']+ tranches_cf['fee_servicer']
    NPV_originator = np.npv(rate_discount / 12,actual_pay_to_Originator) / (1 + rate_discount / 12 )  #
    
    NPVs = pd.DataFrame({'NPV_asset_pool':[NPV_asset_pool],
                        'NPV_originator':[NPV_originator]
                        })

    return NPVs
