# -*- coding: utf-8 -*-
'''
Spyder Editor

This is a temporary script file.
'''
import sys
sys.path.append("..")
import os
from dateutil.relativedelta import relativedelta
import pandas as pd
import numpy as np
import datetime
from constant import *
from Params import *
from abs_util.util_general import *
from Deal import Deal
from RevolvingDeal import RevolvingDeal
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

    SR = ServiceReport(ProjectName,datetime.date(2019,2,1),1)
    SR.get_ServiceReportAssetsList('2ndReportDate',
                                   #['20190101_funding_abs11_asset_1166_0','20190101_funding_abs11_asset_1166_1'],
                                   #['AllAssetList20190218101008','AllAssetList20190218101059','AllAssetList20190218101157'],
                                   ['AllAssetList20190118154309','AllAssetList20190118154356','AllAssetList20190118154446'],
                                   #'',
                                   
                                   #['20190201_funding_abs9_asset_1263_0','20190201_funding_abs9_asset_1263_1','20190201_funding_abs9_asset_1263_2','20190201_funding_abs9_asset_1263_3','20190201_funding_abs9_asset_1263_4'], #AllAssetList
                                   #['20190201_funding_abs11_asset_1276_0','20190201_funding_abs11_asset_1276_1'],
                                   ['AllAssetList20190218101008','AllAssetList20190218101059','AllAssetList20190218101157'],
                                   '',              #'DefaultAssetList',
                                   'WaivedAssetList',#'abs9_waived_20181201',              #'WaivedAssetList',20180901_funding_abs9_waived_845
                                   'RedempedAssetList'#20190101_funding_abs11_unquali_1164'  #'RedemptionAssetList' #20180801_funding_abs9_unquali_784 
                                   ) 
    
    SR.service_report_AllAssetList_pre = SR.service_report_AllAssetList_pre[SR.service_report_AllAssetList_pre['ABS资产性质'] == 'ABS11_InitialPool']
    SR.service_report_AllAssetList_pre = SR.service_report_AllAssetList_pre[(~SR.service_report_AllAssetList_pre['No_Contract'].isin(SR.service_report_RedemptionAssetList['No_Contract']))]
    logger.info('SR.service_report_AllAssetList_pre[["Amount_Outstanding_yuan"]].sum() is {0},Asset count is {1}'.format(SR.service_report_AllAssetList_pre['Amount_Outstanding_yuan'].sum(),SR.service_report_AllAssetList_pre['No_Contract'].count()))

    SR.service_report_AllAssetList = SR.service_report_AllAssetList[SR.service_report_AllAssetList['ABS资产性质'] == 'ABS11_InitialPool']
    logger.info('SR.service_report_AllAssetList[["Amount_Outstanding_yuan"]].sum() is {0},Asset count is {1}'.format(SR.service_report_AllAssetList['Amount_Outstanding_yuan'].sum(),SR.service_report_AllAssetList['No_Contract'].count()))

    SR.service_report_WaivedAssetList = SR.service_report_WaivedAssetList[(SR.service_report_WaivedAssetList['No_Contract'].isin(SR.service_report_AllAssetList_pre['No_Contract']))]
    logger.info('SR.service_report_WaivedAssetList[["Amount_Outstanding_yuan"]].sum() is {0},Asset count is {1}'.format(SR.service_report_WaivedAssetList['本金减免金额'].sum(),SR.service_report_WaivedAssetList['No_Contract'].count()))

    #SR.service_report_AllAssetList = SR.service_report_AllAssetList.merge(SR.service_report_AllAssetList_pre[['订单号_DWH','剩余本金']],left_on= '订单号_ABS',right_on = '订单号_DWH',how='left')
   #SR.service_report_AllAssetList[SR.service_report_AllAssetList['Amount_Outstanding_yuan'] != SR.service_report_AllAssetList['剩余本金']].to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName + '/compare_OutstandingPrincipal_with_pre.csv')
    
    print(pd.unique(SR.service_report_AllAssetList['入池时间'].ravel()))
    SR.service_report_AllAssetList = SR.service_report_AllAssetList[(SR.service_report_AllAssetList['入池时间'] == '2018/08/31')]
    
    SR.service_report_AllAssetList = SR.service_report_AllAssetList[SR.service_report_AllAssetList['贷款是否已结清'] == 'N']
    print(len(SR.service_report_AllAssetList))
    SR.service_report_AllAssetList_pre['贷款状态'] = SR.service_report_AllAssetList_pre['贷款状态'].where((SR.service_report_AllAssetList_pre['贷款是否已结清'] == '未结清')|(SR.service_report_AllAssetList_pre['贷款是否已结清'] == 'N'),'已结清')
    pv = SR.service_report_AllAssetList_pre.groupby(['贷款是否已结清','贷款状态'])\
                                .agg({'Amount_Outstanding_yuan':'sum','No_Contract':'count'})\
                                .reset_index()\
                                .rename(columns = {'Amount_Outstanding_yuan':'金额','No_Contract':'笔数'}
                       )
                                
    pv.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/pv.csv',index=False)                            
    print(pv)

