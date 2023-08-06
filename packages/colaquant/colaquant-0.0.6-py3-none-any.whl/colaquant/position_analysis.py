import numpy as np
import pandas as pd

def stats_asset_in_detail_by_year(factor_data_ex, num=None):
    """每个组每年选中的资产及其命中率, num表示每组收益最高和最低的前num个资产"""
    grouper = ["Group", factor_data_ex.index.get_level_values(0).year, "Asset"] # 按照组别、年份、资产分组
    
    # 累计超额、选中次数、命中次数、命中率
    asset_ex_by_year = factor_data_ex.groupby(grouper).M1.agg(["sum", "count", lambda x: (x>0).sum(), lambda x: (x>0).sum()/x.count()]).dropna()
    
    # 因子均值
    asset_factor_by_year = factor_data_ex.groupby(grouper).Factor.mean()
    
    # 合并
    asset_ex_by_year = asset_ex_by_year.join(asset_factor_by_year)
    asset_ex_by_year.columns = ["累计超额", "选中次数", "命中次数", "命中率", "因子均值"]
    asset_ex_by_year = asset_ex_by_year[["因子均值", "累计超额", "选中次数", "命中次数", "命中率"]]
    
    # 所属板块
    if 'Sector' in factor_data_ex.columns:
        asset_sector = factor_data_ex.groupby(grouper).apply(lambda x: x.Sector.value_counts().idxmax())
        asset_sector.name = 'Sector'
        asset_ex_by_year = asset_ex_by_year.join(asset_sector)
    
    if num is not None:
        asset_ex_by_year = asset_ex_by_year.groupby(['Group', 'Date'], group_keys=False).apply(lambda x: x.sort_values('累计超额').iloc[np.r_[0:num, -num:0]])
    asset_ex_by_year = asset_ex_by_year.reset_index()

    return asset_ex_by_year

def stats_sector_in_detail_by_year(factor_data_ex):
    """每组每年选中的板块及其命中率, 板块收益率是板块内行业收益率的平均, 相当于等权配置"""
    asset_ex_by_year = stats_asset_in_detail_by_year(factor_data_ex)
    sector_ex_by_year = asset_ex_by_year.groupby(["Group", "Date", "Sector"]).agg({"因子均值": "mean", "累计超额": "sum", "选中次数": "sum", "命中次数": "sum", "命中率": "mean"}).dropna()
    return sector_ex_by_year.reset_index()

def stats_asset_group_score(factor_data, num=None):
    """资产组合平均得分, 被分到G1得1分, 分到G5得5分, 分到G10得10分"""
    asset_group_score = factor_data.Group.apply(lambda x: x[1:]).dropna().astype(np.int).groupby(["Asset"]).mean().sort_values(ascending=False)
    asset_group_score = asset_group_score.reset_index()
    asset_group_score.columns = ["Asset", "Score"]
    
    if num is not None:
        asset_group_score = asset_group_score.iloc[np.r_[0:num, -num:0]]
    return asset_group_score