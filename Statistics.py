# -*- coding: utf-8 -*-
"""
Created on Thu May 24 17:02:56 2018

@author: jonah.chen
"""
import pandas as pd
from constant import wb_name
from abs_util.util_general import save_to_excel,get_logger,stastics_group_by_d,df_bins_result
import datetime
from Params import Batch_ID


logger = get_logger(__name__)

class Statistics():
    
    def __init__(self,df):

        self.asset_pool = df
        self.max_maturity_date = datetime.date(3000,1,1)
        self.max_province_profession = {}
        
    def general_statistics_1(self):
        logger.info('calculating basic tables')
        df = self.asset_pool
        
        logger.info('Statistics Dimension Setting.....')
        df['Amount_Contract'] = df['Amount_Contract_yuan']#/10000
        df['OutstandingPrincipal'] = df['Amount_Outstanding_yuan']
        df['Amount_Outstanding'] = df['Amount_Outstanding_yuan']#/10000
        df['No_Contract_helper'] = df['No_Contract']
        
        df_unique_ID = df.groupby('ID')\
                       .agg({'No_Contract':'count'})\
                       .reset_index()\
                       .rename(columns = {'No_Contract':'ID_Unique'})
                       
        df_unique_NO = df.groupby('No_Contract_helper')\
               .agg({'No_Contract':'count'})\
               .reset_index()\
               .rename(columns = {'No_Contract_helper':'NO_Unique'})
        
        b_s_1 = {'贷款笔数':df['No_Contract'].count(),
                 '合同数':df_unique_NO['NO_Unique'].count(),
               '借款人数量':df_unique_ID['ID_Unique'].count(),
               '合同初始金额总额（万元）':df['Amount_Contract'].sum(),
               '未偿本金余额总额（万元）':df['Amount_Outstanding'].sum(),
               '借款人平均未偿本金余额（万元）':df['Amount_Outstanding'].sum() / df_unique_ID['ID_Unique'].count(),
               '单笔贷款最高本金余额（万元）':df['Amount_Outstanding'].max(),
               '单笔贷款平均本金余额（万元）': df['Amount_Outstanding'].sum() / df['No_Contract'].count(),
               '单笔贷款最高合同金额（万元）': df['Amount_Contract'].max(),                                      
               '单笔贷款平均合同金额（万元）':df['Amount_Contract'].sum() / df['No_Contract'].count()
               }
    
        b_s_2 = {'加权平均贷款合同期限（天）':(df['LoanTerm']*df['Amount_Outstanding']).sum()/df['Amount_Outstanding'].sum(),
                 '加权平均贷款账龄（天）':(df['LoanAge']*df['Amount_Outstanding']).sum()/df['Amount_Outstanding'].sum(),
                 '加权平均贷款剩余期限（天）':(df['LoanRemainTerm']*df['Amount_Outstanding']).sum()/df['Amount_Outstanding'].sum(),
                 '单笔贷款最长剩余期限（天）':df['LoanRemainTerm'].max(),
                 '单笔贷款最短剩余期限（天）':df['LoanRemainTerm'].min(),
                 '单笔贷款最长期限（天）':df['LoanTerm'].max(),
                 '单笔贷款最短期限（天）':df['LoanTerm'].min()
                }
    
        #TODO: Complete b_s_3
        try:
            b_s_3 = {'加权平均贷款年利率（%）':(df['Interest_Rate']*df['Amount_Outstanding']).sum()/df['Amount_Outstanding'].sum() * 100,
                 '单笔贷款最高年利率（%）':df['Interest_Rate'].max() * 100,
                 '单笔贷款最低年利率（%）':df['Interest_Rate'].min() * 100,    
                 '加权平均贷款月度内部收益率（%）':(df['Interest_Rate']*df['Amount_Outstanding']).sum()/df['Amount_Outstanding'].sum() * 100 /12,
                 '加权平均信用评分':(df['Credit_Score']*df['Amount_Outstanding']).sum()/df['Amount_Outstanding'].sum()   
                 }
        
        except(KeyError):
            b_s_3 = {'加权平均贷款年利率（%）':(df['Interest_Rate']*df['Amount_Outstanding']).sum()/df['Amount_Outstanding'].sum() * 100,
                 '单笔贷款最高年利率（%）':df['Interest_Rate'].max() * 100,
                 '单笔贷款最低年利率（%）':df['Interest_Rate'].min() * 100,    
                 '加权平均贷款月度内部收益率（%）':(df['Interest_Rate']*df['Amount_Outstanding']).sum()/df['Amount_Outstanding'].sum() * 100 /12,
                 }
        
        
        try:
            b_s_4 = {
                '借款人加权平均年龄':(df['Age_Project_Start']*df['Amount_Outstanding']).sum()/df['Amount_Outstanding'].sum(),
                 '30-40岁借款人贷款余额占比（%）':df[(df['Age_Project_Start']>30) & (df['Age_Project_Start']<=40)]\
                                                  ['Amount_Outstanding'].sum() / df['Amount_Outstanding'].sum() * 100,                
                 
                 '借款人加权平均年收入（万元）':(df['Income']*df['Amount_Outstanding']).sum()/df['Amount_Outstanding'].sum() / 10000 ,
                }
        except(KeyError):b_s_4 = {}
