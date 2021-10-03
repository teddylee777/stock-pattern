import FinanceDataReader as fdr
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from matplotlib.figure import Figure


class PatternFinder():
    def __init__(self, period=5):
        self.period = period
    
    def set_stock(self, code: str):
        self.code = code
        self.data = fdr.DataReader(code)
        self.close = self.data['Close']
        self.change = self.data['Change']
        return self.data
        
    def search(self, start_date, end_date, threshold=0.98):
        base = self.close[start_date:end_date]
        self.base_norm = (base - base.min()) / (base.max() - base.min())
        self.base = base

        window_size = len(base)
        moving_cnt = len(self.data) - window_size - self.period - 1
        cos_sims = self.__cosine_sims(moving_cnt, window_size)
        
        self.window_size = window_size
        cos_sims = cos_sims[cos_sims > threshold]
        return cos_sims
    
    
    def __cosine_sims(self, moving_cnt, window_size):
        def cosine_similarity(x, y):
            return np.dot(x, y) / (np.sqrt(np.dot(x, x)) * np.sqrt(np.dot(y, y)))
        
        # 유사도 저장 딕셔너리
        sim_list = []

        for i in range(moving_cnt):
            target = self.close[i:i+window_size]

            # Normalize
            target_norm = (target - target.min()) / (target.max() - target.min())

            # 코사인 유사도 저장
            cos_similarity = cosine_similarity(self.base_norm, target_norm)

            # 코사인 유사도 <- i(인덱스), 시계열데이터 함께 저장
            sim_list.append(cos_similarity)
        return pd.Series(sim_list).sort_values(ascending=False)

    
    def plot_pattern(self, idx, period=5):
        if period != self.period:
            self.period = period
            
        top = self.close[idx:idx+self.window_size+period]
        top_norm = (top - top.min()) / (top.max() - top.min())
        fig = Figure()
        axis = fig.add_subplot(1, 1, 1)
        axis.plot(self.base_norm.values, label='base', color='black',  alpha=0.7)
        axis.plot(top_norm.values, label='prediction', color='red', linestyle='dashed')
        axis.plot(top_norm.values[:len(self.base_norm.values)], label='pattern', color='red', linestyle='solid')
        axis.axvline(x=len(self.base_norm)-1, c='tomato', linestyle='dotted')
        axis.axvspan(len(self.base_norm.values)-1, len(top_norm.values)-1, facecolor='yellow', alpha=0.3)
        axis.legend()
        axis.get_yaxis().set_visible(False)
        axis.get_xaxis().set_visible(False)
        
        preds = self.change[idx+self.window_size: idx+self.window_size+period]
        print(f'pred: {preds.mean()*100} % ')
        return fig

    def stat_prediction(self, results, period=5):
        idx_list = list(results.keys())
        mean_list = []
        for idx in idx_list:
            pred = self.change[idx+self.window_size: idx+self.window_size+period]
            mean_list.append(pred.mean())
        return np.array(mean_list)