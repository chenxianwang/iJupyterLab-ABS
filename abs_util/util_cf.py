## -*- coding: utf-8 -*-
'''
Created on Mon Jun  5 20:59:42 2017

@author: Jonah.Chen
'''
import pandas as pd
import datetime
import numpy as np
from abs_util.util_general import save_to_excel,get_next_eom,get_logger

logger = get_logger(__name__)

pd.options.mode.chained_assignment = None

def cash_flow_collection(df_cash_flow,dates_recycle,first_due_period,revolving_pool_name,wb_name):
    
    #logger.info('Calculating PMT for ' + revolving_pool_name + '.....')
    #unique_due_month = pd.unique(df_cash_flow[first_due_period].ravel())
    
    #logger.info('Calculating PPMT for ' + revolving_pool_name + '.....')
    df_ppmt = calc_PPMT(df_cash_flow,dates_recycle,first_due_period)
    #save_to_excel(df_ppmt,'acf_ppmt_'+revolving_pool_name,wb_name)
    
    #logger.info('Calculating IPMT for ' + revolving_pool_name + '.....')
    df_ipmt = calc_IPMT(df_cash_flow,dates_recycle,first_due_period)
    #save_to_excel(df_ipmt,'acf_ipmt_'+revolving_pool_name,wb_name)
    
    #logger.info('Calculating Fee for ' + revolving_pool_name + '.....')
    df_fee = calc_FEE(df_cash_flow,dates_recycle,first_due_period)
    #save_to_excel(df_fee,'acf_fee_'+revolving_pool_name,wb_name)
    
    df_ppmt_total_by_date = pd.DataFrame([df_ppmt[dates_recycle].sum()])
    df_ipmt_total_by_date = pd.DataFrame([df_ipmt[dates_recycle].sum()])
    df_fee_total_by_date = pd.DataFrame([df_fee[dates_recycle].sum()])
   
    df_pmt_total_by_date = pd.DataFrame({'date_recycle': dates_recycle,
                                         'principal': df_ppmt_total_by_date.transpose()[0],
                                         'interest': df_ipmt_total_by_date.transpose()[0],
                                         #'fee': df_fee_total_by_date.transpose()[0],
                                         'total': (df_ppmt_total_by_date
                                                          + df_ipmt_total_by_date
                                                          + df_fee_total_by_date
                                                          ).transpose()[0]
                                         })
    #save_to_excel(df_pmt_total_by_date,'acf_pmt_'+revolving_pool_name,wb_name)
    
    #logger.info('Cash Flow Calculation Done for ' + revolving_pool_name + '.....')
    
    return df_pmt_total_by_date,df_ppmt,df_ipmt#,df_ppmt_total_by_date,df_ipmt_total_by_date,df_fee_total_by_date
    

def calc_PPMT(df,dts_r,first_due_period):
    first_due_month = pd.unique(df[first_due_period].ravel())
    df_ppmt = pd.DataFrame()
    
    for f_d_m in first_due_month:
        f_d_m_this_n_z = df[(df[first_due_period] == f_d_m) & (df['Total_Fee_Rate']>0)]
        for ind_r,date_r in enumerate(dts_r):
            #f_d_m_this_n_z[date_r] = 0
            f_d_m_this_n_z[date_r] = f_d_m_this_n_z[date_r].where((f_d_m_this_n_z[first_due_period] > ind_r) | (f_d_m_this_n_z['Term_Remain'] < (ind_r - f_d_m +1)),
                                                    np.ppmt(f_d_m_this_n_z['Total_Fee_Rate']/12,(ind_r - f_d_m +1),f_d_m_this_n_z['Term_Remain'],((-1)*f_d_m_this_n_z['OutstandingPrincipal']))
                                                    )
            
        f_d_m_this_z = df[(df[first_due_period] == f_d_m) & (df['Total_Fee_Rate']==0)]   
        for ind_r,date_r in enumerate(dts_r):
            #f_d_m_this_z[date_r] = 0    
            f_d_m_this_z[date_r] = f_d_m_this_z[date_r].where((f_d_m_this_z[first_due_period] > ind_r) | (f_d_m_this_z['Term_Remain'] < (ind_r - f_d_m +1)),
                                                    f_d_m_this_z['OutstandingPrincipal'] / f_d_m_this_z['Term_Remain']
                                                    )
        df_ppmt = df_ppmt.append(f_d_m_this_n_z).append(f_d_m_this_z,ignore_index=True)
    
    return df_ppmt

#SERVICE_FEE_RATE   
def calc_IPMT(df,dts_r,first_due_period):
    first_due_month = pd.unique(df[first_due_period].ravel())
    df_ipmt = pd.DataFrame()
    
    for f_d_m in first_due_month:
        f_d_m_this_n_z = df[(df[first_due_period] == f_d_m) & (df['Interest_Rate']>0)]
        for ind_r,date_r in enumerate(dts_r):
            #f_d_m_this_n_z[date_r] = 0
            f_d_m_this_n_z[date_r] = f_d_m_this_n_z[date_r].where((f_d_m_this_n_z[first_due_period] > ind_r) | (f_d_m_this_n_z['Term_Remain'] < (ind_r - f_d_m +1)),
                                                    f_d_m_this_n_z['Interest_Rate_Proportion'] * np.ipmt(f_d_m_this_n_z['Total_Fee_Rate']/12,(ind_r - f_d_m +1),f_d_m_this_n_z['Term_Remain'],((-1)*f_d_m_this_n_z['OutstandingPrincipal']))
                                                    )
            
        f_d_m_this_z = df[(df[first_due_period] == f_d_m) & (df['Interest_Rate']==0)]   
#        for ind_r,date_r in enumerate(dts_r):
#            f_d_m_this_z[date_r] = 0    

        df_ipmt = df_ipmt.append(f_d_m_this_n_z).append(f_d_m_this_z,ignore_index=True)
    
    return df_ipmt


def calc_FEE(df,dts_r,first_due_period):
    first_due_month = pd.unique(df[first_due_period].ravel())
    df_fee = pd.DataFrame()
    
    for f_d_m in first_due_month:
        f_d_m_this_n_z = df[(df[first_due_period] == f_d_m) & (df['SERVICE_FEE_RATE']>0)]
        for ind_r,date_r in enumerate(dts_r):
            #f_d_m_this_n_z[date_r] = 0
            f_d_m_this_n_z[date_r] = f_d_m_this_n_z[date_r].where((f_d_m_this_n_z[first_due_period] > ind_r) | (f_d_m_this_n_z['Term_Remain'] < (ind_r - f_d_m +1)),
                                                    (1-f_d_m_this_n_z['Interest_Rate_Proportion']) * np.ipmt(f_d_m_this_n_z['Total_Fee_Rate']/12,(ind_r - f_d_m +1),f_d_m_this_n_z['Term_Remain'],((-1)*f_d_m_this_n_z['OutstandingPrincipal']))
                                                    )
            
        f_d_m_this_z = df[(df[first_due_period] == f_d_m) & (df['SERVICE_FEE_RATE']==0)]
#        for ind_r,date_r in enumerate(dts_r):
#            f_d_m_this_z[date_r] = 0    

        df_fee = df_fee.append(f_d_m_this_n_z).append(f_d_m_this_z,ignore_index=True)
    
    return df_fee