#    
        df_b_s_list = []
        for b_s_dict in [b_s_1,b_s_2,b_s_3,b_s_4]:
            df_b_s = pd.DataFrame(list(b_s_dict.items()),columns=['项目','数值'])
            df_b_s_list.append(df_b_s)
        save_to_excel(df_b_s_list,'statistics'+Batch_ID,wb_name)

        #print(df_unique_ID[:5])
        #df_ID_cnt_gt_1 = df_unique_ID[df_unique_ID['ID_Unique'] > 1]
        #df_ID_cnt_gt_1.to_csv('df_ID_cnt_gt_1.csv')
        
    def loop_Ds_ret_province_profession(self,Distribution_By_Category,Distribution_By_Bins):
        
        logger.info('Calculating distribution tables' )
        
        df = self.asset_pool
        
        logger.info('Statistics Dimension Setting.....')
        df['Credit'] = df['Amount_Contract_yuan']
        df['Amount_Contract'] = df['Amount_Contract_yuan']#/10000
        df['OutstandingPrincipal'] = df['Amount_Outstanding_yuan']
        df['Amount_Outstanding'] = df['Amount_Outstanding_yuan']#/10000
        
        dimension_category_list = []
        max_province_profession = {}
        for dimension_category in Distribution_By_Category:
            logger.info('Calculating for ' + dimension_category )
            try:
                group_this_d = stastics_group_by_d(df,dimension_category,dimension_category)
                dimension_category_list.append(group_this_d)
                if dimension_category in ['Province','Profession']:
                    max_province_profession[dimension_category] = max(group_this_d['本金余额占比'])
            except(KeyError):
                logger.info(dimension_category + ' Calculation failed.' )
            except(ValueError):
                logger.info(dimension_category + ' Calculation failed.' )
                continue
                
        save_to_excel(dimension_category_list,'statistics'+Batch_ID,wb_name)
        
        dimension_bins_list = []
        for dimension_bins in Distribution_By_Bins.keys():
            logger.info('Calculating for ' + dimension_bins )
            try:
                group_this_d_bins = df_bins_result(df,dimension_bins,Distribution_By_Bins[dimension_bins])
                group_this_d_bins[dimension_bins] = group_this_d_bins[dimension_bins].astype(str)
                dimension_bins_list.append(group_this_d_bins)
            except(KeyError): 
                logger.info('Calculating for ' + dimension_bins + 'Failed' ) 
                continue
        save_to_excel(dimension_bins_list,'statistics'+Batch_ID,wb_name)
        
        self.max_province_profession = max_province_profession
        
    def general_statistics_2(self):

        b_s_5 = self.max_province_profession
        
        b_s_6 = {'逾期次数为0次的占比（%）':'',
                 '逾期次数在5次之内的占比（%）':'',
                 '本期资产支持证券入池资产共涉及借款人【】位，':'',
                 '其中【】位借款人在发起机构的各笔贷款未全部入池':''
                }
    
        df_b_s_list = []
        for b_s_dict in [b_s_5,b_s_6]:   
            df_b_s = pd.DataFrame(list(b_s_dict.items()),columns=['项目','数值'])
            df_b_s_list.append(df_b_s)
        save_to_excel(df_b_s_list,'statistics'+Batch_ID,wb_name)
        
        
    def cal_income2debt_by_ID(self):
        
        df = self.asset_pool
                
        logger.info('WA_Income2Debt_by_ID.....')
        df['Amount_Contract'] = df['Amount_Contract_yuan']#/10000
        df['OutstandingPrincipal'] = df['Amount_Outstanding_yuan']
        df['Amount_Outstanding'] = df['Amount_Outstanding_yuan']#/10000
        
        df['weight'] = df['Amount_Outstanding'] / df.groupby('ID')['Amount_Outstanding'].transform('sum')
        df['wa_Term_Remain'] = df['Term_Remain'] * df['weight']
        Income2Debt_by_ID = df.groupby('ID')\
                       .agg({'Income':'mean','wa_Term_Remain':'sum','Amount_Outstanding':'sum'})\
                       .reset_index()
    
        WA_Income2Debt_by_ID = (Income2Debt_by_ID['Income']/12*Income2Debt_by_ID['wa_Term_Remain']).sum() / (Income2Debt_by_ID['Amount_Outstanding']).sum() / 10000
    
        WA_Income2Debt = {'加权平均债务收入比':WA_Income2Debt_by_ID}
        df_WA_Income2Debt = pd.DataFrame(list(WA_Income2Debt.items()),columns=['项目','数值'])
    
        save_to_excel(df_WA_Income2Debt,'statistics'+Batch_ID,wb_name)