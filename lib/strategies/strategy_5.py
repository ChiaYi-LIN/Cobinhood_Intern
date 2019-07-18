# SAR 乖離觸發交易訊號
# -> 交易訊號出現後第 7 根 long 進場

# 進場後
# -> 若 close >= 交易訊號時的 close 則開始50%移動停利
# -> 若虧損超過5%即停損
#%%
from .process.trade_process import trade_process
class trade_strategy_5(trade_process):
    def apply_trading_strategy(self, sar_diff, lower_shadow, upper_shadow):
        self.long_signal = False
        self.short_signal = False
        self.buy_signal = False
        self.sell_signal = False
        self.keep_signal = 0
        self.set_delay = 6
        self.delay = 0
        self.start_ma_stop_gain_3 = False
        self.start_ma_stop_gain_6 = False

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
                    '''
                    if self.long_signal:
                        self.trade_long(i, self.long_quantity(i))
                        self.long_signal = False
                    else:
                        self.should_long(i)
                    '''
                    if self.current_situation > 0:
                        if self.sell_signal:
                            self.trade_sell(i, self.sell_quantity(i))
                            self.sell_signal = False
                        else:
                            self.should_sell(i, sar_diff, upper_shadow)
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

    def do_next_trade(self, i, period):
        if i >= self.previous_action + period:
            return True
        else:
            return False 
    
    def should_long(self, i, sar_diff, lower_shadow):
        if self.data["Parabolic SAR"].iloc[i] > self.data["High"].iloc[i]:
            if (self.data["Parabolic SAR"].iloc[i] - self.data["Low"].iloc[i])/self.data["Low"].iloc[i] > sar_diff:
                if self.data["Volume"].iloc[i] == self.data["Volume"].iloc[i-14:i+1].max():
                    if self.data["Open"].iloc[i] - self.data["Low"].iloc[i] <= self.data["Close"].iloc[i] - self.data["Low"].iloc[i]:
                        if (self.data["Open"].iloc[i] - self.data["Low"].iloc[i])/(self.data["High"].iloc[i] - self.data["Low"].iloc[i]) >= lower_shadow:
                            self.long_signal = True
                            self.delay = self.set_delay
                            self.keep_signal = self.data["Close"].iloc[i]
                    else:
                        if (self.data["Close"].iloc[i] - self.data["Low"].iloc[i])/(self.data["High"].iloc[i] - self.data["Low"].iloc[i]) >= lower_shadow:
                            self.long_signal = True
                            self.delay = self.set_delay
                            self.keep_signal = self.data["Close"].iloc[i]
        

    def should_sell(self, i, sar_diff, upper_shadow):
        if (self.data["Close"].iloc[i] >= self.keep_signal and self.data["Close"].iloc[i] >= self.exist_long[0][4]) or self.start_ma_stop_gain_3 == True:
            # 移動停利
            if self.start_ma_stop_gain_3 != True:
                self.start_ma_stop_gain_3 = True
            if self.ma_stop_gain == 0:
                self.ma_stop_gain = (self.data["Close"].iloc[i] - self.exist_long[0][4])/self.exist_long[0][4] 
            else:
                if ((self.data["Close"].iloc[i] - self.exist_long[0][4])/self.exist_long[0][4]) <= self.ma_stop_gain*1/2:
                    self.sell_signal = True
                    self.keep_signal = 0
                    self.ma_stop_gain = 0
                    self.start_ma_stop_gain_3 = False
                    self.start_ma_stop_gain_6 = False
                elif ((self.data["Close"].iloc[i] - self.exist_long[0][4])/self.exist_long[0][4]) > self.ma_stop_gain:
                    self.ma_stop_gain = (self.data["Close"].iloc[i] - self.exist_long[0][4])/self.exist_long[0][4] 
        elif (self.data["Close"].iloc[i] - self.exist_long[0][4])/self.exist_long[0][4] <= -0.05:
            self.sell_signal = True
            self.keep_signal = 0
            self.ma_stop_gain = 0
            self.start_ma_stop_gain_3 = False
            self.start_ma_stop_gain_6 = False

        """
        elif (self.data["Close"].iloc[i] - self.exist_long[0][1])/self.data["Close"].iloc[i] >= (0.0065 + self.fees):
            self.sell_signal = True
            self.delay = self.set_delay
            self.keep_signal = 0
        """
        

        """
        if self.data["Parabolic SAR"].iloc[i] < self.data["Close"].iloc[i]: 
            self.sell_signal = True
        

        long_data = self.exist_long
        long_position = self.current_situation
        
        if (long_data != []) and (long_position > 0):
            if (self.data["Close"].iloc[i] - long_data[0][1])/long_data[0][1] < -0.03: 
                self.sell_signal = True
        
        if self.data["Low"].iloc[i] < self.keep_signal:
            self.sell_signal = True
            self.delay = self.set_delay
            self.keep_signal = 0
        """
    
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
        expect_quantity = 1
        if self.current_situation <= expect_quantity:
            return abs(self.current_situation)
        else:
            return expect_quantity