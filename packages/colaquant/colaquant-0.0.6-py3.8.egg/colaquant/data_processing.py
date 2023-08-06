import numpy as np
import pandas as pd

def check_input_data_format(factor, rets, sector_data=None, asset_type='stock'):
    """检查并规范输入的数据格式"""
    # 1. 检查输入的数据是否为DataFrame格式
    ## 如果 factor 或 rets 是 Series, 转换成 DataFrame
    if isinstance(factor, pd.Series):
        factor = pd.DataFrame(factor)
    if isinstance(rets, pd.Series):
        rets = pd.DataFrame(rets)
        
    # 2. 修改输入的数据的列名和索引名
    ## 修改 factor 和 rets 的列名和索引名
    factor.columns = ["Factor"]
    factor.index.names = ["Date", "Asset"]
    rets.columns = ["Return"]
    rets.index.names = ["Date", "Asset"]
    
    # 3. 对板块数据的检查
    ## 如果是行业轮动，行业和板块的匹配不随时间变化，所以合并时只需要on="Asset"
    ## 如果是选股，股票和板块的匹配随时间变化，所以合并时需要on=["Date", "Asset"]
    if sector_data is not None:
        if asset_type == "industry":
            sector_data.columns = ["Asset", "Sector"]
        elif asset_type == "stock":
            sector_data.columns = ["Date", "Asset", "Sector"]
    
    return factor, rets, sector_data

def get_clean_factor_and_forward_return(factor, rets, sector_data=None, asset_type='stock', if_group=True, group_num=5):
    """清洗因子和收益率数据"""
    
    # 1. 检查并规范输入数据的格式
    factor, rets, sector_data = check_input_data_format(factor, rets, sector_data, asset_type)
    
    # 2. 清洗因子数据: 只取调仓日的数据并滞后一期
    clean_factor = get_clean_factor(factor, if_group=if_group, group_num=group_num)
    
    # 3. 按照因子值分组
    if if_group:
        factor_quantile = get_factor_quantile(clean_factor, group_num=group_num)
    else:
        factor_quantile = None
    
    # 4. 清洗收益率数据: 索引为日期, 列为资产
    clean_rets = get_clean_rets(rets)
    
    # 5. 计算超额收益率
    clean_excess_rets = get_clean_excess_rets(clean_rets)
    
    # 6. 计算未来收益率
    forward_rets = get_forward_rets(clean_rets)
    forward_excess_rets = get_forward_rets(clean_excess_rets)
    
    # 7. 合并数据
    factor_data = merge_factor_data(clean_factor, clean_rets, factor_quantile, forward_rets, sector_data, asset_type, if_excess=False)
    factor_data_ex = merge_factor_data(clean_factor, clean_excess_rets, factor_quantile, forward_excess_rets, sector_data, asset_type, if_excess=True)

    return factor_data, factor_data_ex

def get_clean_factor(factor, if_group=True, group_num=5):
    """清洗因子数据
    clean_factor是清洗过的因子数据, 索引是日期+资产。
    这里进行两个处理, 一是只取调仓日的数据并滞后一期, 二是删除资产个数少于quantile的日期
    """
    # 1. 只取调仓日的数据并滞后一期
    # 每个月月底显示的因子值都是上一个月月底对应的值，因为分组是基于上个月月底的因子来分的
    # 先unstack把索引变成日期，然后只取调仓日的因子数据，接着shift一个月，再stack回去
    refer_data = factor.unstack()["Factor"]
    rebalancing_index = refer_data.groupby(refer_data.index.to_period('M')).apply(lambda x: x.index.max())
    clean_factor = factor.unstack()["Factor"].loc[rebalancing_index].shift().stack()
    
    # 2. 删除资产个数少于quantile的日期，因为这些日期无法分组
    if if_group:
        tmp = clean_factor.groupby("Date").count() # 统计每天的资产个数
        del_idx = tmp[tmp<group_num].index # 取出资产个数少于quantile的日期
        clean_factor = clean_factor[~clean_factor.index.get_level_values(0).isin(del_idx)]
    return clean_factor

def get_factor_quantile(clean_factor, group_num):
    """根据因子得分进行分组"""
    factor_quantile = clean_factor.groupby("Date", group_keys=False).apply(lambda x: pd.qcut(x, group_num, labels=["G"+str(i) for i in range(1, group_num+1)]))
    factor_quantile.name = 'Group'
    return factor_quantile

def get_clean_rets(rets):
    """清洗收益率数据
    clean_rets是清洗过的收益率数据, 索引是日期, 列为资产
    """
    # 计算两个调仓日之间的收益率之和
    refer_data = rets.unstack()["Return"]
    rebalancing_index = refer_data.groupby(refer_data.index.to_period('M')).apply(lambda x: x.index.max())
    clean_rets = refer_data.groupby(refer_data.index.to_period('M')).apply(lambda x: x.sum()).replace(0, np.nan)
    clean_rets.index = rebalancing_index.values
    clean_rets.index.name = "Date"
    return clean_rets

def get_clean_excess_rets(clean_rets):
    """
    clean_excess_rets是超额收益率, 索引为日期, 列为资产。基准为资产等权。
    """
    clean_excess_rets = clean_rets.sub(clean_rets.mean(axis=1), axis=0) # 月度超额收益率
    return clean_excess_rets

def get_forward_rets(clean_rets):
    forward_rets = pd.DataFrame()
    for i in range(2, 13):
        forward_rets[f"M{i}"] = clean_rets.shift(-1*(i-1)).stack()
    return forward_rets

def merge_factor_data(clean_factor, clean_rets, factor_quantile=None, forward_rets=None, sector_data=None, asset_type='stock', if_excess=False):
    """合并因子和收益率数据
    """
    factor_data = pd.DataFrame({"Factor": clean_factor, "M1": clean_rets.stack()})
    
    if forward_rets is not None:
        factor_data = pd.merge(factor_data, forward_rets, left_index=True, right_index=True, how='left')
    
    if factor_quantile is not None:
        factor_data = pd.merge(factor_data, factor_quantile, left_index=True, right_index=True, how='left')

    # 把超额收益率除以该期所在组的资产数量，方便后续计算
    if if_excess:
        num_by_group = factor_data.groupby(["Date", "Group"]).Factor.count() # 每期各组的资产数量
        num_by_group.name = "num" # 重命名series
        tmp = factor_data.join(num_by_group, on=["Date", "Group"], how="left") # 合并原始数据和资产数量
        factor_data = tmp[[f"M{i}" for i in range(1, 13)]+["num"]].apply(lambda s: s/s.num, axis=1) # 将超额收益率除以资产数量
        factor_data = factor_data[[f"M{i}" for i in range(1, 13)]].join(tmp[["Factor", "Group"]], on=['Date', 'Asset'], how='left')

    factor_data = factor_data.dropna(subset=['Factor'])
    factor_data = factor_data.reset_index()

    if sector_data is not None:
        if asset_type == "industry":
            factor_data = factor_data.merge(sector_data, on="Asset", how="left")
        elif asset_type == "stock":
            factor_data = factor_data.merge(sector_data, on=["Date", "Asset"], how="left")
    return factor_data.set_index(['Date', 'Asset'])

