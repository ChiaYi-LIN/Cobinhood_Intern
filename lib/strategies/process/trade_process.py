#%%
import pandas as pd
# import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
# from mpl_finance import candlestick_ohlc
# import math
# import time
from datetime import datetime
import openpyxl
from itertools import groupby
# from plotly.tools import FigureFactory as FF
from plotly.tools import make_subplots
import plotly.offline as py
import plotly.graph_objs as go
import cufflinks
from bokeh.plotting import figure, show, output_file
from bokeh.models import ColumnDataSource, LabelSet, Label
from bokeh.io import output_notebook
cufflinks.go_offline(connected=True)
py.init_notebook_mode(connected=True)

#%%
class trade_process:
    def __init__(self,data):
        self.data = data
        self.previous_action = 0
        self.current_situation = 0
        self.start_btc_account = 0
        self.start_usd_account = 100000
        self.btc = self.start_btc_account
        self.usd = self.start_usd_account
        self.start_period_usd = 0
        self.end_period_usd = 0
        self.exist_long = []
        self.exist_short = []
        self.fees = 0.0025
        self.ma_stop_gain = 0
        self.profit = 0
        self.win_rate = 0
    
    def print_data(self, start, end):
        print(self.data.iloc[start:end,])

    def output_result(self):
        self.data.to_excel("./result/Trading_Results.xlsx", sheet_name='Results')
        self.data.loc[(self.data["Action"] == "Buy")|(self.data["Action"] == "Sell")|(self.data["Action"] == "Long")|(self.data["Action"] == "Short")].to_csv("./result/Each_Action.csv", sep = ',', encoding='utf-8')
        return
    
    def calculate_overview(self, buy_sell, win_lose):
        times = len(self.data.loc[(self.data["Action"] == buy_sell) & (self.data["Win/Lose"] == win_lose)])
        data_filter = self.data[["Rate of return", buy_sell]].loc[(self.data["Action"] == buy_sell) & (self.data["Win/Lose"] == win_lose)] 
        if sum(data_filter[buy_sell]) == 0:
            average = 0
        else:    
            average = (sum(data_filter["Rate of return"]*data_filter[buy_sell])/sum(data_filter[buy_sell]))*100
        return [buy_sell, win_lose, times, average]

    def output_overview(self):
        # Part 1
        overview_array = []
        overview_array.append(["Action", "Win/Lose", "Times", "Weighted average rate of return(%)"])
        overview_array.append(self.calculate_overview("Buy", "Win"))
        overview_array.append(self.calculate_overview("Buy", "Lose"))
        overview_array.append(self.calculate_overview("Sell", "Win"))
        overview_array.append(self.calculate_overview("Sell", "Lose"))
    
        # Print array
        overview_header = overview_array.pop(0)
        overview_array = pd.DataFrame(overview_array, columns = overview_header)

        # Part 2
        total_trade = len(self.data.loc[(self.data["Action"] == "Buy") | (self.data["Action"] == "Sell")])
        total_win = len(self.data.loc[self.data["Win/Lose"] == "Win"])
        total_lose = len(self.data.loc[self.data["Win/Lose"] == "Lose"])
        total_gain  = sum(self.data["Gain/Loss"].loc[self.data["Gain/Loss"] > 0 ])
        total_loss = sum(self.data["Gain/Loss"].loc[self.data["Gain/Loss"] < 0 ])
        self.profit = total_gain + total_loss
        if total_win == 0 or total_loss == 0 or total_lose == 0:
            profit_factor = "None"
        else:
            profit_factor = abs((total_gain/total_win)/(total_loss/total_lose))
        if total_trade == 0:
            average_win_rate = "None"
        else:
            average_win_rate = (total_win/total_trade)*100
        
        # Part 3
        max_gain = self.data["Gain/Loss"].max()
        max_loss = self.data["Gain/Loss"].min()  
        max_gain_rate = (self.data["Rate of return"].max())*100
        max_loss_rate= (self.data["Rate of return"].min())*100
        win_lose_streak = self.data["Win/Lose"].loc[(self.data["Win/Lose"] == "Win")|(self.data["Win/Lose"] == "Lose")]
        # Calculate max streak
        groups = groupby(win_lose_streak)
        result = [[label, sum(1 for _ in group)] for label, group in groups]
        result = pd.DataFrame(result, columns=["Win/Lose", "Streak"])
        max_gains = result["Streak"].loc[result["Win/Lose"] == "Win"].max()
        max_losses = result["Streak"].loc[result["Win/Lose"] == "Lose"].max()
    
        # Output txt
        with open("./result/Output.txt", "w") as text_file:
            # Part 1 output
            print(overview_array, file=text_file)
            print("============================================================", file=text_file)
            # Part 2 output
            print("總出手次數: {}" .format(total_trade), file=text_file)
            print("總獲利次數: {}" .format(total_win), file=text_file)
            print("總虧損次數: {}" .format(total_lose), file=text_file)
            print("總淨利(USD): {}" .format(self.profit), file=text_file)
            print("總獲利(USD): {}" .format(total_gain), file=text_file)
            print("總虧損(USD): {}" .format(total_loss), file=text_file)
            print("獲利因子(平均每筆獲利/平均每筆虧損): {}" .format(profit_factor), file=text_file)
            print("平均勝率(%): {}" .format(average_win_rate), file=text_file)
            print("============================================================", file=text_file)
            # Part 3 output
            print("歷史最大獲利(USD): {}" .format(max_gain), file=text_file)
            print("歷史最大虧損(USD): {}" .format(max_loss), file=text_file)
            print("歷史最大獲利率(%): {}" .format(max_gain_rate), file=text_file)
            print("歷史最大虧損率(%): {}" .format(max_loss_rate), file=text_file)
            print("最大連續獲利次數: {}" .format(max_gains), file=text_file)
            print("最大連續虧損次數: {}" .format(max_losses), file=text_file)  
    
    def trade_long(self, i, n):
        self.current_situation += n
        self.data["Situation"].iloc[i] = self.current_situation
        self.data["Action"].iloc[i] = "Long"
        self.data["Long"].iloc[i] = n
        self.data["Price"].iloc[i] = self.data["Close"].iloc[i]*(1 + self.fees)
        self.start_period_usd = self.usd
        self.usd = self.usd/2
        self.btc += self.usd/self.data["Price"].loc[i]
        # self.usd -= self.data["Price"].iloc[i]*n
        self.data["BTC account"].iloc[i] = self.btc
        self.data["USD account"].iloc[i] = self.usd
        self.previous_action = i
        self.exist_long.append([n, self.data["Price"].iloc[i], self.data["High"].iloc[i], self.data["Low"].iloc[i], self.data["Close"].iloc[i]])

    def trade_short(self, i, n):
        self.current_situation -= n
        self.data["Situation"].iloc[i] = self.current_situation
        self.data["Action"].iloc[i] = "Short"
        self.data["Short"].iloc[i] = n
        self.data["Price"].iloc[i] = self.data["Close"].iloc[i]*(1 - self.fees)
        self.start_period_usd = self.usd
        self.btc += -(self.usd/2)/self.data["Price"].loc[i]
        self.usd = self.usd*(3/2)
        # self.usd += self.data["Price"].iloc[i]*n
        self.data["BTC account"].iloc[i] = self.btc
        self.data["USD account"].iloc[i] = self.usd
        self.previous_action = i 
        self.exist_short.append([n, self.data["Price"].iloc[i], self.data["High"].iloc[i], self.data["Low"].iloc[i], self.data["Close"].iloc[i]])

    def trade_buy(self, i, n):
        self.current_situation += n
        self.data["Situation"].iloc[i] = self.current_situation
        self.data["Action"].iloc[i] = "Buy"
        self.data["Buy"].iloc[i] = n
        self.data["Price"].iloc[i] = self.data["Close"].iloc[i]*(1 + self.fees)
        self.usd = self.usd + self.btc*self.data["Price"].iloc[i]
        self.end_period_usd = self.usd
        self.btc = 0
        # self.usd -= self.data["Price"].iloc[i]*n
        self.data["BTC account"].iloc[i] = self.btc
        self.data["USD account"].iloc[i] = self.usd
        
        del self.exist_short[:]
        """
        unit = n
        return_rate_data = []
        return_sum = 0
        return_unit = 0
        while (self.exist_short != []) and (n > 0):
            if n >= self.exist_short[0][0]:
                n -= self.exist_short[0][0]
                return_rate_data.append(self.exist_short.pop(0))
            else:
                return_rate_data.append([n,self.exist_short[0][1]])
                self.exist_short[0][0] -= n
                n = 0 
        for x in range(len(return_rate_data)):
            return_unit += return_rate_data[x][0]
            return_sum += return_rate_data[x][1]*return_rate_data[x][0] 
        previous_price = (return_sum/return_unit)*unit
        current_price = self.data["Price"].iloc[i]*unit
        """
        if self.start_period_usd < self.end_period_usd:
            self.data["Win/Lose"].iloc[i] = "Win"
            self.data["Gain/Loss"].iloc[i] = abs(self.end_period_usd - self.start_period_usd)
            self.data["Rate of return"].iloc[i] = abs((self.end_period_usd - self.start_period_usd)/self.start_period_usd)
        elif self.start_period_usd > self.end_period_usd:
            self.data["Win/Lose"].iloc[i] = "Lose"
            self.data["Gain/Loss"].iloc[i] = -abs(self.end_period_usd - self.start_period_usd)
            self.data["Rate of return"].iloc[i] = -abs((self.end_period_usd - self.start_period_usd)/self.start_period_usd)
        else:
            self.data["Win/Lose"].iloc[i] = "Fair"
            self.data["Gain/Loss"].iloc[i] = 0
            self.data["Rate of return"].iloc[i] = 0
        """
        if previous_price > current_price:
            self.data["Win/Lose"].iloc[i] = "Win"
            self.data["Gain/Loss"].iloc[i] = abs(current_price - previous_price)
            self.data["Rate of return"].iloc[i] = abs((current_price - previous_price)/previous_price)
        elif previous_price < current_price:
            self.data["Win/Lose"].iloc[i] = "Lose"
            self.data["Gain/Loss"].iloc[i] = -abs(current_price - previous_price)
            self.data["Rate of return"].iloc[i] = -abs((current_price - previous_price)/previous_price)
        else:
            self.data["Win/Lose"].iloc[i] = "Fair"
            self.data["Gain/Loss"].iloc[i] = 0
            self.data["Rate of return"].iloc[i] = 0
        """
        self.start_period_usd = 0
        self.end_period_usd = 0
        self.previous_action = i
    
    def trade_sell(self, i, n):
        # origin_btc = self.btc
        self.current_situation -= n
        self.data["Situation"].iloc[i] = self.current_situation
        self.data["Action"].iloc[i] = "Sell"
        self.data["Sell"].iloc[i] = n
        self.data["Price"].iloc[i] = self.data["Close"].iloc[i]*(1 - self.fees)
        self.usd = self.usd + self.btc*self.data["Price"].iloc[i]
        self.end_period_usd = self.usd
        self.btc = 0
        # self.usd += self.data["Price"].iloc[i]*n
        self.data["USD account"].iloc[i] = self.usd
        self.data["BTC account"].iloc[i] = self.btc
        
        del self.exist_long[:]
        """
        unit = origin_btc
        return_rate_data = []
        return_sum = 0
        return_unit = 0
        while (self.exist_long != []) and (origin_btc > 0):
            if origin_btc >= self.exist_long[0][0]:
                origin_btc -= self.exist_long[0][0]
                return_rate_data.append(self.exist_long.pop(0))
            else:
                return_rate_data.append([origin_btc,self.exist_long[0][1]])
                self.exist_long[0][0] -= origin_btc
                origin_btc = 0
        for x in range(len(return_rate_data)):
            return_unit += return_rate_data[x][0]
            return_sum += return_rate_data[x][1]*return_rate_data[x][0] 
        previous_price = (return_sum/return_unit)*unit
        current_price = self.data["Price"].iloc[i]*unit
        """
        if self.start_period_usd < self.end_period_usd:
            self.data["Win/Lose"].iloc[i] = "Win"
            self.data["Gain/Loss"].iloc[i] = abs(self.end_period_usd - self.start_period_usd)
            self.data["Rate of return"].iloc[i] = abs((self.end_period_usd - self.start_period_usd)/self.start_period_usd)
        elif self.start_period_usd > self.end_period_usd:
            self.data["Win/Lose"].iloc[i] = "Lose"
            self.data["Gain/Loss"].iloc[i] = -abs(self.end_period_usd - self.start_period_usd)
            self.data["Rate of return"].iloc[i] = -abs((self.end_period_usd - self.start_period_usd)/self.start_period_usd)
        else:
            self.data["Win/Lose"].iloc[i] = "Fair"
            self.data["Gain/Loss"].iloc[i] = 0
            self.data["Rate of return"].iloc[i] = 0
        """
        if previous_price < current_price:
            self.data["Win/Lose"].iloc[i] = "Win"
            self.data["Gain/Loss"].iloc[i] = abs(current_price - previous_price)
            self.data["Rate of return"].iloc[i] = abs((current_price - previous_price)/previous_price)
        elif previous_price > current_price:
            self.data["Win/Lose"].iloc[i] = "Lose"
            self.data["Gain/Loss"].iloc[i] = -abs(current_price - previous_price)
            self.data["Rate of return"].iloc[i] = -abs((current_price - previous_price)/previous_price)
        else:
            self.data["Win/Lose"].iloc[i] = "Fair"
            self.data["Gain/Loss"].iloc[i] = 0
            self.data["Rate of return"].iloc[i] = 0
        """
        self.start_period_usd = 0
        self.end_period_usd = 0
        self.previous_action = i

    def trade_sheet(self):
        self.data["Situation"] = 0
        self.data["Action"] = None
        self.data["Long"] = None
        self.data["Short"] = None
        self.data["Buy"] = None
        self.data["Sell"] = None
        self.data["Price"] = None
        self.data["Win/Lose"] = None
        self.data["Gain/Loss"] = None
        self.data["Rate of return"] = None
        self.data["BTC account"] = None
        self.data["BTC account"].iloc[0] = self.start_btc_account
        self.data["USD account"] = None
        self.data["USD account"].iloc[0] = self.start_usd_account

