# -*- coding: utf-8 -*-
"""
Created on Mon May 28 13:42:18 2018

@author: jonah.chen
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
logger = get_logger(__name__)

class ServiceReport():
    
    def __init__(self,name,trust_effective_date,report_period):
        self.name = name
        self.trust_effective_date = trust_effective_date
        
        self.service_report_AllAssetList_pre = pd.DataFrame()
        
        self.service_report_AllAssetList = pd.DataFrame()
        self.service_report_DefaultAssetList = pd.DataFrame()
        self.service_report_WaivedAssetList = pd.DataFrame()
        self.service_report_RedemptionAssetList = pd.DataFrame()
        
        self.for_report = pd.DataFrame()
        
        self.report_period = report_period
        
        
    def get_ServiceReportAssetsList(self,FilePath,AllAssetList_previous,AllAssetList,DefaultAssetList,WaivedAssetList,RedemptionAssetList):
        
        if AllAssetList_previous != '':
            for Pool_index,Pool_name in enumerate(AllAssetList_previous):
                logger.info('Getting AllAssetList_pre part ' + str(Pool_index+1) + '...')
                AssetPoolPath_all_pre = path_root +'/../CheckTheseProjects/'+self.name+'/ServiceReportList/'+ '/' + FilePath + '/' + Pool_name + '.csv'
                try:
                    AssetPool_all_pre = pd.read_csv(AssetPoolPath_all_pre,encoding = 'utf-8') 
                except:
                    AssetPool_all_pre = pd.read_csv(AssetPoolPath_all_pre,encoding = 'gbk') 
                self.service_report_AllAssetList_pre = self.service_report_AllAssetList_pre.append(AssetPool_all_pre,ignore_index=True)
            self.service_report_AllAssetList_pre = self.service_report_AllAssetList_pre.rename(columns = Header_Rename) 
                            
            #print(isinstance(AssetPool_all_pre['订单号'][0],np.int64))
            if isinstance(self.service_report_AllAssetList_pre['No_Contract'][0],np.int64) == False:pass
            else: self.service_report_AllAssetList_pre['No_Contract'] = '#' + self.service_report_AllAssetList_pre['No_Contract'].astype(str)  
            
        for Pool_index,Pool_name in enumerate(AllAssetList):
            logger.info('Getting AllAssetList part ' + str(Pool_index+1) + '...')
            AssetPoolPath_all = path_root +'/../CheckTheseProjects/'+self.name+'/ServiceReportList/'+ '/' + FilePath + '/' + Pool_name + '.csv'
            try:
                AssetPool_all = pd.read_csv(AssetPoolPath_all,encoding = 'utf-8') 
            except:
                AssetPool_all = pd.read_csv(AssetPoolPath_all,encoding = 'gbk') 
            self.service_report_AllAssetList = self.service_report_AllAssetList.append(AssetPool_all,ignore_index=True)
        self.service_report_AllAssetList = self.service_report_AllAssetList.rename(columns = Header_Rename)
                
        if isinstance(self.service_report_AllAssetList['No_Contract'][0],np.int64) == False:pass
        else: self.service_report_AllAssetList['No_Contract'] = '#' + self.service_report_AllAssetList['No_Contract'].astype(str)   
                    
        if DefaultAssetList != '':
            logger.info('Getting DefaultAssetList...')
            AssetPoolPath_Default = path_root +'/../CheckTheseProjects/'+self.name+'/ServiceReportList/'+ FilePath + '/' + DefaultAssetList + '.csv'
            try:
                AssetPool_Default = pd.read_csv(AssetPoolPath_Default,encoding = 'utf-8') 
            except:
                AssetPool_Default = pd.read_csv(AssetPoolPath_Default,encoding = 'gbk')
            self.service_report_DefaultAssetList = self.service_report_DefaultAssetList.append(AssetPool_Default,ignore_index=True)

        if WaivedAssetList != '':
            logger.info('Getting WaivedAssetList...')
            AssetPoolPath_Waive = path_root +'/../CheckTheseProjects/'+self.name+'/ServiceReportList/' + FilePath + '/' + WaivedAssetList + '.csv'
            try:
                AssetPool_Waive = pd.read_csv(AssetPoolPath_Waive,encoding = 'utf-8') 
            except:
                AssetPool_Waive = pd.read_csv(AssetPoolPath_Waive,encoding = 'gbk') 

                if isinstance(AssetPool_Waive['订单号'][0],np.int64) == False:pass
                else: AssetPool_Waive['订单号'] = '#' + AssetPool_Waive['订单号'].astype(str)   
                
            self.service_report_WaivedAssetList = self.service_report_WaivedAssetList.append(AssetPool_Waive,ignore_index=True)
            self.service_report_WaivedAssetList = self.service_report_WaivedAssetList.rename(columns = Header_Rename)
        
        if RedemptionAssetList != '':
            logger.info('Getting RedemptionAssetList...')
            AssetPoolPath_redemp = path_root +'/../CheckTheseProjects/'+self.name+'/ServiceReportList/'+ FilePath + '/' + RedemptionAssetList + '.csv'
            #print(AssetPoolPath_redemp[:5])
            try:
                AssetPool_redemp = pd.read_csv(AssetPoolPath_redemp,encoding = 'utf-8') 
            except:
                AssetPool_redemp = pd.read_csv(AssetPoolPath_redemp,encoding = 'gbk') 

            if isinstance(AssetPool_redemp['订单号'][0],np.int64) == False:pass
            else: AssetPool_redemp['订单号'] = '#' + AssetPool_redemp['订单号'].astype(str)  
                
            self.service_report_RedemptionAssetList = self.service_report_RedemptionAssetList.append(AssetPool_redemp,ignore_index=True)

            self.service_report_RedemptionAssetList = self.service_report_RedemptionAssetList.rename(columns = Header_Rename)
        
        
    def add_SeviceRate_From(self,df):
        
        logger.info('Adding Service Fee Rate...')
        #self.for_report['No_Contract'] = '#' + self.for_report['No_Contract'].astype(str)
        self.for_report = self.for_report.merge(df,left_on='No_Contract',right_on='No_Contract',how='left')
        #self.for_report.to_csv('for_report_cf_check.csv')
        print("for_report['SERVICE_FEE_RATE'].sum(): ",self.for_report['SERVICE_FEE_RATE'].sum())

    def check_NextPayDate(self):
        logger.info('check_NextPayDate...')
        DetailList = self.service_report_AllAssetList
        NextPayDate = DetailList[#(~self.service_report_AllAssetList['订单号'].isin(self.service_report_RedemptionAssetList['订单号'])) &
                                (DetailList['Amount_Outstanding_yuan'] > 0) &
                                (DetailList['first_due_date_after_pool_cut'] == '3000/1/1') &
                                (pd.to_datetime(DetailList['Dt_Maturity']).dt.date <= TrustEffectiveDate )
                               ]
        NextPayDate.to_csv(path_root  + '/../CheckTheseProjects/' +self.name+'/' + 'check_NextPayDate.csv')
        
    
    def check_Redemption_price(self):
       logger.info('check_Redemption_price......')
       AllDetailList = self.service_report_AllAssetList[['No_Contract','Amount_Outstanding_yuan']]
       RedemptionDetailList = self.service_report_RedemptionAssetList[['订单号','赎回贷款债权的未偿本金余额']]
       
       #AllDetailList['#合同号'] = "#" + AllDetailList['No_Contract'].astype(str)
       #RedemptionDetailList['#合同号'] = "#" + RedemptionDetailList['订单号'].astype(str)
       
       logger.info('left Merging...')
       R_A = RedemptionDetailList.merge(AllDetailList,left_on='订单号',right_on='No_Contract',how='left')
       R_A_D = R_A[R_A['Amount_Outstanding_yuan'] != R_A['赎回贷款债权的未偿本金余额']]
       R_A_D.to_csv(path_root  + '/../CheckTheseProjects/' +self.name+'/' + 'R_A_D.csv')
    
    
    def check_OutstandingPrincipal(self):
        logger.info('check_OutstandingPrincipal......')
        DetailList = self.service_report_AllAssetList#[(self.service_report_AllAssetList['入池时间'] == '2018/12/01')]
        
#        DetailList = DetailList[['No_Contract','Amount_Outstanding_yuan','B1：正常回收','B2：提前还款','B3：拖欠回收','B4：违约回收','B5:账务处理']]
#        DetailList[['Amount_Outstanding_yuan','B1：正常回收','B2：提前还款','B3：拖欠回收','B4：违约回收','B5:账务处理']] = DetailList[['Amount_Outstanding_yuan','B1：正常回收','B2：提前还款','B3：拖欠回收','B4：违约回收','B5:账务处理']].where(DetailList[['Amount_Outstanding_yuan','B1：正常回收','B2：提前还款','B3：拖欠回收','B4：违约回收','B5:账务处理']]!=0,0)
#        DetailList = DetailList.rename(columns = {'Amount_Outstanding_yuan':'Amount_Outstanding'})        
#        if '调整回收款'.isin(list(DetailList.columns.values)):pass
#        else:DetailList['调整回收款'] = 0                
#        DetailList['剩余本金_poolcutdate_calc'] = DetailList['Amount_Outstanding']+DetailList['B1：正常回收']+DetailList['B2：提前还款']+DetailList['B3：拖欠回收']+DetailList['B4：违约回收']+DetailList['B5:账务处理'] + DetailList['调整回收款']
#        
        header_name_dict = {k:k.replace(":","：") for k in list(DetailList.columns.values) }    
        DetailList = DetailList.rename(columns = {k:v for k,v in header_name_dict.items()})    
        DetailList = DetailList[['No_Contract','Amount_Outstanding_yuan','本金：正常回收','本金：提前还款','本金：拖欠回收','本金：违约回收','本金：账务处理','调整回收款']]
        DetailList[['Amount_Outstanding_yuan','本金：正常回收','本金：提前还款','本金：拖欠回收','本金：违约回收','本金：账务处理','调整回收款']] = DetailList[['Amount_Outstanding_yuan','本金：正常回收','本金：提前还款','本金：拖欠回收','本金：违约回收','本金：账务处理','调整回收款']].where(DetailList[['Amount_Outstanding_yuan','本金：正常回收','本金：提前还款','本金：拖欠回收','本金：违约回收','本金：账务处理','调整回收款']]!=0,0)
        DetailList = DetailList.rename(columns = {'Amount_Outstanding_yuan':'Amount_Outstanding'})
        DetailList['剩余本金_poolcutdate_calc'] = DetailList['Amount_Outstanding']+DetailList['本金：正常回收']+DetailList['本金：提前还款']+DetailList['本金：拖欠回收']+DetailList['本金：违约回收']+DetailList['本金：账务处理'] + DetailList['调整回收款']
#        
#        DetailList = self.service_report_RedemptionAssetList
#        DetailList['No_Contract'] = '#' + DetailList['订单号'].astype(str)
#        DetailList = DetailList[['No_Contract','赎回贷款债权的未偿本金余额','本金']]
#        DetailList[['本金']] = DetailList[['本金']].where(DetailList[['本金']]!=0,0)
#        DetailList = DetailList.rename(columns = {'赎回贷款债权的未偿本金余额':'Amount_Outstanding'})
#        DetailList['剩余本金_poolcutdate_calc'] = DetailList['Amount_Outstanding']+DetailList['本金']
        
        try:return DetailList,self.service_report_WaivedAssetList[['No_Contract','本金减免金额']]
        except(KeyError):return DetailList,self.service_report_WaivedAssetList[['No_Contract','减免金额']]
     
    def check_AgePoolCutDate(self):
        logger.info('check_AgePoolCutDate......')
        DetailList = self.service_report_AllAssetList
        DetailList = DetailList[['No_Contract','Age_Project_Start']]
        DetailList = DetailList.rename(columns = {'Age_Project_Start':'Age_Project_Start_sr'})
        return DetailList
        
    
    def check_LoanAging(self):
        logger.info('check_LoanAging...')
        DetailList = self.service_report_AllAssetList[self.service_report_AllAssetList['贷款是否已结清']=='N'][['No_Contract','Dt_Start','Dt_Maturity','Days_Overdue_Current','LoanAge','LoanTerm','LoanRemainTerm']]
        DetailList['TrustEffectiveDate'] = TrustEffectiveDate
        DetailList['账龄_Jonah'] = (DetailList['TrustEffectiveDate']+ relativedelta(days=-1)).where(DetailList['TrustEffectiveDate'] <= pd.to_datetime(DetailList['Dt_Maturity']).dt.date + relativedelta(days=1),pd.to_datetime(DetailList['Dt_Maturity']).dt.date)  \
                                    - pd.to_datetime(DetailList['Dt_Start']).dt.date 
        DetailList['账龄_Jonah'] = (DetailList['账龄_Jonah'] / np.timedelta64(1, 'D')).astype(int)
        DetailList = DetailList[DetailList['账龄_Jonah'] != DetailList['LoanAge']]
        DetailList.to_csv(path_root  + '/../CheckTheseProjects/' +self.name+'/' + 'check_账龄_Jonah.csv')

    def check_ContractTerm(self):
        logger.info('check_ContractTerm...')
        DetailList = self.service_report_AllAssetList[self.service_report_AllAssetList['贷款是否已结清']=='N'][['No_Contract','Dt_Start','Dt_Maturity','Days_Overdue_Current','LoanAge','LoanTerm','LoanRemainTerm']]
        DetailList['合同天数_Jonah'] = pd.to_datetime(DetailList['Dt_Maturity']).dt.date - pd.to_datetime(DetailList['Dt_Start']).dt.date 
        DetailList['合同天数_Jonah'] = (DetailList['合同天数_Jonah'] / np.timedelta64(1, 'D')).astype(int)
        
        #DetailList['合同天数_Jonah'] = DetailList['LoanAge'] + DetailList['LoanRemainTerm']
        
        DetailList = DetailList[DetailList['合同天数_Jonah'] != DetailList['LoanTerm']]
        
        DetailList.to_csv(path_root  + '/../CheckTheseProjects/' +self.name+'/' + 'check_合同天数_Jonah.csv')
    
    def closed_with_outstandingprincipal(self):
        logger.info('closed_with_outstandingprincipal...')
        DetailList = self.service_report_AllAssetList[(self.service_report_AllAssetList['贷款是否已结清']=='N') & 
                                                       (self.service_report_AllAssetList['Type_Five_Category']=='XNA')
                                                        ]
        DetailList.to_csv(path_root  + '/../CheckTheseProjects/' +self.name+'/' + 'check_五级分类_Jonah.csv')
        save_to_excel(group_by_d(self.service_report_AllAssetList,['贷款是否已结清','Type_Five_Category'],'Amount_Outstanding_yuan'),'service_report',wb_name_sr)
    
    
    def select_by_ContractNO(self,FilePath,exclude_or_focus,these_assets):
        
        #self.asset_pool = self.AP.exclude_or_focus_by_ContractNo(exclude_or_focus,these_assets)
        logger.info('Reading Assets_to_' + exclude_or_focus + '....')
        path_assets = path_root +'/../CheckTheseProjects/'+self.name+'/ServiceReportList/'+ '/' + FilePath + '/' + these_assets + '.csv'
        assets_to_exclude_or_focus = pd.read_csv(path_assets,encoding = 'gbk')
        
        logger.info(exclude_or_focus + 'ing ...') 
        if exclude_or_focus == 'exclude':
            assets = self.service_report_AllAssetList[~self.service_report_AllAssetList['No_Contract'].isin(assets_to_exclude_or_focus['#合同号'])]
        #assets = self.asset_pool[self.asset_pool['ReverseSelection_Flag'].isin(assets_to_exclude_or_focus['ReverseSelection_Flag'])]
        #assets_to_exclude_or_focus['#合同号'] = '#' + assets_to_exclude_or_focus['合同号'].astype(str)       
            return assets
        else:
            assets = self.service_report_AllAssetList[self.service_report_AllAssetList['No_Contract'].isin(assets_to_exclude_or_focus['#合同号'])]
        #assets = self.asset_pool.rename(columns = DWH_header_REVERSE_rename) 
        #assets.to_csv('1stRevolvingPool.csv')
            logger.info(exclude_or_focus + ' is done.')
            assets.to_csv(path_root  + '/../CheckTheseProjects/' +self.name+'/' + '_focus_these.csv')
    
    def service_report_cal(self):
        logger.info('service_report_cal...')
        
#        self.service_report_AllAssetList = self.service_report_AllAssetList[(self.service_report_AllAssetList['贷款是否已结清'] == 'N') 
#                                                  #&(self.service_report_AllAssetList['入池时间'] == '2018/8/1')
#                                                  ]

        #self.service_report_AllAssetList = self.service_report_AllAssetList.merge(self.service_report_AllAssetList_pre[['订单号','剩余期数']],left_on= 'No_Contract',right_on = '订单号',how='left')
        #self.service_report_AllAssetList = self.service_report_AllAssetList[self.service_report_AllAssetList['剩余期数'] - self.service_report_AllAssetList['Term_Remain'] > 1]
        
        
        cal_table_4_1(self.service_report_AllAssetList,wb_name_sr)
        #cal_table_4_2(self.service_report_DefaultAssetList,self.wb_save_results)
        #cal_table_4_3(ServiceReportListPath_D,self.pool_cut_volumn,self.report_period,self.wb_to_save_results)
        
        #cal_table_5(ServiceReportListPath_D,self.wb_to_save_results)
        
#        _calcDate = self.trust_effective_date + relativedelta(months=self.report_period-1)
#        calcDate = date(_calcDate.year,_calcDate.month,1)
        
        #cal_table_6(self.service_report_AllAssetList,self.trust_effective_date,wb_name_sr)
        
        cal_table_7(self.service_report_AllAssetList,wb_name_sr)
        #cal_table_10(self.for_report,self.wb_save_results)    
        
        
        