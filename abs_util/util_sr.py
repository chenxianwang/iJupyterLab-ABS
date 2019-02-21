# -*- coding: utf-8 -*-
'''
Created on Sun Jun  4 17:36:17 2017

@author: Jonah.Chen
'''
import pandas as pd
from constant import *
from abs_util.util_general import *
from abs_util.util_cf import *
import datetime
from Params import *
from dateutil.relativedelta import relativedelta
from AssetsCashFlow import AssetsCashFlow

logger = get_logger(__name__)

def cal_table_4_1(DetailList,wb_name):
    
    #DetailList = DetailList[(DetailList['贷款是否已结清']=='N')]
    logger.info('cal_table_4_1...')
    DetailList['贷款状态'] = DetailList['贷款状态'].where((DetailList['贷款是否已结清'] == '未结清')|(DetailList['贷款是否已结清'] == 'N'),'已结清')
    #DetailList['Amount_Outstanding_yuan'] = DetailList['Amount_Outstanding_yuan'].where(DetailList['Days_Overdue_Current']<=180,0)
    save_to_excel(group_by_d(DetailList,['贷款状态'],'Amount_Outstanding_yuan'),'service_report'+Batch_ID,wb_name)
    
#    DetailList['贷款状态_Jonah'] = '正常'
#    DetailList['贷款状态_Jonah'][(DetailList['Days_Overdue_Current']>=1)&(DetailList['Days_Overdue_Current']<=30)] = '拖欠1-30天'
#    DetailList['贷款状态_Jonah'][(DetailList['Days_Overdue_Current']>=31)&(DetailList['Days_Overdue_Current']<=60)] = '拖欠31-60天'
#    DetailList['贷款状态_Jonah'][(DetailList['Days_Overdue_Current']>=61)&(DetailList['Days_Overdue_Current']<=90)] = '拖欠61-90天'
#    DetailList['贷款状态_Jonah'][(DetailList['Days_Overdue_Current']>=91)] = '拖欠90天以上'              
#    save_to_excel(group_by_d(DetailList,['贷款状态_Jonah'],'Amount_Outstanding_yuan'),'service_report',wb_name)

def cal_table_4_2(DetailList,wb_name):
    save_to_excel(group_by_d(DetailList,'是否为本期新增拖欠超过【90】天（不含）的贷款','违约时点未偿本金余额'),\
                  'service_report',wb_name)

def cal_table_4_3(DetailList,pool_cut_volumn,report_period,wb_name):
    CDR = pd.DataFrame({'Period':[report_period],
                        'CDR':[sum(DetailList['违约时点未偿本金余额']) / pool_cut_volumn]
                        })
    CDR[['CDR']] = percentage_format(CDR[['CDR']])
    print(CDR)
    print(sum(DetailList['违约时点未偿本金余额']))
    print(pool_cut_volumn)
    save_to_excel(CDR,'service_report',wb_name)

def cal_table_5(SourcePath,wb_name):
    DetailList = pd.read_csv(SourcePath,encoding = 'gbk')
    save_to_excel(group_by_d(DetailList,'处置状态：','违约时点未偿本金余额'),'service_report'+Batch_ID,wb_name)

def cal_table_6(DetailList,calcDate,wb_name):
    logger.info('cal_table_6...')
    #DetailList['first_due_date_after_pool_cut'] = pd.to_datetime(DetailList['Dt_Maturity']) - DetailList['Term_Remain'].values.astype("timedelta64[M]")
    DetailList['first_due_date_after_pool_cut'] = DetailList['first_due_date_after_pool_cut'].where(
                                                        DetailList['first_due_date_after_pool_cut'] != '3000/1/1',
                                                        calcDate
                                                        )
    DetailList['SERVICE_FEE_RATE'] = 0
    asset_status_calcDate_BackMonth = {'正常贷款':{'calcDate':calcDate,'BackMonth':0},
                    '拖欠1-30天贷款':{'calcDate':calcDate + relativedelta(months=-1),'BackMonth':1},
                    '拖欠31-60天贷款':{'calcDate':calcDate + relativedelta(months=-2),'BackMonth':2},
                    '拖欠61-90天贷款': {'calcDate':calcDate + relativedelta(months=-3),'BackMonth':3},
                    '拖欠90天以上贷款': {'calcDate':calcDate + relativedelta(months=-4),'BackMonth':4}
                    }

    for asset_status in asset_status_calcDate_BackMonth.keys():
        
        logger.info('calc ACF for ' + asset_status)
        
        DetailList_a_s = DetailList[DetailList['贷款状态'] == asset_status]
        if len(DetailList_a_s) >0:
            
            ACF = AssetsCashFlow(DetailList_a_s[['No_Contract','Interest_Rate','SERVICE_FEE_RATE','Amount_Outstanding_yuan','first_due_date_after_pool_cut','Term_Remain','Dt_Start','Province']],
                             asset_status_calcDate_BackMonth[asset_status]['calcDate']
                             )
    
            acf_original,acf_structure,dates_recycle_list,df_ppmt,df_ipmt = ACF.calc_APCF(asset_status_calcDate_BackMonth[asset_status]['BackMonth'])            
            
