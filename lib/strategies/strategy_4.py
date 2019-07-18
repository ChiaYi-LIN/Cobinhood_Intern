#原本long的相同條件做short
#原本sell的相同條件做buy

#%%
from .process.trade_process import trade_process
class trade_strategy_4(trade_process):
    def apply_trading_strategy(self, sar_diff, lower_shadow, upper_shadow):
        self.short_signal = False
        self.short_signal = False
        self.buy_signal = False
        self.buy_signal = False
        self.keep_signal = 0
        self.set_delay = 1
        self.delay = 0
        self.start_ma_stop_gain_3 = False
        self.start_ma_stop_gain_6 = False

        first_action = True
        for i in range(len(self.data)):
            if self.delay == 0:
                if first_action:
                    if self.short_signal:
                        self.trade_short(i, self.short_quantity(i))
                        self.short_signal = False
                        first_action = False
                    else:
                        self.should_short(i, sar_diff, lower_shadow)
                elif self.do_next_trade(i,3):
                    if self.current_situation < 0:
                        if self.buy_signal:
                            self.trade_buy(i, self.buy_quantity(i))
                            self.buy_signal = False
                        else:
                            self.should_buy(i, sar_diff, upper_shadow)
                    else:
                        if self.short_signal:
                            self.trade_short(i, self.short_quantity(i))
                            self.short_signal = False
                        else:
                            self.should_short(i, sar_diff, lower_shadow)
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
    
    def should_short(self, i, sar_diff, lower_shadow):
        if self.data["Parabolic SAR"].iloc[i] > self.data["High"].iloc[i]:
            if (self.data["Parabolic SAR"].iloc[i] - self.data["Low"].iloc[i])/self.data["Low"].iloc[i] > sar_diff:
                if self.data["Volume"].iloc[i] == self.data["Volume"].iloc[i-14:i+1].max():
                    if self.data["Open"].iloc[i] - self.data["Low"].iloc[i] <= self.data["Close"].iloc[i] - self.data["Low"].iloc[i]:
                        if (self.data["Open"].iloc[i] - self.data["Low"].iloc[i])/(self.data["High"].iloc[i] - self.data["Low"].iloc[i]) >= lower_shadow:
                            self.short_signal = True
                            self.delay = self.set_delay
                            self.keep_signal = self.data["Close"].iloc[i]
                    else:
                        if (self.data["Close"].iloc[i] - self.data["Low"].iloc[i])/(self.data["High"].iloc[i] - self.data["Low"].iloc[i]) >= lower_shadow:
                            self.short_signal = True
                            self.delay = self.set_delay
                            self.keep_signal = self.data["Close"].iloc[i]
        

    def should_buy(self, i, sar_diff, upper_shadow):
        if (self.data["Close"].iloc[i] - self.exist_short[0][4])/self.exist_short[0][4] >= 0.06 or self.start_ma_stop_gain_6 == True:
            
            # 直接出場
            self.buy_signal = True
            self.keep_signal = 0
            self.ma_stop_gain = 0
            self.start_ma_stop_gain_3 = False
            self.start_ma_stop_gain_6 = False

            """
            # 進階移動停利
            if self.start_ma_stop_gain_6 != True:
                self.start_ma_stop_gain_6 = True
            if self.ma_stop_gain == 0:
                self.ma_stop_gain = (self.data["Close"].iloc[i] - self.exist_short[0][4])/self.exist_short[0][4]   
            else:
                if ((self.data["Close"].iloc[i] - self.exist_short[0][4])/self.exist_short[0][4]) <= self.ma_stop_gain*2/3:
                    self.buy_signal = True
                    self.keep_signal = 0
                    self.ma_stop_gain = 0
                    self.start_ma_stop_gain_3 = False
                    self.start_ma_stop_gain_6 = False
                elif ((self.data["Close"].iloc[i] - self.exist_short[0][4])/self.exist_short[0][4]) > self.ma_stop_gain:
                    self.ma_stop_gain = (self.data["Close"].iloc[i] - self.exist_short[0][4])/self.exist_short[0][4] 
            """
        elif (self.data["Close"].iloc[i] - self.exist_short[0][4])/self.exist_short[0][4] >= 0.03 or self.start_ma_stop_gain_3 == True:
            # 移動停利
            if self.start_ma_stop_gain_3 != True:
                self.start_ma_stop_gain_3 = True
            if self.ma_stop_gain == 0:
                self.ma_stop_gain = (self.data["Close"].iloc[i] - self.exist_short[0][4])/self.exist_short[0][4] 
            else:
                if ((self.data["Close"].iloc[i] - self.exist_short[0][4])/self.exist_short[0][4]) <= self.ma_stop_gain*1/2:
                    self.buy_signal = True
                    self.keep_signal = 0
                    self.ma_stop_gain = 0
                    self.start_ma_stop_gain_3 = False
                    self.start_ma_stop_gain_6 = False
                elif ((self.data["Close"].iloc[i] - self.exist_short[0][4])/self.exist_short[0][4]) > self.ma_stop_gain:
                    self.ma_stop_gain = (self.data["Close"].iloc[i] - self.exist_short[0][4])/self.exist_short[0][4] 
        elif (self.data["Close"].iloc[i] - self.exist_short[0][4])/self.exist_short[0][4] <= -0.05:
            self.buy_signal = True
            self.keep_signal = 0
            self.ma_stop_gain = 0
            self.start_ma_stop_gain_3 = False
            self.start_ma_stop_gain_6 = False

    
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