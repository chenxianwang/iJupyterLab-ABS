# -*- coding: utf-8 -*-
'''
Created on Sun Jun 25 21:20:00 2017

@author: Jonah.Chen
'''
import os
import datetime


path_root = os.path.dirname(os.path.realpath(__file__))
#
DATA_FROME_SYSTEM = False #True
ProjectName = 'ABS13'#ABS9_following'
#asset_pool_name_list = ['ServiceDate_1','ServiceDate_2','ServiceDate_3']
asset_pool_name_list = ['part_1','part_2']

path_project = path_root  + '/DataSource/' + ProjectName

wb_name = path_root  + '/DataSource/' + ProjectName + '/'+ProjectName+'_Results.xlsx'
wb_name_sr = path_root  + '/DataSource/' + ProjectName + '/'+ProjectName+'_ServiceReport.xlsx'

Header_Rename = {'#合同号':'No_Contract','合同号':'No_Contract','订单号':'No_Contract','合同编号':'No_Contract','TO_CHAR(T1.TEXT_CONTRACT_NUMBE':'No_Contract',
                 'SKP_CLIENT':'ID','证件号码':'ID','账户号':'ID','#证件号码':'ID',
                 '职业':'Profession','借款人职业':'Profession','职业_信托':'Profession',
                 '年收入':'Income','年收入(万元)':'Income','借款人年收入':'Income',
                 '省份':'Province',#'G3:省份':'Province',
                 '贷款用途':'Usage','购买商品':'Usage','购买商品_信托':'Usage','G4:商品类型':'Usage',
                 '起始日':'Dt_Start','起息日':'Dt_Start','贷款发放日':'Dt_Start',                 
                 '到期日':'Dt_Maturity','贷款到期日':'Dt_Maturity',                 
                 '合同本金':'Amount_Contract_yuan','合同本金(元)':'Amount_Contract_yuan','合同金额':'Amount_Contract_yuan',
                 '截至封包日剩余本金':'Amount_Outstanding_yuan','截至封包日剩余本金(元)':'Amount_Outstanding_yuan','剩余本金':'Amount_Outstanding_yuan',#'合同余额(元)':'Amount_Outstanding_yuan',
                 'INTEREST_RATE':'Interest_Rate','INTEREST_RATE(%)':'Interest_Rate','合同贷款利率':'Interest_Rate','Interest_Rate_S':'Interest_Rate',
                 '当期逾期天数':'Days_Overdue_Current','当前逾期天数':'Days_Overdue_Current',
                 '初始起算日借款人年龄':'Age_Project_Start','年龄':'Age_Project_Start','借款人年龄':'Age_Project_Start',
                 '出生日期':'出生日期',
                 '封包后的第一个还款日':'first_due_date_after_pool_cut','下一个交易日':'first_due_date_after_pool_cut',
                 '合同天数_x':'LoanTerm','合同天数(天)':'LoanTerm','合同天数':'LoanTerm',
                 '账龄（天数）':'LoanAge','账龄（天数）(天)':'LoanAge','账龄':'LoanAge',
                 '剩余天数':'LoanRemainTerm','剩余天数(天)':'LoanRemainTerm',
                 'SERVICE_FEE_RATE':'SERVICE_FEE_RATE',
                 '信用评分':'Credit_Score_15','信用分数':'Credit_Score_15','CREDIT_SCORE':'Credit_Score_15',
                 '合同期限':'Term_Contract','合同期数':'Term_Contract',
                 '剩余期数':'Term_Remain','剩余期限':'Term_Remain',
                 '五级分类':'Type_Five_Category',
                 '最长逾期天数':'Days_Overdue_Max','历史最大逾期天数':'Days_Overdue_Max',
                 #'IS_NEW_SERVICE_FEE_CALCULATION':'IS_NEW_SERVICE_FEE_CALCULATION',
                 '初始还款日':'Dt_First_Pay','性别':'Gender','家庭状况':'Marriagestate','历史逾期次数':'Overdue_Times','贷款发放时借款人年龄':'Age_Loan_Start',
                 #'业务品种':'Type_Loans','G1:产品类型':'Type_Loans',#'贷款状态':'贷款状态',
                          }

sr_recycle_rename = {'E1:正常回收':'E1：正常回收','E2：提前还款':'E2：提前还款','E3:拖欠回收':'E3；拖欠回收','E4:违约回收':'E4：违约回收','E5:账务处理':'E5：账务处理',
             'F1:正常回收':'F1：正常回收','F2：提前还款':'F2：提前还款','F3:拖欠回收':'F3：拖欠回收','F4:违约回收':'F4：违约回收','F5:账务处理':'F5：账务处理'
             }

Header_Rename_Unique = {'#合同号':'No_Contract',
                 'SKP_CLIENT':'ID',
                 '职业':'Profession',
                 '年收入':'Income',
                 '省份':'Province',
                 '购买商品':'Usage',
                 '起始日':'Dt_Start',              
                 '到期日':'Dt_Maturity',          
                 '合同本金':'Amount_Contract_yuan',
                 '截至封包日剩余本金':'Amount_Outstanding_yuan',
                 'INTEREST_RATE':'Interest_Rate',
                 '当期逾期天数':'Days_Overdue_Current',
                 '初始起算日借款人年龄':'Age_Project_Start',
                 '封包后的第一个还款日':'first_due_date_after_pool_cut',
                 '合同天数':'LoanTerm',
                 '账龄（天数）':'LoanAge',
                 '剩余天数':'LoanRemainTerm',
                 'SERVICE_FEE_RATE':'SERVICE_FEE_RATE',
                 '信用评分':'Credit_Score_15',
                 '合同期限':'Term_Contract','剩余期数':'Term_Remain',
                 '五级分类':'Type_Five_Category',
                 '最长逾期天数':'Days_Overdue_Max',
                 #'IS_NEW_SERVICE_FEE_CALCULATION':'IS_NEW_SERVICE_FEE_CALCULATION',
                 '初始还款日':'Dt_First_Pay',
                 '贷款发放时借款人年龄':'Age_Loan_Start',
                 '性别':'Gender',
                 '家庭状况':'Marriagestate',
                 '历史逾期次数':'Overdue_Times',
                          }

Header_Rename_REVERSE  = {v:k for k,v in Header_Rename_Unique.items()}
#Header_Rename_REVERSE['Credit_Score_15'] = '信用评分'