#    SR.service_report_AllAssetList_pre = SR.service_report_AllAssetList_pre[SR.service_report_AllAssetList_pre['贷款是否已结清'] == '未结清']
#    print(len(SR.service_report_AllAssetList_pre))
#    TroubleAssets = SR.service_report_AllAssetList[(~SR.service_report_AllAssetList['No_Contract'].isin(SR.service_report_AllAssetList_pre['No_Contract']))]
#    TroubleAssets.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/UnclosedAssets_DWH-ABSSystem.csv',index=False)
##    
#    SR.service_report_AllAssetList['Amount_Outstanding_yuan'] = SR.service_report_AllAssetList['Amount_Outstanding_yuan'].where(SR.service_report_AllAssetList['Days_Overdue_Current']<=180,0)
#    
#    SR.service_report_cal() #(trust_effective_date, report_period)
#    #SR.service_report_AllAssetList_pre[SR.service_report_AllAssetList_pre['No_Contract'].isin(['#3694454966003'])].to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/pre_3694454966003_.csv',index=False)
##    SR.service_report_AllAssetList[(SR.service_report_AllAssetList['贷款是否已结清'] == 'N') 
##                                    & (SR.service_report_AllAssetList['Income']==0)
##                                    ].to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/Income_CHECK.csv',index=False)
##
#    report_basis = SR.service_report_AllAssetList#[((SR.service_report_AllAssetList['贷款是否已结清']=='未结清')|(SR.service_report_AllAssetList['贷款是否已结清']=='N'))
#                                                  #  &(SR.service_report_AllAssetList['入池时间'] == '2019/01/01')]
#    #report_basis['Amount_Outstanding_yuan'] = report_basis['Amount_Outstanding_yuan'].where(report_basis['Days_Overdue_Current']<=180,0)
#    #report_basis['Type_Five_Category'] = report_basis['Type_Five_Category'].where(report_basis['Type_Five_Category']!='XNA','正常类')
#    report_basis['Usage'] = report_basis['Usage'].where(~report_basis['Usage'].isnull(),'XNA')
##    
#    report_basis['Credit_Score'] = report_basis['Credit_Score_15']#.round(3)
#    S = Statistics(report_basis)
#    S.general_statistics_1()
#    S.loop_Ds_ret_province_profession(Distribution_By_Category,Distribution_By_Bins)
#    S.cal_income2debt_by_ID()
###
#    OP_All,OP_Waived = SR.check_OutstandingPrincipal()
#    OP_PCD = SR.service_report_AllAssetList_pre[['No_Contract','Amount_Outstanding_yuan']]
#    check = OP_PCD.merge(OP_All,left_on='No_Contract',right_on='No_Contract',how='left')
#    check = check.merge(OP_Waived,left_on='No_Contract',right_on='No_Contract',how='left')
#
#    try:
#        check['本金减免金额'] = check['本金减免金额'].where(~check['本金减免金额'].isnull(),0)
#        check = check[abs(check['Amount_Outstanding_yuan'] - check['剩余本金_poolcutdate_calc'] - check['本金减免金额']) > 0.04]
#    except(KeyError):
#        check['减免金额'] = check['减免金额'].where(~check['减免金额'].isnull(),0)
#        check = check[abs(check['Amount_Outstanding_yuan'] - check['剩余本金_poolcutdate_calc'] - check['减免金额']) > 0.04]
#    
#    check.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName + '/compare_OutstandingPrincipal_with_pre.csv')
##
#    Age_SR = SR.check_AgePoolCutDate()
#    Age_PCD = SR.service_report_AllAssetList_pre[['No_Contract','Age_Project_Start']]
#    check = Age_PCD.merge(Age_SR,left_on='No_Contract',right_on='No_Contract',how='left')
#    check_results = check[check['Age_Project_Start'] != check['Age_Project_Start_sr']]
#    check_results.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName + '/check_AgePoolCutDate.csv')
#
#    for_report = SR.service_report_AllAssetList[#(SR.service_report_AllAssetList['No_Contract'].isin(['#3895914267002','#3772855877003'])) #&
#                                                      # ((SR.service_report_AllAssetList['贷款是否已结清']=='未结清')|(SR.service_report_AllAssetList['贷款是否已结清']=='N')) &
#                                                       #(SR.service_report_AllAssetList['Usage'].isin(['其余种类','其它'])) #&
#                                                       #(SR.service_report_AllAssetList['合格资产'] == '是 ') &
#                                                       ((SR.service_report_AllAssetList['Days_Overdue_Current']>180))#|(SR.service_report_AllAssetList['Days_Overdue_Max']>180)) #.isnull()) #&
#                                                       #(SR.service_report_AllAssetList['ABS资产性质'] == 'ABS循环测试round3_r5') #&
#                                                       #(SR.service_report_AllAssetList['贷款状态'].isnull() ) #&
#                                                       #(SR.service_report_AllAssetList['Type_Five_Category'] == '损失类')
#                                                       #(SR.service_report_AllAssetList['Amount_Outstanding_yuan'] < 0) #&
#                                                       #(pd.to_datetime(SR.service_report_AllAssetList['Dt_Maturity']).dt.year == 2020) &
#                                                       #(pd.to_datetime(SR.service_report_AllAssetList['Dt_Maturity']).dt.month == 4) &
#                                                       #(pd.to_datetime(SR.service_report_AllAssetList['Dt_Maturity']).dt.day == 25)
#                                                       ]
#    for_report.to_csv(path_root  + '/../CheckTheseProjects/' +ProjectName+'/' + 'for_report_check_waived_assets.csv')

    end_time = datetime.datetime.now()   
    time_elapsed = end_time - start_time
    logger.info('Time: %0.4f' % time_elapsed.total_seconds())


if __name__ == '__main__':
    main()
