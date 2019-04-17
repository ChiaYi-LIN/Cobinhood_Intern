# 移除下影線條件
# long 1 > long 2 > sell all
# 訊號後第三根交易
# target price = max(long 1 close, long 2 close)
# long 1 用全部資金20%
# long 2 用剩下資金40%
#%%
from .process.trade_process import trade_process
class trade_strategy_6(trade_process):
    def apply_trading_strategy(self, sar_diff, lower_shadow, upper_shadow, stop_loss):
        self.long_signal = False
        self.short_signal = False
        self.buy_signal = False
        self.sell_signal = False
        self.keep_signal = 0
        self.set_delay = 2
        self.delay = 0
        self.start_ma_stop_gain = False

        first_action = True
        for i in range(len(self.data)):
            if self.delay == 0:
                if first_action:
                    if self.long_signal:
                        self.trade_long(i, self.long_quantity(i))
                        self.long_signal = False
                        first_action = False
                    else:
                        self.should_long(i, sar_diff, lower_shadow)
                elif self.do_next_trade(i,3):
                    if self.current_situation >= 1 and self.current_situation < 2:
                        if self.long_signal:
                            self.trade_long(i, self.long_quantity(i))
                            self.long_signal = False
                        else:
                            self.should_long(i, sar_diff, lower_shadow)
                    elif self.current_situation ==  2:
                        if self.sell_signal:
                            self.trade_sell(i, self.sell_quantity(i))
                            self.sell_signal = False
                        else:
                            self.should_sell(i, sar_diff, upper_shadow, stop_loss)
                    else:
                        if self.long_signal:
                            self.trade_long(i, self.long_quantity(i))
                            self.long_signal = False
                        else:
                            self.should_long(i, sar_diff, lower_shadow)
            else:
                self.delay = self.delay - 1   

        total_trade = len(self.data.loc[(self.data["Action"] == "Buy") | (self.data["Action"] == "Sell")])
        total_win = len(self.data.loc[self.data["Win/Lose"] == "Win"])
        self.win_rate = (total_win/total_trade)*100
        total_gain  = sum(self.data["Gain/Loss"].loc[self.data["Gain/Loss"] > 0 ])
        total_loss = sum(self.data["Gain/Loss"].loc[self.data["Gain/Loss"] < 0 ])
        self.profit = total_gain + total_loss
        print("Start BTC: {}, Start USD: {}" .format(self.data["BTC account"].iloc[0], self.data["USD account"].iloc[0]))
        print("Stop-Loss Rate: {}" .format(stop_loss))
        print("Win rate: {}" .format(self.win_rate))
        print("Profit: {}" .format(self.profit))
        print("____________________________")

    def do_next_trade(self, i, period):
        if i >= self.previous_action + period:
            return True
        else:
            return False 
    
    def should_long(self, i, sar_diff, lower_shadow):
        if self.data["Parabolic SAR"].iloc[i] > self.data["High"].iloc[i]:
            if (self.data["Parabolic SAR"].iloc[i] - self.data["Low"].iloc[i])/self.data["Low"].iloc[i] > sar_diff:
                if self.data["Volume"].iloc[i] == self.data["Volume"].iloc[i-14:i+1].max():
                    self.long_signal = True
                    self.delay = self.set_delay
                    # self.keep_signal = self.data["Close"].iloc[i]
                    
    def should_sell(self, i, sar_diff, upper_shadow, stop_loss):
        if self.data["Close"].iloc[i] >= self.exist_long[0][4] or self.start_ma_stop_gain == True:
            # 移動停利
            if self.start_ma_stop_gain != True:
                self.start_ma_stop_gain = True
            if self.ma_stop_gain == 0:
                self.ma_stop_gain = (self.data["Close"].iloc[i] - self.exist_long[0][4])/self.exist_long[0][4] 
            else:
                if ((self.data["Close"].iloc[i] - self.exist_long[0][4])/self.exist_long[0][4]) <= self.ma_stop_gain*1/2:
                    self.sell_signal = True
                    # self.keep_signal = 0
                    self.ma_stop_gain = 0
                    self.start_ma_stop_gain = False
                elif ((self.data["Close"].iloc[i] - self.exist_long[0][4])/self.exist_long[0][4]) > self.ma_stop_gain:
                    self.ma_stop_gain = (self.data["Close"].iloc[i] - self.exist_long[0][4])/self.exist_long[0][4] 
        elif (self.data["Close"].iloc[i] - self.exist_long[1][4])/self.exist_long[1][4] <= stop_loss:
            self.sell_signal = True
            # self.keep_signal = 0
            self.ma_stop_gain = 0
            self.start_ma_stop_gain = False
    
    def long_quantity(self, i):
        return 1
    
    def short_quantity(self, i):
        return 1
    
    def buy_quantity(self, i):
        expect_quantity = 1
        if self.current_situation >= -1*expect_quantity:
            return abs(self.current_situation)
        else:
            return expect_quantity
    
    def sell_quantity(self, i):
        return abs(self.current_situation)

        
        # expect_quantity = 1
        # if self.current_situation <= expect_quantity:
        #     return abs(self.current_situation)
        # else:
        #     return expect_quantity
        

    def trade_long(self, i, n):
        btc_change = 0
        self.current_situation += n
        self.data["Situation"].iloc[i] = self.current_situation
        self.data["Action"].iloc[i] = "Long"
        self.data["Long"].iloc[i] = n
        self.data["Price"].iloc[i] = self.data["Close"].iloc[i]*(1 + self.fees)
        if self.current_situation == 1:
            self.start_period_usd = self.usd
            btc_change = self.usd*0.2/self.data["Price"].loc[i]
            self.btc += btc_change
            self.usd = self.usd*0.8
        elif self.current_situation == 2:  
            btc_change = self.usd*0.4/self.data["Price"].loc[i]
            self.btc += btc_change
            self.usd = self.usd*0.6
        # self.usd -= self.data["Price"].iloc[i]*n
        self.data["BTC account"].iloc[i] = self.btc
        self.data["USD account"].iloc[i] = self.usd
        self.previous_action = i
        self.exist_long.append([btc_change, self.data["Price"].iloc[i], self.data["High"].iloc[i], self.data["Low"].iloc[i], self.data["Close"].iloc[i]])
        if len(self.exist_long) > 2:
            print(self.exist_long)