#%%
class plot_data:
    def __init__(self, data):
        self.data = data
    
    def print_data(self, start, end):
        print(self.data.iloc[start:end,])
    
    def plot_all(self):
        self.bokeh_plot_technical_analysis_part()
        # self.plotly_plot_technical_analysis_part()
        # self.plotly_plot_technical_analysis_full()
        self.plot_overview_win_and_lose()

    def bokeh_plot_technical_analysis_part(self):
        inc = self.data.loc[self.data["Close"] > self.data["Open"]]
        dec = self.data.loc[self.data["Close"] <= self.data["Open"]]
        tools = "pan, wheel_zoom, box_zoom, reset, save"

        mindate = min(self.data["Datetime"])
        maxdate = max(self.data["Datetime"])
        w = 0.5 * (maxdate-mindate).total_seconds()*1000 / len(self.data["Datetime"])

        long_data = self.data.loc[self.data["Action"] == "Long"]
        short_data = self.data.loc[self.data["Action"] == "Short"]
        buy_data = self.data.loc[self.data["Action"] == "Buy"]
        sell_data = self.data.loc[self.data["Action"] == "Sell"]

        long_source = ColumnDataSource(data = dict(
            x = long_data["Datetime"],
            y = long_data["Price"],
            names = long_data["Action"] 
            ))
        
        short_source = ColumnDataSource(data = dict(
            x = short_data["Datetime"],
            y = short_data["Price"],
            names = short_data["Action"] 
            ))
        
        buy_source = ColumnDataSource(data = dict(
            x = buy_data["Datetime"],
            y = buy_data["Price"],
            names = buy_data["Action"] 
            ))
        
        sell_source = ColumnDataSource(data = dict(
            x = sell_data["Datetime"],
            y = sell_data["Price"],
            names = sell_data["Action"] 
            ))

        # output_notebook()
        p = figure(x_axis_type="datetime", tools=tools, plot_width=1000, title = "Bitcoin trade")
        p.grid.grid_line_alpha=0.3
        # Add candle
        p.segment(self.data["Datetime"], self.data["High"], self.data["Datetime"], self.data["Low"], color="black")
        p.vbar(inc["Datetime"], w, inc["Open"], inc["Close"], fill_color="#FF0000", line_color="#FF0000")
        p.vbar(dec["Datetime"], w, dec["Open"], dec["Close"], fill_color="#00FF00", line_color="#00FF00")
        # Add scatter plots
        p.circle(self.data["Datetime"], self.data["SAR Bear"], color="#0D5661", fill_alpha=0.2, size=1)
        p.circle(self.data["Datetime"], self.data["SAR Bull"], color="#E98B2A", fill_alpha=0.2, size=1)
        p.circle(x="x", y="y", color="#B5495B", fill_alpha=0.2, size=10, legend="Long", source=long_source)
        p.circle(x="x", y="y", color="#7BA23F", fill_alpha=0.2, size=10, legend="Short", source=short_source)
        p.circle(x="x", y="y", color="#4F726C", fill_alpha=0.2, size=10, legend="Buy", source=buy_source)
        p.circle(x="x", y="y", color="#F75C2F", fill_alpha=0.2, size=10, legend="Sell", source=sell_source)
        # Add legend
        p.legend.location = "top_left"
        # Add labels
        long_labels = LabelSet(x="x", y="y", text='names', level='glyph', x_offset=5, y_offset=5, source=long_source, render_mode="canvas")
        short_labels = LabelSet(x="x", y="y", text='names', level='glyph', x_offset=5, y_offset=5, source=short_source, render_mode="canvas")
        buy_labels = LabelSet(x="x", y="y", text='names', level='glyph', x_offset=5, y_offset=5, source=buy_source, render_mode="canvas")
        sell_labels = LabelSet(x="x", y="y", text='names', level='glyph', x_offset=5, y_offset=5, source=sell_source, render_mode="canvas")
        p.add_layout(long_labels)
        p.add_layout(short_labels)
        p.add_layout(buy_labels)
        p.add_layout(sell_labels)

        output_file("candlestick.html", title="Bitcoin trade")

        show(p)
        

    def plotly_plot_technical_analysis_part(self):
        trace_ohlc = go.Ohlc(
            x = self.data["Datetime"],
            open = self.data["Open"],
            high = self.data["Close"],
            low = self.data["Low"],
            close = self.data["Close"],
            name = "Candlesticks",
            increasing = dict( line = dict( color = "#FF0000" ) ),
            decreasing = dict( line = dict( color = "#00FF00" ) )
        )
        
        trace_psar_bear = go.Scatter(
            x = self.data["Datetime"],
            y = self.data["SAR Bear"],
            mode = "markers",
            marker = dict( 
                size = 3,
                color = "#0D5661"
            ),
            name = "SAR Bear"
        )

        trace_psar_bull = go.Scatter(
            x = self.data["Datetime"],
            y = self.data["SAR Bull"],
            mode = "markers",
            marker = dict( 
                size = 3,
                color = "#E98B2A" 
            ),
            name = "SAR Bull"
        )

        long_point = self.data.loc[self.data["Long"] > 0 ]
        trace_long = go.Scatter(
            x = long_point["Datetime"],
            y = long_point["Close"],
            mode = "markers+text",
            marker = dict( 
                size = 9,
                color = "#B5495B" 
            ),
            text = long_point["Action"],
            textposition ="bottom center", 
            name = "Long"
        )

        short_point = self.data.loc[self.data["Short"] > 0 ]
        trace_short = go.Scatter(
            x = short_point["Datetime"],
            y = short_point["Close"],
            mode = "markers+text",
            marker = dict( 
                size = 9,
                color = "#7BA23F" 
            ),
            text = short_point["Action"],
            textposition ="bottom center", 
            name = "Short"
        )

        buy_point = self.data.loc[self.data["Buy"] > 0 ]
        trace_buy = go.Scatter(
            x = buy_point["Datetime"],
            y = buy_point["Close"],
            mode = "markers+text",
            marker = dict( 
                size = 9,
                color = "#4F726C" 
            ),
            text = buy_point["Action"],
            textposition ="bottom center", 
            name = "Buy"
        )

        sell_point = self.data.loc[self.data["Sell"] > 0 ]
        trace_sell = go.Scatter(
            x = sell_point["Datetime"],
            y = sell_point["Close"],
            mode = "markers+text",
            marker = dict( 
                size = 9,
                color = "#F75C2F" 
            ),
            text = sell_point["Action"],
            textposition ="bottom center", 
            name = "Sell"
        )
        
        fig = make_subplots(
            rows = 2, 
            cols = 1,
            specs = [[{}],[{}]],
            shared_xaxes = True, 
            shared_yaxes = True,
            vertical_spacing = 0.001
        )

        fig.append_trace(trace_ohlc, 1, 1)
        fig.append_trace(trace_psar_bull, 1, 1)
        fig.append_trace(trace_psar_bear, 1, 1)
        fig.append_trace(trace_long, 1, 1)
        fig.append_trace(trace_short, 1, 1)
        fig.append_trace(trace_buy, 1, 1)
        fig.append_trace(trace_sell, 1, 1)
        
        fig["layout"].update(
            plot_bgcolor = "rgb(250, 250, 250)",
            height = 600,
            xaxis = dict( 
                rangeselector = dict( 
                    visible = True,
                    x = 0, 
                    y = 1,
                    yanchor = "top",
                    bgcolor = "rgba(150, 200, 250, 0.4)",
                    font = dict( size = 13 ),
                    buttons = list([                        
                        dict(
                            count = 1,
                            label = "1 yr",
                            step = "year",
                            stepmode = "backward"
                        ),
                        dict(
                            count = 3,
                            label = "3 mo",
                            step = "month",
                            stepmode = "backward"
                        ),
                        dict(
                            count = 1,
                            label = "1 mo",
                            step = "month",
                            stepmode = "backward"
                        )
                    ])
                ) 
            ),
            legend = dict(
                orientation = "h",
                x = 0.3,
                y = 1,
                yanchor = "bottom"
            ),
            margin = dict(
                t = 40,
                b = 40,
                r = 40,
                l = 40
            ),
            yaxis = dict(
                domain = [0.01, 1]
            ),
            yaxis2 = dict(
                domain = [0, 0.01]
            )
        )

        # Show plots
        py.iplot(fig, filename = "plot_part")

    def plotly_plot_technical_analysis_full(self):
        # Part 1
        trace_ohlc = go.Ohlc(
            x = self.data["Datetime"],
            open = self.data["Open"],
            high = self.data["Close"],
            low = self.data["Low"],
            close = self.data["Close"],
            name = "Candlesticks",
            increasing = dict( line = dict( color = "#FF0000" ) ),
            decreasing = dict( line = dict( color = "#00FF00" ) )
        )
        
        trace_sma_20 = go.Scatter(
            x = self.data["Datetime"], 
            y = self.data["SMA_20"],
            mode = "lines",
            line = dict(
                width = 1,
                color = "#6A4C9C"
            ),
            name = "SMA_20"
        )

        trace_sma_60 = go.Scatter(
            x = self.data["Datetime"], 
            y = self.data["SMA_60"],
            mode = "lines",
            line = dict(
                width = 1,
                color = "#D05A6E"
            ),
            name = "SMA_60"
        )
        
        trace_psar_bear = go.Scatter(
            x = self.data["Datetime"],
            y = self.data["SAR Bear"],
            mode = "markers",
            marker = dict( 
                size = 3,
                color = "#0D5661"
            ),
            name = "SAR Bear"
        )

        trace_psar_bull = go.Scatter(
            x = self.data["Datetime"],
            y = self.data["SAR Bull"],
            mode = "markers",
            marker = dict( 
                size = 3,
                color = "#E98B2A" 
            ),
            name = "SAR Bull"
        )

        long_point = self.data.loc[self.data["Long"] > 0 ]
        trace_long = go.Scatter(
            x = long_point["Datetime"],
            y = long_point["Close"],
            mode = "markers+text",
            marker = dict( 
                size = 9,
                color = "#B5495B" 
            ),
            text = long_point["Action"],
            textposition ="bottom center", 
            name = "Long"
        )

        short_point = self.data.loc[self.data["Short"] > 0 ]
        trace_short = go.Scatter(
            x = short_point["Datetime"],
            y = short_point["Close"],
            mode = "markers+text",
            marker = dict( 
                size = 9,
                color = "#7BA23F" 
            ),
            text = short_point["Action"],
            textposition ="bottom center", 
            name = "Short"
        )

        buy_point = self.data.loc[self.data["Buy"] > 0 ]
        trace_buy = go.Scatter(
            x = buy_point["Datetime"],
            y = buy_point["Close"],
            mode = "markers+text",
            marker = dict( 
                size = 9,
                color = "#4F726C" 
            ),
            text = buy_point["Action"],
            textposition ="bottom center", 
            name = "Buy"
        )

        sell_point = self.data.loc[self.data["Sell"] > 0 ]
        trace_sell = go.Scatter(
            x = sell_point["Datetime"],
            y = sell_point["Close"],
            mode = "markers+text",
            marker = dict( 
                size = 9,
                color = "#F75C2F" 
            ),
            text = sell_point["Action"],
            textposition ="bottom center", 
            name = "Sell"
        )
        
        trace_upper_bband = go.Scatter(
            x = self.data["Datetime"],
            y = self.data["Upper BBand"],
            mode = "lines",
            line = dict(
                width = 1,
                color = "#005CAF"
            ),
            name = "Upper BBand"
        )

        trace_lower_bband = go.Scatter(
            x = self.data["Datetime"],
            y = self.data["Lower BBand"],
            mode = "lines",
            line = dict(
                width = 1,
                color = "#005CAF"
            ),
            name = "Lower BBand"
        )

        trace_upper_kc = go.Scatter(
            x = self.data["Datetime"],
            y = self.data["Upper KC"],
            mode = "lines",
            line = dict(
                width = 1,
                color = "#1B813E"
            ),
            name = "Upper KC"
        )

        trace_lower_kc = go.Scatter(
            x = self.data["Datetime"],
            y = self.data["Lower KC"],
            mode = "lines",
            line = dict(
                width = 1,
                color = "#1B813E"
            ),
            name = "Lower KC"
        )
        
        # Part 2
        colors = []
        for i in range(len(self.data["Close"])):
            if i != 0:
                if self.data["Close"].iloc[i] > self.data["Close"].iloc[i-1]:
                    colors.append("#FF0000")
                else:
                    colors.append("#00ff00")
            else:
                colors.append("#00FF00")
        trace_volume = go.Bar(
            x = self.data["Datetime"],
            y = self.data["Volume"],
            marker = dict( color = colors ),
            name = "Volume"
        )
        
        # Part 3
        trace_atr = go.Scatter(
            x = self.data["Datetime"],
            y = self.data["Average true range"],
            mode = "lines",
            line = dict( color = "#0D5661" ),
            name = "ATR"
        )

        # Part 4
        trace_stochastic_oscillator_k = go.Scatter(
            x = self.data["Datetime"],
            y = self.data["%K"],
            mode = "lines",
            line = dict( color = "#B54434" ),
            name = "%K"
        )

        trace_stochastic_oscillator_d = go.Scatter(
            x = self.data["Datetime"],
            y = self.data["%D"],
            mode = "lines",
            line = dict( color = "#DDA52D" ),
            name = "%D"
        )
        
        # Set figures
        fig = make_subplots(
            rows = 4, 
            cols = 1, 
            specs = [[{}], [{}], [{}], [{}]],
            shared_xaxes = True, 
            shared_yaxes = True,
            vertical_spacing = 0.001
        )

        # Plot part 1
        fig.append_trace(trace_ohlc, 1, 1)
        fig.append_trace(trace_sma_20, 1, 1)
        fig.append_trace(trace_sma_60, 1, 1)
        fig.append_trace(trace_psar_bull, 1, 1)
        fig.append_trace(trace_psar_bear, 1, 1)
        fig.append_trace(trace_long, 1, 1)
        fig.append_trace(trace_short, 1, 1)
        fig.append_trace(trace_buy, 1, 1)
        fig.append_trace(trace_sell, 1, 1)
        fig.append_trace(trace_upper_bband, 1, 1)
        fig.append_trace(trace_lower_bband, 1, 1)
        fig.append_trace(trace_upper_kc, 1, 1)
        fig.append_trace(trace_lower_kc, 1, 1)

        # Plot part 2
        fig.append_trace(trace_volume, 2, 1)

        # Plot part 3
        fig.append_trace(trace_atr, 3, 1)

        # Plot part 4
        fig.append_trace(trace_stochastic_oscillator_k, 4, 1)
        fig.append_trace(trace_stochastic_oscillator_d, 4, 1)

        # Set styles
        fig["layout"].update(
            plot_bgcolor = "rgb(250, 250, 250)",
            height = 1000,
            xaxis = dict( 
                rangeselector = dict( 
                    visible = True,
                    x = 0, 
                    y = 1,
                    yanchor = "top",
                    bgcolor = "rgba(150, 200, 250, 0.4)",
                    font = dict( size = 13 ),
                    buttons = list([                        
                        dict(
                            count = 1,
                            label = "1 yr",
                            step = "year",
                            stepmode = "backward"
                        ),
                        dict(
                            count = 3,
                            label = "3 mo",
                            step = "month",
                            stepmode = "backward"
                        ),
                        dict(
                            count = 1,
                            label = "1 mo",
                            step = "month",
                            stepmode = "backward"
                        )
                    ])
                ) 
            ),
            legend = dict(
                orientation = "h",
                x = 0.3,
                y = 1,
                yanchor = "bottom"
            ),
            margin = dict(
                t = 40,
                b = 40,
                r = 40,
                l = 40
            ),
            yaxis = dict(
                domain = [0.3, 1]
            ),
            yaxis2 = dict(
                domain = [0.2, 0.3]
            ),
            yaxis3 = dict(
                domain = [0.1, 0.2]
            ),
            yaxis4 = dict(
                domain = [0, 0.1]
            )
        )

        # Show plots
        py.iplot(fig, filename = "plot_all")  

    def plot_overview_win_and_lose(self):
        each_win_lose = self.data.loc[(self.data["Win/Lose"] == "Win") | (self.data["Win/Lose"] == "Lose")]
        colors = []
        for i in range(len(each_win_lose)):
            if each_win_lose["Gain/Loss"].iloc[i] >= 0:
                colors.append("#DB4D6D")
            else:
                colors.append("#4A593D")

        x_axis = each_win_lose["Datetime"].apply(lambda x: x.strftime("%Y/%m/%d %H:%M"))
        trace_each_action_by_datetime = go.Bar(
            x = x_axis,
            y = each_win_lose["Gain/Loss"],
            base = 0,
            marker = dict( color = colors ),
            name = "Gain/Loss in each trade"
        )

        trace_cumulate_gain_and_loss = go.Scatter(
            x = x_axis,
            # y = each_win_lose["Gain/Loss"].cumsum(),
            y = each_win_lose["USD account"],
            mode = "lines",
            line = dict( color = "#B54434" ),
            name = "Cumulated Gain/Loss after each trade"
        )
        
        fig = make_subplots(
            rows = 2, 
            cols = 1, 
            specs = [[{}], [{}]],
            shared_xaxes = True, 
            shared_yaxes = False,
            vertical_spacing = 0.001
        )

        fig.append_trace(trace_each_action_by_datetime, 1, 1)
        fig.append_trace(trace_cumulate_gain_and_loss, 2, 1)
        
        # fig = go.Figure(data = [trace_each_action_by_datetime])

        # Set styles
        fig["layout"].update(
            title = "Gain and loss in each trade (USD) // Cumulated gain and loss after each trade (USD)",
            plot_bgcolor = "rgb(250, 250, 250)",
            height = 600,
            xaxis = dict( 
                rangeselector = dict( 
                    visible = True,
                    x = 0, 
                    y = 1,
                    yanchor = "top",
                    bgcolor = "rgba(150, 200, 250, 0.4)",
                    font = dict( size = 13 ),
                    buttons = list([                        
                        dict(
                            count = 1,
                            label = "1 yr",
                            step = "year",
                            stepmode = "backward"
                        ),
                        dict(
                            count = 3,
                            label = "3 mo",
                            step = "month",
                            stepmode = "backward"
                        ),
                        dict(
                            count = 1,
                            label = "1 mo",
                            step = "month",
                            stepmode = "backward"
                        )
                    ])
                )
            ),
            legend = dict(
                orientation = "h",
                x = 0.45,
                y = 1,
                yanchor = "top"
            ),
            margin = dict(
                t = 40,
                b = 40,
                r = 40,
                l = 40
            ),
            yaxis = dict(
                domain = [0.5, 1]
            ),
            yaxis2 = dict(
                domain = [0, 0.5]
            ) 
        )

        py.iplot(fig, filename = "plot_overview_win_and_lose")

        # sns_plot = sns.barplot(x = "Datetime", y = "Gain/Loss", data = each_win_lose, hue = "Win/Lose")
        # sns_plot.get_figure().savefig("./Gain and Loss in each trade.png")

    def plot_overview_account_balance(self):
        # btc_account_balance = self.data.loc[(self.data["BTC account"] >= 0) | (self.data["BTC account"] < 0)]
        usd_account_balance = self.data.loc[(self.data["USD account"] >= 0) | (self.data["USD account"] < 0)]
        '''
        trace_btc_account_balance = go.Scatter(
            x = btc_account_balance["Datetime"],
            y = btc_account_balance["BTC account"],
            mode = "lines",
            line = dict( color = "#DDA52D" ),
            name = "BTC account balance"
        )
        '''
        trace_usd_account_balance = go.Scatter(
            x = usd_account_balance["Datetime"],
            y = usd_account_balance["USD account"],
            mode = "lines",
            line = dict( color = "#B54434" ),
            name = "USD account balance"
        )

        # Set figures
        '''
        fig = make_subplots(
            rows = 2, 
            cols = 1, 
            specs = [[{}], [{}]],
            shared_xaxes = True, 
            shared_yaxes = True,
            vertical_spacing = 0.001
        )

        fig.append_trace(trace_btc_account_balance, 1, 1)
        fig.append_trace(trace_usd_account_balance, 2, 1)
        '''
        fig = go.Figure(data = [trace_usd_account_balance])
        # Set styles
        fig["layout"].update(
            title = "Account balance over time (USD)",
            plot_bgcolor = "rgb(250, 250, 250)",
            height = 600,
            xaxis = dict( 
                rangeselector = dict( 
                    visible = True,
                    x = 0, 
                    y = 1,
                    yanchor = "top",
                    bgcolor = "rgba(150, 200, 250, 0.4)",
                    font = dict( size = 13 ),
                    buttons = list([                        
                        dict(
                            count = 1,
                            label = "1 yr",
                            step = "year",
                            stepmode = "backward"
                        ),
                        dict(
                            count = 3,
                            label = "3 mo",
                            step = "month",
                            stepmode = "backward"
                        ),
                        dict(
                            count = 1,
                            label = "1 mo",
                            step = "month",
                            stepmode = "backward"
                        )
                    ])
                ) 
            ),
            legend = dict(
                orientation = "h",
                x = 0.3,
                y = 1,
                yanchor = "bottom"
            ),
            margin = dict(
                t = 40,
                b = 40,
                r = 40,
                l = 40
            ),
        )

        py.iplot(fig, filename = "plot_overview_account_balance")

