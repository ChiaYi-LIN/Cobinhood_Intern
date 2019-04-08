#%%
from lib.strategies.process.trade_process import trade_process
from lib.strategies.process.trade_process import plot_data
from lib.strategies.process.trade_process import technical_analysis
from lib.strategies.strategy_1 import trade_strategy_1
import pandas as pd
import numpy as np

#%%
if __name__ == '__main__':
    data = 0
    data_timestamp = "Timestamp"
    data_open = "Open"
    data_high = "High"
    data_low = "Low"
    data_close = "Close"
    data_volume = "Volume"
    ta_test = 0
    plot = 0
    ts_test = 0

    # Import data
    test_data = pd.read_csv("./data/BTC_USD_2018.csv", header = None, names = [data_timestamp, data_open, data_close, data_high, data_low, data_volume])

    # Import data
    data = pd.read_csv("./data/binance_candles_btcusdt_190331.csv")
    data.columns = [data_timestamp, data_open, data_high, data_low, data_close, data_volume]
    data = data.sort_values(data_timestamp)
    data = data.reset_index(drop=True)
    
    # Technical analysis
    ta_test = technical_analysis(data)
    # ta_test = technical_analysis(data.iloc[0:50000,])
    
    ta_test.add_real_datetime()
    ta_test.to_5min()
    
    
    # Add curves
    ta_test.add_parabolic_sar()
    ta_test.add_average_true_range(14)
    ta_test.add_sma(20)
    ta_test.add_sma(60)
    ta_test.add_bbands()
    ta_test.add_stochastic_oscillator()
    ta_test.add_keltner_channels()
    # ta_test.print_data(0,10)

    # Trading strategy
    ts_test = trade_strategy_1(ta_test.data)  
    """
    max = -5000
    op_i = 0
    op_j = 0
    for i in np.arange(0.005, 0.01, 0.0005):
        for j in np.arange(0.0005, 0.001, 0.0001):
            ts_test.trade_sheet()  
            ts_test.apply_trading_strategy(i, j)
            if ts_test.profit > max:
                max = ts_test.profit
                op_i = i
                op_j = j
                print(str(op_i))
                print(str(op_j))
                print(str(max))
    print("Final result")
    print(str(op_i))
    print(str(op_j))
    print(str(max))
    
    """
    # ts_test.print_data(0,100)
    ts_test.trade_sheet()
    ts_test.apply_trading_strategy(0.0095, 0.0008)
    ts_test.output_result()
    ts_test.output_overview()
    
    # Plot results
    plot = plot_data(ta_test.data)
    # plot.print_data(0,10)
    plot.plot_all()
    
    
    
    