#            cf_c_a_s_1 = _cf_c_a_s[_cf_c_a_s['date_recycle'] <= get_next_eom(calcDate,0)]
#            cf_c_a_s_1 = pd.DataFrame(cf_c_a_s_1[['amount_interest','amount_principal','amount_total']].sum()).transpose()
#            cf_c_a_s_1['date_recycle'] = get_next_eom(calcDate,0)
#            #save_to_excel(cf_c_a_s_1,asset_status+'_1',wb_name)
#            cf_c_a_s_2 = _cf_c_a_s[_cf_c_a_s['date_recycle'] > get_next_eom(calcDate,0)]
#            #save_to_excel(cf_c_a_s_2,asset_status+'_2',wb_name)        
#            cf_c_a_s = cf_c_a_s_1.append(cf_c_a_s_2,ignore_index=True)
            
            save_to_excel(acf_original,asset_status + '_cf'+Batch_ID,wb_name)
        
        
    
def cal_table_7(DetailList,wb_name):
    
    header_name_dict = {k:k.replace(":","：") for k in list(DetailList.columns.values) }    
    DetailList = DetailList.rename(columns = {k:v for k,v in header_name_dict.items()})
    
    table_7 = pd.DataFrame()
    
    if DATA_FROME_SYSTEM == False:
        fee_type_dict = {'B':'principal','C':'interest','E':'penalty','F':'acc'}
    else:
        fee_type_dict = {'本金':'principal','利息':'interest','违约金':'penalty','其他':'acc',}
        
    for recycle_type,recycle_type_en in fee_type_dict.items():
        this_recycle_type = []
        
        this_recycle_sub_type = recycle_type_en + '_sub_type'
        
        if DATA_FROME_SYSTEM == False:
            for  this_recycle_sub_type in [recycle_type+'1：正常回收',recycle_type+'2：提前还款',recycle_type+'3：拖欠回收',recycle_type+'4：违约回收',recycle_type+'5：账务处理']:
                this_recycle_type.append(DetailList[this_recycle_sub_type].sum())
        else:
            for  this_recycle_sub_type in [recycle_type+'：正常回收',recycle_type+'：提前还款',recycle_type+'：拖欠回收',recycle_type+'：违约回收',recycle_type+'：账务处理']:
                this_recycle_type.append(DetailList[this_recycle_sub_type].sum())

        table_7[recycle_type] = this_recycle_type
                        
    try:logger.info('调整回收款 is {0}'.format(DetailList['调整回收款'].sum()))
    except(KeyError):pass

    save_to_excel(table_7,'service_report'+Batch_ID,wb_name)

def cal_table_11_13(ServiceReportListPath_A):    
    DetailList = pd.read_csv(SourcePath,encoding = 'gbk')
    
    logger.info('Statistics Dimension Setting.....')
    Distribution_By_Category, Distribution_By_Bins = dimension_setup()
    
    DetailList['_剩余本金'] = DetailList['剩余本金']
    
    DetailList['账龄'] = DetailList['合同期限'] - DetailList['剩余期限']  
    
    #basic_statistics(df)

    dimension_category_list = []
    for dimension_category in Distribution_By_Category:
        logger.info('Calculating for ' + dimension_category )
        dimension_category_list.append(df_result(DetailList,dimension_category,dimension_category))
    save_to_excel(dimension_category_list,'sr_table_11')
    
    dimension_bins_list = []
    for dimension_bins in Distribution_By_Bins.keys():
        logger.info('Calculating for ' + dimension_bins )
        dimension_bins_list.append(df_bins_result(DetailList,dimension_bins,Distribution_By_Bins[dimension_bins]))
    save_to_excel(dimension_bins_list,'sr_table_11'+Batch_ID,wb_name)

    logger.info('Statistics Calculation Done.')

def df_bins_result(df,d,bins_this):
        d_cut = pd.cut(df[d], bins=bins_this)
        return df_result(df,d_cut,d)


def df_result(df,d_cut,d):
    df_this = df.groupby([d_cut])\
               .agg({'剩余本金':'sum','订单号':'count'})\
               .reset_index()\
               .rename(columns = {'剩余本金':'本金余额（万元）',
                                  '订单号':'贷款笔数'                                                      
                                  }
                       )
    df_this = percentage_cal(df_this,d)
    return df_this


def group_by_d(DetailList,group_d,sum_d):
    
    try:
        group_table = DetailList.groupby([d for d in group_d])\
                                .agg({sum_d:'sum','订单号':'count'})\
                                .reset_index()\
                                .rename(columns = {sum_d:'金额','订单号':'笔数'}
                       )
    except(KeyError):
         group_table = DetailList.groupby([d for d in group_d])\
                        .agg({sum_d:'sum','No_Contract':'count'})\
                        .reset_index()\
                        .rename(columns = {sum_d:'金额','No_Contract':'笔数'}
               )
                            
    group_table['金额占比'] = group_table['金额'] / sum(group_table['金额'])
    group_table['笔数占比'] = group_table['笔数'] / sum(group_table['笔数'])
    group_table.loc['总计']= group_table.sum()
    group_table.iloc[-1,group_table.columns.get_loc(group_d[0])] = '总计'
    
    group_table[['金额占比','笔数占比']] = percentage_format(group_table[['金额占比','笔数占比']])
    group_table[['金额','笔数']] = decimal_format(group_table[['金额','笔数']])
    
    print(group_table)
    return group_table