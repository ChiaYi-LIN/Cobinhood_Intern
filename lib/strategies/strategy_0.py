#%%
from .process.trade_process import trade_process
class trade_strategy_1(trade_process):
    def apply_trading_strategy(self):
        self.long_signal = False
        self.short_signal = False
        self.buy_signal = False
        self.sell_signal = False

        first_action = True
        for i in range(len(self.data)):
            if first_action:
                #long or short
                if self.should_long(i):
                    self.trade_long(i, self.long_quantity(i))
                elif self.should_short(i):
                    self.trade_short(i, self.short_quantity(i))

                first_action = False
            elif self.do_next_trade(i,3):
                if self.current_situation > 0:
                    #long or sell
                    if self.should_sell(i):
                        self.trade_sell(i, self.sell_quantity(i))
                    elif self.should_long(i):
                        self.trade_long(i, self.long_quantity(i))
                elif self.current_situation < 0:
                    #short or buy
                    if self.should_buy(i):
                        self.trade_buy(i, self.buy_quantity(i))
                    elif self.should_short(i):
                        self.trade_short(i, self.short_quantity(i))
                else:
                    #long or short
                    if self.should_long(i):
                        self.trade_long(i, self.long_quantity(i))
                    elif self.should_short(i):
                        self.trade_short(i, self.short_quantity(i))
    
    def do_next_trade(self, i, period):
        if i >= self.previous_action + period:
            return True
        else:
            return False 
    
    def should_long(self, i):
        if (self.data["SMA_20"].iloc[i-1] <= self.data["SMA_60"].iloc[i-1]) and (self.data["SMA_20"].iloc[i] > self.data["SMA_60"].iloc[i]):
            return True
        else:
            return False
    
    def should_short(self, i):
        if self.current_situation > -5:
            if (self.data["Upper BBand"].iloc[i-1] <= self.data["Upper KC"].iloc[i-1]) and (self.data["Upper BBand"].iloc[i] > self.data["Upper KC"].iloc[i]):
                return True
            else:
                return False
        else:
            return False

    def should_buy(self, i):
        if (self.data["Lower KC"].iloc[i] > self.data["Lower BBand"].iloc[i]) and (self.data["Parabolic SAR"].iloc[i] > self.data["High"].iloc[i]):
            return True
        else:
            return False

    def should_sell(self, i):
        if self.data["SMA_20"].iloc[i] < self.data["SMA_60"].iloc[i]:
            return True
        else:
            return False
    
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