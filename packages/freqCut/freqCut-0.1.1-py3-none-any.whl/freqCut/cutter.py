# -*- coding: utf-8 -*-
"""
Created on Tue Jun 14 14:10:08 2022

@author: man Yip
"""
import numpy as np
import pandas as pd
from DagLpDp import DAGLP

def value_counts_weight(data,weight=None):
    data = pd.DataFrame({'data':data})
    if weight is not None:
        weight = pd.DataFrame({'weight':weight},index=data.index)
    else:
        weight = pd.DataFrame({'weight':1},index=data.index)    
    df = pd.concat([data,weight],axis=1)
    distr = df.groupby('data',dropna=False)['weight'].sum()
    distr = distr / distr.sum()
    return distr

def trancate_by_distr(distr,min_distr):
    tmp = distr.loc[distr.index.notna()]
    curr=0
    rm_points = []
    for k,v in tmp.items():
        curr+=v
        if curr < min_distr:
            rm_points.append(k)
        else:
            rm_points.append(k) #由于是右开区间，所以需要游标多走一位
            break
    
    tmp2 = tmp.iloc[::-1]
    curr=0
    for k,v in tmp2.items():
        curr+=v
        if curr < min_distr:
            rm_points.append(k)
        else:
            break        
    return list(tmp.loc[~tmp.index.isin(rm_points)].index.values)

def gen_connect_table(legal_points,distr,threshold_distr,min_distr):
    distr_notna = distr.loc[distr.index.notna()]
    ma = distr_notna.keys().max() 
    distr_notna[ma + 0.001] = 0   
    legal_points = legal_points+[ma + 0.001]     
    tables={}
    curr_from = distr_notna.keys().min()
    cursor = 0
    while(cursor < len(legal_points)):
        for end in legal_points[cursor:]:
            v = distr_notna[curr_from:end].sum() - distr_notna[end]
            if v >= min_distr:
                tables[(curr_from,end)] = -1 * (np.abs(v-threshold_distr)**2)
        curr_from = legal_points[cursor]  
        cursor+=1
    return tables

def freq_cut(data,threshold_distr,min_distr,weight=None):
    if threshold_distr > 1:
        threshold_distr = 1/threshold_distr
    distr = value_counts_weight(data,weight)
    legal_points = trancate_by_distr(distr,min_distr)
    tables = gen_connect_table(legal_points,distr,threshold_distr,min_distr)
    dlp = DAGLP(tables)
    fc = [v for k,v in dlp.nodePV.items() if k in dlp.ends][0][0]
    bins = ''
    for i,v in enumerate(fc):
        if i < len(fc)-2:
            tmp = '[%d,%d), '%(v,fc[i+1])
            bins+=tmp
        elif i == len(fc)-2:
            tmp = '[%d,%d]'%(v,distr.keys().max())
            bins+=tmp   
    return bins

def cut_by_bins(data,bins):
    data_bin = pd.Series(data)
    mi = data_bin.min()
    ma = data_bin.max()
    sbins = data_bin.copy()
    sbins = sbins.apply(str)
    binsarr = bins.split(', ')
    for i,b in enumerate(binsarr):
        coma = b.index(',')
        v1 = float(b[1:coma])
        if i == 0 and mi < v1:
            v1 = mi
            b = '%s%s%s'%(b[0],v1,b[coma:])
            coma = b.index(',')
            
        if b[0] =='[':
            cond1 = data_bin>=v1
        elif b[0]=='(':
            cond1 = data_bin>v1
        
        v2 = float(b[coma+1:-1])
        if i == len(binsarr)-1 and ma > v2:
            v2 = ma
            b = '%s%s%s'%(b[:coma+1],v2,b[-1])
            
        if b[-1] ==']':
            cond2 = data_bin <= v2
        elif b[-1]==')':
            cond2 = data_bin < v2
        sbins.loc[cond1 & cond2]=b
    return sbins