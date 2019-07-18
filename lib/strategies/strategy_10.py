# 移除下影線條件
# long 1 > long 2 > sell all
# target price = long 1 close + X
# long 1 用全部資金20%
# long 2 用剩下資金40%
# 停損 Long 2 Close
# 移動乖離(ATR)
# 

#%%
from .process.trade_process import trade_process
class trade_strategy_10(trade_process):
    def apply_trading_strategy(self, sar_diff, long_1_stop_gain, long_1_moving_rate, long_2_if_loss, long_2_target, long_2_moving_stop, long_2_stop_loss, delay_period, volume_max):
        self.long_signal = False
        self.short_signal = False
        self.buy_signal = False
        self.sell_signal = False
        self.keep_signal = 0
        self.set_delay = delay_period
        self.delay = 0
        self.start_ma_stop_gain = False
        self.to_target_price = False
        self.sma_stop = False

        first_action = True
        test_sell_long_1 = False
        # test_long_2 = False
        for i in range(len(self.data)):
            if self.delay == 0:
                if first_action:
                    if self.long_signal:
                        self.trade_long(i, self.long_quantity(i))
                        self.long_signal = False
                        first_action = False
                    else:
                        self.should_long(i, sar_diff, volume_max)
                elif self.do_next_trade(i,3):                   
                    if self.current_situation == 1:
                        if self.current_return(self.exist_long[0][4], self.data["Close"].iloc[i]) >= long_1_stop_gain or test_sell_long_1:
                            test_sell_long_1 = True
                            #1/3移動停利
                            if self.sell_signal:
                                self.trade_sell(i, self.sell_quantity(i))
                                self.sell_signal = False
                                test_sell_long_1 = False
                            else:
                                self.should_sell(i, sar_diff, long_1_moving_rate, long_2_target, long_2_moving_stop, long_2_stop_loss)
                        elif self.current_return(self.exist_long[0][4], self.data["Close"].iloc[i]) <= long_2_if_loss:
                            # test_long_2 = True
                            if self.long_signal:
                                self.trade_long(i, self.long_quantity(i))
                                self.long_signal = False
                                # test_long_2 = False
                            else:
                                self.should_long(i, sar_diff, volume_max)
                    elif self.current_situation ==  2:
                        if self.sell_signal:
                            self.trade_sell(i, self.sell_quantity(i))
                            self.sell_signal = False
                        else:
                            self.should_sell(i, sar_diff, long_1_moving_rate, long_2_target, long_2_moving_stop, long_2_stop_loss)
                    else:
                        if self.long_signal:
                            self.trade_long(i, self.long_quantity(i))
                            self.long_signal = False
                        else:
                            self.should_long(i, sar_diff, volume_max)
            else:
                self.delay = self.delay - 1   

        total_lose = len(self.data.loc[self.data["Win/Lose"] == "Lose"])
        total_win = len(self.data.loc[self.data["Win/Lose"] == "Win"])
        self.win_rate = (total_win/(total_win + total_lose))*100
        total_gain  = sum(self.data["Gain/Loss"].loc[self.data["Gain/Loss"] > 0 ])
        total_loss = sum(self.data["Gain/Loss"].loc[self.data["Gain/Loss"] < 0 ])
        self.profit = total_gain + total_loss
        print("Start BTC: {}, Start USD: {}" .format(self.data["BTC account"].iloc[0], self.data["USD account"].iloc[0]))
        print("Parameters: {}" .format([sar_diff, long_1_stop_gain, long_1_moving_rate, long_2_if_loss, long_2_target, long_2_moving_stop, long_2_stop_loss, delay_period, volume_max]))
        # print("Stop-Loss Rate: {}" .format(long_2_stop_loss))
        print("Win rate: {}" .format(self.win_rate))
        print("Profit: {}" .format(self.profit))
        print("____________________________")

    def do_next_trade(self, i, period):
        if i >= self.previous_action + period:
            return True
        else:
            return False 
    
    def should_long(self, i, sar_diff, volume_max):
        if self.data["Parabolic SAR"].iloc[i] > self.data["High"].iloc[i] and i > 14:
            if self.data["Average true range"].iloc[i] > self.data["Average true range"].iloc[i-1]*1.05:
                if self.data["Volume"].iloc[i] == self.data["Volume"].iloc[i-volume_max:i+1].max() and self.data["Open"].iloc[i] < self.data["Close"].iloc[i] :
                    self.long_signal = True
                    self.delay = self.set_delay
                    # self.keep_signal = self.data["Close"].iloc[i]
                    
    def should_sell(self, i, sar_diff, long_1_moving_rate, long_2_target, long_2_moving_stop, long_2_stop_loss):
        if self.current_situation == 1:
            if self.ma_stop_gain == 0:
                self.ma_stop_gain = (self.data["Close"].iloc[i] - self.exist_long[0][4])/self.exist_long[0][4] 
            else:
                if (self.data["Close"].iloc[i]-self.data["Open"].iloc[i])/self.data["Open"].iloc[i] > 0.006 or self.sma_stop:
                    if self.sma_stop == False:
                        self.sma_stop = True
                    if self.data["SMA_12"].iloc[i] > self.data["Close"].iloc[i]:
                        self.sell_signal = True
                        # self.keep_signal = 0
                        self.ma_stop_gain = 0
                        self.start_ma_stop_gain = False
                        self.to_target_price = False
                        self.sma_stop = False
                elif ((self.data["Close"].iloc[i] - self.exist_long[0][4])/self.exist_long[0][4]) <= self.ma_stop_gain*long_1_moving_rate:
                    self.sell_signal = True
                    # self.keep_signal = 0
                    self.ma_stop_gain = 0
                    self.start_ma_stop_gain = False
                    self.to_target_price = False
                    self.sma_stop = False
                elif ((self.data["Close"].iloc[i] - self.exist_long[0][4])/self.exist_long[0][4]) > self.ma_stop_gain:
                    self.ma_stop_gain = (self.data["Close"].iloc[i] - self.exist_long[0][4])/self.exist_long[0][4] 
        elif self.current_situation == 2:
            weighted_cost = (self.exist_long[0][0]*self.exist_long[0][4] + self.exist_long[1][0]*self.exist_long[1][4])/(self.exist_long[0][0] + self.exist_long[1][0])
            if self.to_target_price == False and self.data["Close"].iloc[i] >= self.exist_long[0][4]*(1 + long_2_target):
                self.to_target_price = True
                if self.start_ma_stop_gain != True:
                    self.start_ma_stop_gain = True
                if self.ma_stop_gain == 0:
                    self.ma_stop_gain = (self.data["Close"].iloc[i] - weighted_cost)/weighted_cost 
            
            if self.to_target_price:
                if self.data["Close"].iloc[i] <= weighted_cost:
                    self.sell_signal = True
                    self.ma_stop_gain = 0
                    self.start_ma_stop_gain = False
                    self.to_target_price = False
                    self.sma_stop = False
                elif (self.data["Close"].iloc[i]-self.data["Open"].iloc[i])/self.data["Open"].iloc[i] > 0.006 or self.sma_stop:
                    if self.sma_stop == False:
                        self.sma_stop = True
                    if self.data["SMA_12"].iloc[i] > self.data["Close"].iloc[i]:
                        self.sell_signal = True
                        # self.keep_signal = 0
                        self.ma_stop_gain = 0
                        self.start_ma_stop_gain = False
                        self.to_target_price = False
                        self.sma_stop = False
                elif ((self.data["Close"].iloc[i] - weighted_cost)/weighted_cost) <= self.ma_stop_gain*long_2_moving_stop:
                    self.sell_signal = True
                    self.ma_stop_gain = 0
                    self.start_ma_stop_gain = False
                    self.to_target_price = False
                    self.sma_stop = False
                elif ((self.data["Close"].iloc[i] - weighted_cost)/weighted_cost) > self.ma_stop_gain:
                    self.ma_stop_gain = (self.data["Close"].iloc[i] - weighted_cost)/weighted_cost 
            else:
                if (self.data["Close"].iloc[i] - self.exist_long[1][4])/self.exist_long[1][4] <= long_2_stop_loss:
                    self.sell_signal = True
                    self.ma_stop_gain = 0
                    self.start_ma_stop_gain = False
                    self.to_target_price = False
                    self.sma_stop = False

            '''

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
            elif (self.data["Close"].iloc[i] - self.exist_long[1][4])/self.exist_long[1][4] <= long_2_stop_loss:
                self.sell_signal = True
                # self.keep_signal = 0
                self.ma_stop_gain = 0
                self.start_ma_stop_gain = False
            '''
    
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