#%%
class technical_analysis:
    def __init__(self, data):
        self.data = data
        self.ohlc_dict = {                                                                                                             
        'Timestamp':'last',
        'Open':'first',                                                                                                    
        'High':'max',                                                                                                       
        'Low':'min',                                                                                                        
        'Close': 'last',                                                                                                    
        'Volume': 'sum'
        }

    def print_data(self, start, end):
        print(self.data.iloc[start:end,])

    def add_real_datetime(self):
        self.data["Datetime"] = None
        self.data["Datetime"] = pd.to_datetime(self.data["Timestamp"], unit='ms')

    def to_5min(self):
        self.data = self.data.set_index("Datetime")
        self.data = self.data.resample('5T', closed='left', label='left').apply(self.ohlc_dict)
        self.data = self.data.reset_index()

    def to_15min(self):
        self.data = self.data.set_index("Datetime")
        self.data = self.data.resample('15T', closed='left', label='left').apply(self.ohlc_dict)
        self.data = self.data.reset_index()

    def to_60min(self):
        self.data = self.data.set_index("Datetime")
        self.data = self.data.resample('60T', closed='left', label='left').apply(self.ohlc_dict)
        self.data = self.data.reset_index()

    def drop_blank(self):
        self.data = self.data.loc[self.data["Volume"] > 0]
        # self.data = self.data.dropna(inplace = True) 
        self.data = self.data.reset_index(drop=True)

    def add_ema(self, period):
        ema_colname = "EMA_" + str(period)
        self.data[ema_colname] = None
        self.data[ema_colname] = self.data["Close"].ewm(span=period, adjust=False).mean()
    
    def add_sma(self, period):
        sma_colname = "SMA_" + str(period)
        self.data[sma_colname] = None
        self.data[sma_colname] = self.data["Close"].rolling(period).mean()

    def add_parabolic_sar(self):
        iaf = 0.02
        maxaf = 0.2
        high = list(self.data["High"])
        low = list(self.data["Low"])
        close = list(self.data["Close"])
        length = len(self.data)
        psar = close[0:len(close)]
        psarbull = [None] * length
        psarbear = [None] * length
        bull = True
        af = iaf
        # ep = low[0]
        hp = high[0]
        lp = low[0]

        for i in range(2,length):
            if bull:
                psar[i] = psar[i - 1] + af * (hp - psar[i - 1])
            else:
                psar[i] = psar[i - 1] + af * (lp - psar[i - 1])
            
            reverse = False
            
            if bull:
                if low[i] < psar[i]:
                    bull = False
                    reverse = True
                    psar[i] = hp
                    lp = low[i]
                    af = iaf
            else:
                if high[i] > psar[i]:
                    bull = True
                    reverse = True
                    psar[i] = lp
                    hp = high[i]
                    af = iaf
        
            if not reverse:
                if bull:
                    if high[i] > hp:
                        hp = high[i]
                        af = min(af + iaf, maxaf)
                    if low[i - 1] < psar[i]:
                        psar[i] = low[i - 1]
                    if low[i - 2] < psar[i]:
                        psar[i] = low[i - 2]
                else:
                    if low[i] < lp:
                        lp = low[i]
                        af = min(af + iaf, maxaf)
                    if high[i - 1] > psar[i]:
                        psar[i] = high[i - 1]
                    if high[i - 2] > psar[i]:
                        psar[i] = high[i - 2]
                        
            if bull:
                psarbull[i] = psar[i]
            else:
                psarbear[i] = psar[i]

        self.data["Parabolic SAR"] = None
        self.data["SAR Bear"] = None
        self.data["SAR Bull"] = None
        self.data["Parabolic SAR"] = psar
        self.data["SAR Bear"] = psarbear
        self.data["SAR Bull"] = psarbull

        return
    
    def add_average_true_range(self, period):
        self.data["True range"] = None
        for i in range(len(self.data)):
            if i == 0:
                self.data["True range"].iloc[i] = self.data["High"].iloc[i] - self.data["Low"].iloc[i] 
            else:
                tr_1 = self.data["High"].iloc[i] - self.data["Low"].iloc[i]
                tr_2 = abs(self.data["High"].iloc[i] - self.data["Close"].iloc[i-1])
                tr_3 = abs(self.data["Low"].iloc[i] - self.data["Close"].iloc[i-1])
                self.data["True range"].iloc[i] = max(tr_1, tr_2, tr_3)
        
        self.data["Average true range"] = None
        current_atr = 0
        if len(self.data) < period:
            return 0
        else:
            for i in range(len(self.data)):
                if i >= period-1:
                    if current_atr == 0:
                        current_atr = sum(self.data["True range"].iloc[i-period+1:i+1]) / period
                        self.data["Average true range"].iloc[i] = current_atr
                    else:
                        current_atr = (current_atr*(period - 1) + self.data["True range"].iloc[i]) / period
                        self.data["Average true range"].iloc[i] = current_atr     

    def add_bbands(self, n = 20, ndev = 2):
        self.data["Upper BBand"] = None
        self.data["Lower BBand"] = None
        ma_bb = self.data["Close"].rolling(n).mean()
        m_std = self.data["Close"].rolling(n).std()
        self.data["Upper BBand"] = ma_bb + ndev*m_std
        self.data["Lower BBand"] = ma_bb - ndev*m_std  

    def add_stochastic_oscillator(self, n1 = 20, n2 = 3):
        self.data["%K"] = None
        self.data["%D"] = None
        self.data["%K"] = ((self.data["Close"] - self.data["Low"].rolling(n1).min())/(self.data["High"].rolling(n1).max() - self.data["Low"].rolling(n1).min()))*100
        self.data["%D"] = self.data["%K"].rolling(n2).mean()
    
    def add_keltner_channels(self, n = 2):
        self.data["Upper KC"] = None
        self.data["Lower KC"] = None
        self.data["Upper KC"] = self.data["SMA_20"] + n*self.data["Average true range"]
        self.data["Lower KC"] = self.data["SMA_20"] - n*self.data["Average true range"]

#%%
"""
data = 0
data_timestamp = "Timestamp"
data_opem = "Open"
data_high = "High"
data_low = "Low"
data_close = "Close"
data_volume = "Volume"
ta_test = 0
plot = 0
ts_test = 0

# Import data
data = pd.read_csv("./BTC_USD_2018.csv", header = None, names = [data_timestamp, data_opem, data_close, data_high, data_low, data_volume])

# Technical analysis
ta_test = technical_analysis(data.iloc[0:50000,])
ta_test.add_real_datetime()
ta_test.to_15min()

ta_test.add_parabolic_sar()
ta_test.add_average_true_range(14)
ta_test.add_sma(20)
ta_test.add_sma(60)
ta_test.add_bbands()
ta_test.add_stochastic_oscillator()
ta_test.add_keltner_channels()
# ta_test.print_data(0,10)

# Trading strategy
ts_test = trade_strategy(ta_test.data) 
# ts_test.print_data(0,10)
ts_test.apply_trading_strategy()
ts_test.output_result()
ts_test.output_overview()

# Plot results
plot = plot_data(ta_test.data)
# plot.print_data(0,10)
plot.plot_all()
"""