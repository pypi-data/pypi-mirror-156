import numpy as np
import pandas as pd

def excess_returns_by_group(factor_data_ex, by_sector=False):
    """每期每个组别的超额收益率"""
    if by_sector:
        grouper = ["Sector", "Date", "Group"]
    else:
        grouper = ["Date", "Group"]
    excess_rets = factor_data_ex.groupby(grouper)["M1"].sum().unstack()
    return excess_rets

def excess_nav_by_group(factor_data_ex, by_sector=False):
    """每期每个组别的超额净值"""
    excess_rets = excess_returns_by_group(factor_data_ex, by_sector)
    
    if by_sector:
        excess_nav = excess_rets.groupby("Sector").cumsum()
    else:
        excess_nav = excess_rets.cumsum()
    excess_nav = excess_nav.join(pd.Series(excess_nav.iloc[:,-1] - excess_nav.iloc[:,0], name="Long-Short"))
    return excess_nav

def stats_alpha_by_group(factor_data_ex, by_sector=False):
    """
    计算因子的alpha。各组合的收益率减去基准(行业等权组合)的收益率
    """
    excess_rets = excess_returns_by_group(factor_data_ex, by_sector)
    
    if by_sector:
        # 整体表现
        alpha = excess_rets.groupby("Sector").sum()
        
        # 分年分组表现
        grouper = ["Sector", excess_rets.index.get_level_values(1).year]
        alpha_by_year = excess_rets.groupby(grouper).sum() 
        
    else:
        # 整体表现
        alpha = excess_rets.sum() 
        
        # 分年分组表现
        grouper = [excess_rets.index.year]
        alpha_by_year = excess_rets.groupby(grouper).sum() 
    
    return alpha, alpha_by_year

def stats_alpha_by_group_and_month(factor_data_ex, by_sector=False):
    """
    计算因子分组分月的alpha
    """
    excess_rets = excess_returns_by_group(factor_data_ex, by_sector)
    
    if by_sector:
        grouper = ["Sector", excess_rets.index.get_level_values(1).year, excess_rets.index.get_level_values(1).month]
        alpha_by_year_and_month = excess_rets.groupby(grouper).sum()
        alpha_by_year_and_month.index.names = ["Sector", "Year", "Month"]
        alpha_by_month = alpha_by_year_and_month.groupby(["Sector", "Month"]).mean()
        
    else:
        grouper = [excess_rets.index.year, excess_rets.index.month]
        alpha_by_year_and_month = excess_rets.groupby(grouper).sum()
        alpha_by_year_and_month.index.names = ["Year", "Month"]
        alpha_by_month = alpha_by_year_and_month.groupby(["Month"]).mean()
        
    return alpha_by_month
    
def stats_winrate_by_group(factor_data_ex):
    """
    计算因子的胜率，胜率是组合表现超过基准的月份占比。
    """
    excess_rets = factor_data_ex.groupby(["Date", "Group"])["M1"].sum().unstack()
    
    # 整体表现
    winrate = (excess_rets>0).sum() / excess_rets.shape[0]
    
    # 分年分组表现
    grouper = [excess_rets.index.year]
    winrate_by_year = (excess_rets > 0).groupby(grouper).mean()
    
    return winrate, winrate_by_year

def stats_hitrate_by_group(factor_data_ex):
    """
    计算因子的命中率。命中率是组合平均每个月跑赢基准的行业占比
    """
    hitrate_by_day = factor_data_ex.groupby(["Group", "Date"])["M1"].apply(lambda x: (x > 0).sum() / x.count())
    
    # 整体表现
    hitrate = hitrate_by_day.groupby(["Group"]).mean()
    
    # 分年分组表现
    grouper = [hitrate_by_day.index.get_level_values(1).year]
    hitrate_by_year = hitrate_by_day.groupby(grouper).mean()

    return hitrate, hitrate_by_year

def stats_decay_by_group(factor_data_ex):
    """
    计算因子的衰减率。接下去第一个月、第二个月、第三个月直到第十二个月的超额收益率
    """
    alpha_by_date = factor_data_ex.groupby(["Date", "Group"]).sum().drop(columns=["Factor"]) # 每期每组的未来收益率
    alpha_by_date.replace(0, np.nan, inplace=True) # 将0替换为nan
    alpha = alpha_by_date.groupby(["Group"]).mean() 
    alpha.columns = [f"M{i}" for i in range(1, 13)]
    return alpha
