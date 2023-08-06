import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib as mpl
import seaborn as sns
import os

def get_factortrend_of_asset(factor_data, year=2020, asset="IT服务"):
    
    # 净值
    nav = factor_data.query(f"Asset=='{asset}'")["M1"].droplevel(1).cumsum()
    # 因子
    factor = factor_data.query(f"Asset=='{asset}'")["Factor"].droplevel(1)
    # 分组
    group = factor_data.query(f"Asset=='{asset}'")["Group"].droplevel(1)
    
    rets = nav.diff()
    tmp = pd.concat([rets, factor, group], axis=1).query(f"Date>{year-2} & Date<={year+2}")
    tmp.columns = ["收益率", "因子值", "组别"]
    
    return tmp

def plot_factortrend_of_asset(factor_data, asset="IT服务", group_num=5):
    # 净值
    nav = factor_data.query(f"Asset=='{asset}'")["M1"].droplevel(1).cumsum()
    # 因子
    factor = factor_data.query(f"Asset=='{asset}'")["Factor"].droplevel(1)
    # 分组
    group = factor_data.query(f"Asset=='{asset}'")["Group"].droplevel(1)
    
    fig, ax = plt.subplots(figsize=(10, 5), dpi=150)
    ax2 = ax.twinx()
    nav.plot(ax=ax, label="NAV") # 净值走势
    factor.plot(ax=ax2, color="#fdae61", alpha=0.5, label="factor") # 因子走势

    for date in group[group=='G1'].index:
        xmin = date
        xmax = group.loc[date:].iloc[:2].index[-1]
        ax.axvspan(xmin=xmin, xmax=xmax, facecolor="#abdda4", alpha=0.3)

    for date in group[group=='G'+str(group_num)].index:
        xmin = date
        xmax = group.loc[date:].iloc[:2].index[-1]
        ax.axvspan(xmin=xmin, xmax=xmax, facecolor="#d7191c", alpha=0.1)

    ax.set_title(f"{asset}-因子和净值趋势")

    fig.legend()
    