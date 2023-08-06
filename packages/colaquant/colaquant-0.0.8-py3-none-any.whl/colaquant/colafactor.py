import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import os

plt.style.use('seaborn')
plt.rcParams["font.sans-serif"] = ["SimHei"] # 中文字体显示
plt.rcParams["axes.unicode_minus"] = False # 负号正常显示
mpl.rcParams["figure.autolayout"] = True # 自动排版

import warnings
warnings.filterwarnings('ignore')

# 测试的时候用这几行
# import sys 
# sys.path.append("..") 
# import data_processing as dp
# import information_analysis as ia
# import returns_analysis as ra
# import position_analysis as pa
# import asset_analysis as aa
# from utils import *

# 发布的时候用这几行
from . import data_processing as dp
from . import information_analysis as ia
from . import returns_analysis as ra
from . import position_analysis as pa
from . import asset_analysis as aa
from . utils import *

# ----------------------------------------

class colafactor:
    
    def __init__(self, factor, rets, sector_data=None, asset_type='stock', if_group=True, group_num=5):
        """
        :param factor: 资产的因子数据，索引为日期和资产，日期统一为"%Y-%m-%d"形式
        :param rets: 资产的收益率数据，索引为日期和资产
        :param sector_data: 资产所属板块，无索引，列为日期、资产和板块（股票）或资产和板块（行业）；如果是None，则不考虑板块内轮动
        :param asset_type: 资产类型，"industry"或"stock"，分别代表行业轮动和选股策略
        :param if_group: 是否进行分组，默认为True
        :param group_num: 分组数，默认为5
        """
        
        self.factor = factor # 因子
        self.rets = rets # 收益率
        self.sector_data = sector_data # 所属板块
        self.asset_type = asset_type # 资产类型
        self.if_group = if_group # 是否进行分组
        self.group_num = group_num
        
        # 清洗后的因子数据，之后的计算都是基于factor_data或factor_data_ex
        self.factor_data, self.factor_data_ex = dp.get_clean_factor_and_forward_return(factor, rets, sector_data, asset_type, if_group, group_num)
        
    def information_analysis(self, by_sector=None):
        
        if by_sector is None:
            if self.sector_data is not None:
                by_sector = True
            else:
                by_sector = False
        else:
            by_sector = by_sector
        
        ic_stats = ia.factor_IC_stats(self.factor_data, by_sector=by_sector)
        ic_cum = ia.factor_IC_cum(self.factor_data, by_sector=by_sector)

        return ic_stats, ic_cum
    
    def returns_analysis(self, by_sector=None):
        
        if by_sector is None:
            if self.sector_data is not None:
                by_sector = True
            else:
                by_sector = False
        else:
            by_sector = by_sector
            
        alpha, alpha_by_year = ra.stats_alpha_by_group(self.factor_data_ex, by_sector=by_sector)
        alpha_by_month = ra.stats_alpha_by_group_and_month(self.factor_data_ex, by_sector=by_sector)
        
        winrate, winrate_by_year = ra.stats_winrate_by_group(self.factor_data_ex)
        hitrate, hitrate_by_year = ra.stats_hitrate_by_group(self.factor_data_ex)

        return alpha, alpha_by_year, alpha_by_month, winrate, hitrate

    def decay_analysis(self, by_sector=None):
        
        if by_sector is None:
            if self.sector_data is not None:
                by_sector = True
            else:
                by_sector = False
        else:
            by_sector = by_sector
        
        ic_decay = ia.factor_IC_decay(self.factor_data, by_sector=by_sector)
        returns_decay = ra.stats_decay_by_group(self.factor_data_ex)

        return ic_decay, returns_decay

    def position_analysis(self, num=None):
        
        asset_ex_by_year = pa.stats_asset_in_detail_by_year(self.factor_data_ex, num=num)
        asset_group_score = pa.stats_asset_group_score(self.factor_data, num=num)
        
        return asset_ex_by_year, asset_group_score
    
    def show_simple_results(self):
        if self.sector_data is not None:
            by_sector = True
        else:
            by_sector = False
            
        ic_stats, ic_cum = self.information_analysis(by_sector=by_sector)
        excess_nav = ra.excess_nav_by_group(self.factor_data_ex, by_sector=False).dropna()
        
        fig, axes = plt.subplots(2, 1, figsize=(10, 8), dpi=150)
        ic_cum.plot(ax=axes[0], title='累计IC', cmap=plt.cm.tab20)
        excess_nav.plot(ax=axes[1], title='分组超额净值', cmap=plt.cm.tab20)
    
    def save_detailed_results(self, num=None, save_path=None):
        if save_path is None:
            save_path = "详细结果.xlsx"
            
        with pd.ExcelWriter(
            save_path,
            datetime_format='YYYY-MM-DD'  # 只显示年月日, 不显示时分秒
        ) as writer:
            
            if self.sector_data is not None:

                ic_stats, ic_cum = self.information_analysis(by_sector=True)
                alpha, alpha_by_year, alpha_by_month, winrate, hitrate = self.returns_analysis(by_sector=False)
                result = pd.concat([alpha, winrate, hitrate], axis=1)
                result.columns = ["超额收益率", "胜率", "命中率"]
                
                excess_nav = ra.excess_nav_by_group(self.factor_data_ex, by_sector=False).dropna()
                excess_nav_by_sector = ra.excess_nav_by_group(self.factor_data_ex, by_sector=True).dropna()
                
                ic_stats.to_excel(writer, sheet_name="IC统计量")
                ic_cum.to_excel(writer, sheet_name="累计IC")
                excess_nav.to_excel(writer, sheet_name="分组超额净值")
                excess_nav_by_sector.to_excel(writer, sheet_name="分板块-分组超额净值")
                
                result.to_excel(writer, sheet_name="分年分组汇总")
                alpha_by_year.to_excel(writer, sheet_name="分年分组超额")
                alpha_by_month.to_excel(writer, sheet_name="分月分组超额")
                
                alpha, alpha_by_year, alpha_by_month, winrate, hitrate = self.returns_analysis(by_sector=True)
                ic_decay, returns_decay = self.decay_analysis(by_sector=True)
                asset_ex_by_year, asset_group_score = self.position_analysis(num=num)
                alpha_by_year = alpha_by_year.replace(0, np.nan).dropna()
                alpha_by_year.to_excel(writer, sheet_name="分板块-分年分组超额")
                
                pd.concat([ic_decay, returns_decay]).to_excel(writer, sheet_name="衰减")
                
                asset_group_score.to_excel(writer, sheet_name="资产组别得分", index=False)
                asset_ex_by_year.to_excel(writer, sheet_name="资产情况明细-分年", index=False)
                pa.stats_sector_in_detail_by_year(self.factor_data_ex).to_excel(writer, sheet_name="板块情况明细-分年", index=False)
                
                
            else:
                ic_stats, ic_cum = self.information_analysis(by_sector=False)
                alpha, alpha_by_year, alpha_by_month, winrate, hitrate = self.returns_analysis(by_sector=False)
                result = pd.concat([alpha, winrate, hitrate], axis=1)
                result.columns = ["超额收益率", "胜率", "命中率"]

                excess_nav = ra.excess_nav_by_group(self.factor_data_ex, by_sector=False).dropna()
                
                ic_stats.to_excel(writer, sheet_name="IC统计量")
                ic_cum.to_excel(writer, sheet_name="累计IC")
                excess_nav.to_excel(writer, sheet_name="分组超额净值")
                
                result.to_excel(writer, sheet_name="分年分组汇总")
                alpha_by_year = alpha_by_year.replace(0, np.nan).dropna()
                alpha_by_year.to_excel(writer, sheet_name="分年分组超额")
                alpha_by_month.to_excel(writer, sheet_name="分月分组超额")
                
                ic_decay, returns_decay = self.decay_analysis(by_sector=False)
                asset_ex_by_year, asset_group_score = self.position_analysis(num=num)
                
                pd.concat([ic_decay, returns_decay]).to_excel(writer, sheet_name="衰减")
                
                asset_group_score.to_excel(writer, sheet_name="资产组别得分", index=False)
                asset_ex_by_year.to_excel(writer, sheet_name="资产情况明细-分年", index=False)
                
            print(f"因子测试的详细结果已保存到 {save_path}")
