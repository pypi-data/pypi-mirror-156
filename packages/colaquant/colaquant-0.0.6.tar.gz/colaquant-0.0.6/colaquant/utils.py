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

def read_ind_factor(path, path_prfx='../../'):
    """
    读取行业因子数据
    """
    ind_factor = pd.read_excel(path_prfx+path)
    ind_factor['Date'] = pd.to_datetime(ind_factor['END_DATE'], format='%Y%m%d') # 转换日期格式
    ind_factor = ind_factor[['Date', 'NAME', 'Alpha']] # 只取Alpha
    ind_factor.columns = ['Date', 'Industry', 'Factor'] # 列名重命名
    ind_factor = ind_factor.set_index(['Date', 'Industry']) # 设置索引
    return ind_factor

def read_ind_sector(path_prfx='../../'):
    """
    读取行业和板块数据
    """
    sector_data = pd.read_excel(path_prfx + '../data/富国行业数据/富国行业分类.xlsx').drop(columns=['模拟ETF', '申万3级', '新1级行业']).drop_duplicates()
    sector_data.columns = ['Industry', 'Sector']
    return sector_data

def read_ind_data(factor_path, path_prfx='../../', if_sector=True, if_del_less_three=True, del_sector_list=[], del_ind_list=[]):
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