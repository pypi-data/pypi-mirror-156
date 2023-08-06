import numpy as np
import pandas as pd

def factor_information_coefficient(factor_data, by_sector=False):
    """计算因子的Rank IC序列
    
    Parameters
    ==========
    factor_data: pd.DataFrame, 清洗过的因子数据, 包含因子值、收益率、所属板块（可选）等信息
    by_sector: bool, 是否分板块计算IC
    
    Returns
    =======
    ic_all: pd.DataFrame, 因子的Rank IC序列, 通过ic_all, 可以计算累计IC、IC均值、ICIR、IC_t、IC胜率等
    
    Notes
    =====
    ic = ic_all.M1 # IC
    ic_cum = ic.cumsum() # 累计IC
    ic_mean = ic.mean() # IC 均值
    icir = ic.mean() / ic.std() # ICIR
    ic_t = ic.mean() / ic.std() * np.sqrt(ic.shape[0]-1) # IC_t
    ic_winrate = (ic>0).sum() / ic.shape[0] # IC 序列的胜率, IC 向上的占比
    ic_decay = ic_all.mean() # IC衰减
    """
    grouper = ["Date"]
    if by_sector: # 如果分板块计算IC，则需要添加板块信息
        grouper.append("Sector")
        
    ic_all = factor_data.groupby(grouper).apply(lambda x: x.corr(method="spearman")["Factor"]).drop(columns=["Factor"])
    return ic_all

def factor_IC_stats(factor_data, by_sector=False):
    """
    计算IC的统计量
    
    IC的绝对值大于0.03时，因子的择股(行业)能力较强, IR大于0.5时因子稳定获取超额收益能力较强
    """
    # 先计算全样本的IC
    ic_all = factor_information_coefficient(factor_data, by_sector=False)
    ic = ic_all.M1 # IC 序列
    ic_mean = ic.mean() # IC 均值
    icir = ic.mean() / ic.std() # ICIR
    ic_t = ic.mean() / ic.std() * np.sqrt(ic.shape[0]-1) # IC_t：用于检查 IC 值序列均值是否显著不为 0
    ic_winrate = (ic>0).sum() / ic.shape[0] # IC 序列的胜率：IC 向上的占比
    
    result = pd.Series({'IC 均值': ic_mean, "IC IR": icir, 'IC T值': ic_t, 'IC 胜率': ic_winrate}, name="全样本")
    
    if by_sector: # 分板块计算IC
        ic_all = factor_information_coefficient(factor_data, by_sector=by_sector)
        ic = ic_all.M1 # IC序列
        ic_mean = ic.groupby("Sector").mean() # 各板块的IC均值
        icir = ic.groupby("Sector").mean() / ic.groupby("Sector").std() # ICIR
        ic_t = icir * ic.groupby("Sector").apply(lambda x: np.sqrt(x.shape[0]-1)) # IC_t
        ic_winrate = ic.groupby("Sector").apply(lambda x: (x>0).sum() / x.shape[0]) # IC序列的胜率

        results = pd.DataFrame({'IC 均值': ic_mean, "IC IR": icir, 'IC T值': ic_t, 'IC 胜率': ic_winrate}).T
        results["全样本"] = result
    else: # 不分板块的话，就直接返回全样本的结果
        results = result
        
    return results

def factor_IC_cum(factor_data, by_sector=False):
    """
    计算累计IC
    """
    if by_sector:
        # 各板块的累计IC
        ic_all = factor_information_coefficient(factor_data, by_sector)
        ic = ic_all.M1 # IC序列
        ic_cum = ic.groupby("Sector").cumsum().unstack() # 各板块的累计IC
        
        # 全样本的累计IC
        ic_all = factor_information_coefficient(factor_data, by_sector=False)
        ic = ic_all.M1 # IC序列
        ic_cum["全样本"] = ic.cumsum() # 全样本的累计IC
    else:
        # 全样本的累计IC
        ic_all = factor_information_coefficient(factor_data, by_sector)
        ic = ic_all.M1 # IC
        ic_cum = ic.cumsum() # 累计IC
        ic_cum.name = "全样本"
    return ic_cum

def factor_IC_decay(factor_data, by_sector=False):
    """
    计算因子IC的衰减
    """
    ic_all = factor_information_coefficient(factor_data, by_sector)
    if by_sector:
        ic_decay = ic_all.groupby('Sector').mean()
        ic_decay_all = ic_all.mean()
        ic_decay_all = ic_decay_all.to_frame().rename(columns={0: "IC 衰减"}).T
        ic_decay = ic_decay.append(ic_decay_all)
    else:
        ic_decay = ic_all.mean() # IC衰减
        ic_decay = ic_decay.to_frame().rename(columns={0: "IC 衰减"}).T
    return ic_decay
