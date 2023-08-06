import numpy as np
import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

def del_industry_with_less_than_three_stocks(data, path_prfx='../../'):
    """
    只适用于行业轮动。如果某个截面上的某个行业包含的成分股个数少于三只, 则删除这条数据。注意索引一定要是日期+资产
    """
    stock_num_of_industry = pd.read_csv(path_prfx+'../data/衍生数据/富国行业每期包含股票数-实时更新.csv', parse_dates=True, index_col=[0, 1])
    mask = (stock_num_of_industry>3)['Number']  # 大于三只股票的行业，索引为日期+行业
    return data.mask(~mask, np.nan).dropna()

def read_ind_rets(path_prfx='../../'):
    """
    读取富国行业收益率数据，索引为日期+行业，列为Return
    """
    ind_rets = pd.read_pickle(path_prfx+'../data/衍生数据/富国行业收益率-实时更新.pkl')
    return ind_rets

def read_stock_rets(path_prfx='../../'):
    """
    读取股票收益率数据，索引为日期+股票，列为Return
    """
    stock_rets = pd.read_pickle(path_prfx+'../data/衍生数据/个股收益率-实时更新.pkl')
    return stock_rets

def read_ind_factor(path, path_prfx='../../'):
    """
    读取行业因子数据
    """
    ind_factor = pd.read_excel(path_prfx+path)
    ind_factor['Date'] = pd.to_datetime(ind_factor['END_DATE'], format='%Y%m%d') # 转换日期格式
    try:
        ind_factor = ind_factor[['Date', 'NAME', 'Alpha']] # 只取Alpha
    except:
        ind_factor = ind_factor[['Date', 'NAME', 'VALUE']] # 没有Alpha就取VALUE
    ind_factor.columns = ['Date', 'Industry', 'Factor'] # 列名重命名
    ind_factor = ind_factor.set_index(['Date', 'Industry']) # 设置索引
    return ind_factor

def read_stock_factor(path, path_prfx='../../'):
    """
    读取股票因子数据
    """
    stock_factor = pd.read_excel(path_prfx+path)
    stock_factor['NAME'] = stock_factor['NAME'].apply(lambda x: str(x).zfill(6))
    stock_factor['Date'] = pd.to_datetime(stock_factor['END_DATE'], format='%Y%m%d') # 转换日期格式
    try:
        stock_factor = stock_factor[['Date', 'NAME', 'Alpha']] # 只取Alpha
    except:
        stock_factor = stock_factor[['Date', 'NAME', 'VALUE']] # 没有Alpha就取VALUE
    stock_factor.columns = ['Date', 'Stock', 'Factor'] # 列名重命名
    stock_factor = stock_factor.set_index(['Date', 'Stock']) # 设置索引
    return stock_factor

def read_ind_sector(path_prfx='../../'):
    """
    读取行业和板块数据
    """
    sector_data = pd.read_excel(path_prfx + '../data/富国行业数据/富国行业分类.xlsx').drop(columns=['模拟ETF', '申万3级', '新1级行业']).drop_duplicates()
    sector_data.columns = ['Industry', 'Sector']
    return sector_data

def read_stock_sector(path_prfx='../../'):
    """
    读取股票和板块数据
    """
    # 读取个股和板块对应数据
    stock_sector = pd.read_pickle(path_prfx+'../data/衍生数据/个股所属板块-实时更新.pkl')
    return stock_sector

def read_ind_data(factor_path, path_prfx='../../', if_sector=True, if_del_less_three=True, del_sector_list=[], del_ind_list=[]):
    """读取行业轮动需要的数据：行业因子、行业收益率、行业所属板块"""
    factor = read_ind_factor(path=factor_path, path_prfx=path_prfx)
    rets = read_ind_rets(path_prfx=path_prfx)
    if if_sector:
        sector_data = read_ind_sector(path_prfx=path_prfx)
    else:
        sector_data = None
    if if_del_less_three:
        factor = del_industry_with_less_than_three_stocks(factor, path_prfx=path_prfx)
        rets = del_industry_with_less_than_three_stocks(rets, path_prfx=path_prfx)
    if len(del_sector_list) != 0:
        tmp = pd.merge(factor.reset_index(), sector_data, on='Industry', how='left')
        tmp = tmp[tmp.Sector not in del_sector_list]
        factor = tmp[["Date", "Industry", "Factor"]].set_index(['Date', 'Industry'])
    if len(del_ind_list) != 0:
        factor = factor.query("Industry not in @del_ind_list")
    return factor, rets, sector_data

def read_stock_data(factor_path, path_prfx='../../', if_sector=True, del_sector_list=[]):
    """读取选股需要的数据：股票因子、股票收益率、股票所属板块"""
    factor = read_stock_factor(path=factor_path, path_prfx=path_prfx)
    rets = read_stock_rets(path_prfx=path_prfx)
    if if_sector:
        sector_data = read_stock_sector(path_prfx=path_prfx)
    else:
        sector_data = None
    if len(del_sector_list) != 0:
        tmp = pd.merge(factor.reset_index(), sector_data, on=['Date', 'Stock'], how='left')
        tmp = tmp[tmp.Sector not in del_sector_list]
        factor = tmp[["Date", "Stock", "Factor"]].set_index(['Date', 'Stock'])
    return factor, rets, sector_data