import urllib
import numpy as np
from StartingClasses import *
import time
import datetime
from numpy import loadtxt
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import matplotlib
#from mplfinance.original_flavor import candlestick_ochl as candlestick
import mplfinance
import pylab
import tkinter as Tk
matplotlib.rcParams.update({'font.size': 9})


### Global Variables
currentDataTF = False


### MAIN FUNCTIONS
### Test and Stats
def statData(stock):

    ### Pull Stock
    data = stockData(stock)

    ### CONFIGVAR
    configVar = configPull()
    ### Limit Variables
    macdShort = configVar[0]
    macdLong = configVar[1]
    macdSignal = configVar[2]
    kPeriod = configVar[3]
    dPeriod = configVar[4]
    sLimitHigh = configVar[5]
    sLimitLow = configVar[6]
    MA1 = configVar[7]
    MA2 = configVar[8]
    rsiPeriod = configVar[9]
    rLimitHigh = configVar[10]
    rLimitLow = configVar[11]
    mfiPeriod = configVar[12]
    mLimitHigh = configVar[13]
    mLimitLow = configVar[14]
    ### TradeVariables
    B = configVar[15]
    S = configVar[16]

    ### Calculate Indicators
    SP = len(data.date[MA2 - 1:])
    ### Moving Averages
    Av1 = data.movingAverage(data.closep, MA1)
    Av2 = data.movingAverage(data.closep, MA2)
    ### MACD
    nema = macdSignal
    emaslow, emafast, macd, ema9 = data.macd(macdLong, macdShort, nema)
    ### RSI
    rsi = data.rsi(rsiPeriod)
    ### Stochastic
    k = data.stochastic(kPeriod)
    d = data.expMovingAverage(k, dPeriod)
    ### MFI
    mfi = data.mfi(mfiPeriod)

    ### Tracking Variables
    stance = 'none'
    buyPrice = 0
    sellPrice = 0
    tradeCount = 0
    overallStartingPrice = 0
    overallEndingPrice = 0
    totalProfit = 0
    inSignal = False
    outSignal = False

    ### Time Tracking Variables
    startingTime = 0
    endingTime = 0
    overallStartingTime = 0
    overallEndingTime = 0
    totalInvestedTime = 0

    ### Calculate Stats
    for i in range(0, len(data.date)):

        s = 0
        b = 0

        ### Buy/Sell signals
        if macd[i] > ema9[i]:  # macd[i] > ema9[i] and macd[i-1] < ema9[i-1]:
            b += 1
        if k[i] < d[i]:  # k[i] > d[i] and k[i-1] < d[i-1]:
            b += 1
        if k[i] < sLimitLow:  # k[i] > sLimitLow and k[i-1] < sLimitLow:
            b += 1
        if rsi[i] < rLimitLow:  # rsi[i] > rLimitLow and rsi[i-1] < rLimitLow:
            b += 1
        if mfi[i] < mLimitLow:  # mfi[i] > mLimitLow and mfi[i-1] < mLimitLow:
            b += 1

        ### Buy/Sell signals
        if macd[i] < ema9[i]:  # macd[i] < ema9[i] and macd[i-1] > ema9[i-1]:
            s += 1
        if k[i] > d[i]:  # k[i] < d[i] and k[i-1] > d[i-1]:
            s += 1
        if k[i] > sLimitHigh:  # k[i] < sLimitHigh and k[i-1] > sLimitHigh:
            s += 1
        if rsi[i] > rLimitHigh:  # rsi[i] < rLimitHigh and rsi[i-1] > rLimitHigh:
            s += 1
        if mfi[i] > mLimitHigh:  # mfi[i] < mLimitHigh and mfi[i-1] > mLimitHigh:
            s += 1

        if stance == 'none':
            if b >= B:
                buyPrice = data.closep[i]
                stance = 'In'
                startingTime = data.date[i]
                overallStartingTime = data.date[i]
                overallStartingPrice = buyPrice
                inSignal = True

        elif stance == 'In':
            if s >= S:
                sellPrice = data.closep[i]
                totalProfit += (sellPrice - buyPrice)
                stance = 'Out'
                endingTime = data.date[i]
                #totalInvestedTime += (endingTime - startingTime)
                tradeCount += 1
                overallEndingTime = data.date[i]
                overallEndingPrice = sellPrice
                inSignal = False
                outSignal = True

        elif stance == 'Out':
            if b >= B:
                buyPrice = data.closep[i]
                stance = 'In'
                startingTime = data.date[i]
                inSignal = True
                outSignal = False

        i += 1

    ## Calculated Variables
    totalProfit = round(totalProfit, 2)
    percentProfit = round((totalProfit / overallStartingPrice) * 100, 2)
    averageTradeLength = round(totalInvestedTime / tradeCount, 2)
    overallTime = 50 #overallEndingTime - overallStartingTime
    percentageInvestedTime = 50 # round((totalInvestedTime / overallTime) * 100, 2)
    naturalProfit = round(overallEndingPrice - overallStartingPrice, 2)
    naturalPercentProfit = round((naturalProfit / overallStartingPrice) * 100, 2)
    performance = round(totalProfit - naturalProfit, 2)
    percentPerformance = round(percentProfit - naturalPercentProfit, 2)

    ###Create Graph
    graphData(stock, data, SP, Av1, Av2, mfi, rsi, k, d, macd, ema9, emaslow, emafast, inSignal, outSignal)

    ### STATS WINDOW
    SD = Tk.Tk()
    SD.geometry('220x300+610+100')

    ### Title Bar
    SD.title(stock + ' STATS')
    SD.iconbitmap('Zephyr Limit 1.4/Images/Favicon.ico')

    ### SETTING LABELS
    ### Total Time Trading
    overallTimeVal = Tk.StringVar(SD, 'Trading Period Length:')
    overallTimeVal2 = Tk.DoubleVar(SD, int(overallTime))
    overallTimeLabel = Tk.Label(SD, textvariable=overallTimeVal)
    overallTimeLabel2 = Tk.Label(SD, textvariable=overallTimeVal2)
    overallTimeLabel.grid(row=0, column=0, sticky=Tk.E)
    overallTimeLabel2.grid(row=0, column=1, sticky=Tk.W)

    ### Total Time Invested
    totalInvestedTimeVal = Tk.StringVar(SD, 'Total Exposure Time:')
    totalInvestedTimeVal2 = Tk.DoubleVar(SD, int(totalInvestedTime))
    totalInvestedTimeLabel = Tk.Label(SD, textvariable=totalInvestedTimeVal)
    totalInvestedTimeLabel2 = Tk.Label(SD, textvariable=totalInvestedTimeVal2)
    totalInvestedTimeLabel.grid(row=1, column=0, sticky=Tk.E)
    totalInvestedTimeLabel2.grid(row=1, column=1, sticky=Tk.W)

    ### Time Invested as Percentage of Time Trading
    percentInvestedTimeVal = Tk.StringVar(SD, 'Percent Exposed Time:')
    percentInvestedTimeVal2 = Tk.DoubleVar(SD, round(percentageInvestedTime, 2))
    percentInvestedTimeLabel = Tk.Label(SD, textvariable=percentInvestedTimeVal)
    percentInvestedTimeLabel2 = Tk.Label(SD, textvariable=percentInvestedTimeVal2)
    percentInvestedTimeLabel.grid(row=2, column=0, sticky=Tk.E)
    percentInvestedTimeLabel2.grid(row=2, column=1, sticky=Tk.W)

    ### Total Count
    tradeCountVal = Tk.StringVar(SD, 'Total Number of Trades:')
    tradeCountVal2 = Tk.DoubleVar(SD, tradeCount)
    tradeCountLabel = Tk.Label(SD, textvariable=tradeCountVal)
    tradeCountLabel2 = Tk.Label(SD, textvariable=tradeCountVal2)
    tradeCountLabel.grid(row=3, column=0, sticky=Tk.E)
    tradeCountLabel2.grid(row=3, column=1, sticky=Tk.W)

    ### Average Trade Length
    averageTradeLengthVal = Tk.StringVar(SD, 'Average Trade Length:')
    averageTradeLengthVal2 = Tk.DoubleVar(SD, averageTradeLength)
    averageTradeLengthLabel = Tk.Label(SD, textvariable=averageTradeLengthVal)
    averageTradeLengthLabel2 = Tk.Label(SD, textvariable=averageTradeLengthVal2)
    averageTradeLengthLabel.grid(row=4, column=0, sticky=Tk.E)
    averageTradeLengthLabel2.grid(row=4, column=1, sticky=Tk.W)

    ### Total Profit
    totalProfitVal = Tk.StringVar(SD, 'Total Profit:')
    totalProfitVal2 = Tk.DoubleVar(SD, totalProfit)
    totalProfitLabel = Tk.Label(SD, textvariable=totalProfitVal)
    totalProfitLabel2 = Tk.Label(SD, textvariable=totalProfitVal2)
    totalProfitLabel.grid(row=5, column=0, sticky=Tk.E)
    totalProfitLabel2.grid(row=5, column=1, sticky=Tk.W)

    ### Percent Profit
    percentProfitVal = Tk.StringVar(SD, 'Percent Profit:')
    percentProfitVal2 = Tk.DoubleVar(SD, percentProfit)
    percentProfitLabel = Tk.Label(SD, textvariable=percentProfitVal)
    percentProfitLabel2 = Tk.Label(SD, textvariable=percentProfitVal2)
    percentProfitLabel.grid(row=6, column=0, sticky=Tk.E)
    percentProfitLabel2.grid(row=6, column=1, sticky=Tk.W)

    ### Natural Profit
    naturalProfitVal = Tk.StringVar(SD, 'Natural Profit:')
    naturalProfitVal2 = Tk.DoubleVar(SD, naturalProfit)
    naturalProfitLabel = Tk.Label(SD, textvariable=naturalProfitVal)
    naturalProfitLabel2 = Tk.Label(SD, textvariable=naturalProfitVal2)
    naturalProfitLabel.grid(row=7, column=0, sticky=Tk.E)
    naturalProfitLabel2.grid(row=7, column=1, sticky=Tk.W)

    ### Natural Percent Profit
    naturalPercentProfitVal = Tk.StringVar(SD, 'Natural Percent Profit:')
    naturalPercentProfitVal2 = Tk.DoubleVar(SD, naturalPercentProfit)
    naturalPercentProfitLabel = Tk.Label(SD, textvariable=naturalPercentProfitVal)
    naturalPercentProfitLabel2 = Tk.Label(SD, textvariable=naturalPercentProfitVal2)
    naturalPercentProfitLabel.grid(row=8, column=0, sticky=Tk.E)
    naturalPercentProfitLabel2.grid(row=8, column=1, sticky=Tk.W)

    ### Performance
    performanceVal = Tk.StringVar(SD, 'Performance:')
    performanceVal2 = Tk.DoubleVar(SD, performance)
    performanceLabel = Tk.Label(SD, textvariable=performanceVal)
    performanceLabel2 = Tk.Label(SD, textvariable=performanceVal2)
    performanceLabel.grid(row=9, column=0, sticky=Tk.E)
    performanceLabel2.grid(row=9, column=1, sticky=Tk.W)

    ### Percent Performance
    percentPerformanceVal = Tk.StringVar(SD, 'Percent Performance:')
    percentPerformanceVal2 = Tk.DoubleVar(SD, percentPerformance)
    percentPerformanceLabel = Tk.Label(SD, textvariable=percentPerformanceVal)
    percentPerformanceLabel2 = Tk.Label(SD, textvariable=percentPerformanceVal2)
    percentPerformanceLabel.grid(row=10, column=0, sticky=Tk.E)
    percentPerformanceLabel2.grid(row=10, column=1, sticky=Tk.W)

    return


### Create Graph
def graphData(stock, data, SP, Av1, Av2, mfi, rsi, k, d, macd, ema9, emaslow, emafast, inSignal, outSignal):

    date = data.date
    closep = data.closep
    highp = data.highp
    lowp = data.lowp
    openp = data.openp
    volume = data.volume

    configVar = configPull()
    macdShort = configVar[0]
    macdLong = configVar[1]
    macdSignal = configVar[2]
    kPeriod = configVar[3]
    dPeriod = configVar[4]
    sLimitHigh = configVar[5]
    sLimitLow = configVar[6]
    MA1 = configVar[7]
    MA2 = configVar[8]
    rsiPeriod = configVar[9]
    rLimitHigh = configVar[10]
    rLimitLow = configVar[11]
    mfiPeriod = configVar[12]
    mLimitHigh = configVar[13]
    mLimitLow = configVar[14]

    ### Variables
    plt.ion()

    ### Price Plot
    dataFrame = yf.download(stock, start="2020-01-01", end="2021-01-01", multi_level_index=False)
    mplfinance.plot(dataFrame, type='candle', style='yahoo', title=stock, ylabel='Price', block=False)
    
    ### MA and Volume
    fig = plt.figure(facecolor='#07000d')
    ax1 = plt.subplot2grid((7, 4), (2, 0), rowspan=3, colspan=4, facecolor='#07000d')
    ax1.grid(True, color='w')
    ax1.xaxis.set_major_locator(mticker.MaxNLocator(10))
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))
    ax1.yaxis.label.set_color("w")
    ax1.spines['bottom'].set_color("#5998ff")
    ax1.spines['top'].set_color("#5998ff")
    ax1.spines['left'].set_color("#5998ff")
    ax1.spines['right'].set_color("#5998ff")
    ax1.text(0.015, 0.95, 'Moving Average and Volume', verticalalignment='top', color='w', transform=ax1.transAxes)
    ax1.tick_params(axis='y', colors='w')
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper'))
    ax1.tick_params(axis='x', colors='w')
    ### MA Plot
    ax1.plot(date[-SP:], Av1[-SP:], '#4ee6fd', label='Fast', linewidth=1.5)
    ax1.plot(date[-SP:], Av2[-SP:], '#e1edf9', label='Slow', linewidth=1.5)
    ### Legend
    maLeg = plt.legend(loc=9, ncol=2, prop={'size': 7}, fancybox=True, borderaxespad=0.)
    maLeg.get_frame().set_alpha(0.4)
    textEd = pylab.gca().get_legend().get_texts()
    pylab.setp(textEd[0:5], color='w')
    ### Volume Overlay
    ax1v = ax1.twinx()
    ax1v.fill_between(date[-SP:], 0, volume[-SP:], facecolor='#00ffe8', alpha=.4)
    ax1v.axes.yaxis.set_ticklabels([])
    ax1v.grid(False)
    ax1v.set_ylim(0, 3 * volume.max())
    ax1v.spines['bottom'].set_color("#5998ff")
    ax1v.spines['top'].set_color("#5998ff")
    ax1v.spines['left'].set_color("#5998ff")
    ax1v.spines['right'].set_color("#5998ff")
    ax1v.tick_params(axis='x', colors='w')
    ax1v.tick_params(axis='y', colors='w')

    ### MACD Plot
    ax2 = plt.subplot2grid((7, 4), (0, 0), sharex=ax1, rowspan=1, colspan=4, facecolor='#07000d')
    fillcolor = '#00ffe8'
    posCol = '#386d13'
    negCol = '#8f2020'
    ax2.plot(date[-SP:], macd[-SP:], color='#4ee6fd', lw=2)
    ax2.plot(date[-SP:], ema9[-SP:], color='#e1edf9', lw=1)
    ax2.fill_between(date[-SP:], macd[-SP:] - ema9[-SP:], 0, alpha=0.5, facecolor=fillcolor, edgecolor=fillcolor)
    plt.gca().yaxis.set_major_locator(mticker.MaxNLocator(prune='upper', nbins=5))
    ax2.fill_between(date[-SP:], max(macd), min(macd), where=(macd[-SP:] <= ema9[-SP:]), facecolor=negCol, edgecolor=negCol, alpha=0.5)
    ax2.fill_between(date[-SP:], min(macd), max(macd), where=(macd[-SP:] >= ema9[-SP:]), facecolor=posCol, edgecolor=posCol, alpha=0.5)
    ax2.spines['bottom'].set_color("#5998ff")
    ax2.spines['top'].set_color("#5998ff")
    ax2.spines['left'].set_color("#5998ff")
    ax2.spines['right'].set_color("#5998ff")
    ax2.text(0.015, 0.95, 'MACD', verticalalignment='top', color='w', transform=ax2.transAxes)
    ax2.tick_params(axis='x', colors='w')
    ax2.tick_params(axis='y', colors='w')

    ### Stochastic Plot
    ax4 = plt.subplot2grid((7, 4), (1, 0), sharex=ax1, rowspan=1, colspan=4, facecolor='#07000d')
    posCol = '#386d13'
    negCol = '#8f2020'
    highLimit = sLimitHigh
    lowLimit = sLimitLow
    ax4.plot(date[-SP:], k[-SP:], color='#4ee6fd', lw=2)
    ax4.plot(date[-SP:], d[-SP:], color='#e1edf9', lw=1)
    ax4.fill_between(date[-SP:], 100, 0, where=(k[-SP:] >= highLimit), facecolor=negCol, edgecolor=negCol, alpha=0.5)
    ax4.fill_between(date[-SP:], 0, 100, where=(k[-SP:] <= lowLimit), facecolor=posCol, edgecolor=posCol, alpha=0.5)
    ax4.axhline(highLimit, color=negCol)
    ax4.axhline(lowLimit, color=posCol)
    ax4.set_yticks([lowLimit, highLimit])
    ax4.spines['bottom'].set_color("#5998ff")
    ax4.spines['top'].set_color("#5998ff")
    ax4.spines['left'].set_color("#5998ff")
    ax4.spines['right'].set_color("#5998ff")
    ax4.text(0.015, 0.95, 'Stochastic', verticalalignment='top', color='w', transform=ax4.transAxes)
    ax4.tick_params(axis='x', colors='w')
    ax4.tick_params(axis='y', colors='w')

    ### RSI Plot
    ax0 = plt.subplot2grid((7, 4), (5, 0), sharex=ax1, rowspan=1, colspan=4, facecolor='#07000d')
    rsiCol = '#4ee6fd'
    posCol = '#386d13'
    negCol = '#8f2020'
    highLimit = rLimitHigh
    lowLimit = rLimitLow
    ax0.plot(date[-SP:], rsi[-SP:], rsiCol, linewidth=1.5)
    ax0.axhline(highLimit, color=negCol)
    ax0.axhline(lowLimit, color=posCol)
    ax0.fill_between(date[-SP:], 100, 0, where=(rsi[-SP:] >= highLimit), facecolor=negCol, edgecolor=negCol, alpha=0.5)
    ax0.fill_between(date[-SP:], 0, 100, where=(rsi[-SP:] <= lowLimit), facecolor=posCol, edgecolor=posCol, alpha=0.5)
    ax0.set_yticks([lowLimit, highLimit])
    ax0.spines['bottom'].set_color("#5998ff")
    ax0.spines['top'].set_color("#5998ff")
    ax0.spines['left'].set_color("#5998ff")
    ax0.spines['right'].set_color("#5998ff")
    ax0.text(0.015, 0.95, 'RSI', verticalalignment='top', color='w', transform=ax0.transAxes)
    ax0.tick_params(axis='x', colors='w')
    ax0.tick_params(axis='y', colors='w')

    ### MFI Plot
    ax3 = plt.subplot2grid((7, 4), (6, 0), sharex=ax1, rowspan=1, colspan=4, facecolor='#07000d')
    mfiCol = '#4ee6fd'
    posCol = '#386d13'
    negCol = '#8f2020'
    highLimit = mLimitHigh
    lowLimit = mLimitLow
    ax3.plot(date[-SP:], mfi[-SP:], mfiCol, linewidth=1.5)
    ax3.axhline(highLimit, color=negCol)
    ax3.axhline(lowLimit, color=posCol)
    ax3.fill_between(date[-SP:], 100, 0, where=(mfi[-SP:] >= highLimit), facecolor=negCol, edgecolor=negCol, alpha=0.5)
    ax3.fill_between(date[-SP:], 0, 100, where=(mfi[-SP:] <= lowLimit), facecolor=posCol, edgecolor=posCol, alpha=0.5)
    ax3.set_yticks([lowLimit, highLimit])
    ax3.spines['bottom'].set_color("#5998ff")
    ax3.spines['top'].set_color("#5998ff")
    ax3.spines['left'].set_color("#5998ff")
    ax3.spines['right'].set_color("#5998ff")
    ax3.text(0.015, 0.95, 'MFI', verticalalignment='top', color='w', transform=ax3.transAxes)
    ax3.tick_params(axis='y', colors='w')
    ax3.tick_params(axis='x', colors='w')

    ### X Axis Label
    for label in ax3.xaxis.get_ticklabels():
        label.set_rotation(45)
    plt.suptitle(stock.upper(), color='w')
    plt.setp(ax0.get_xticklabels(), visible=False)
    plt.setp(ax1.get_xticklabels(), visible=False)
    plt.setp(ax2.get_xticklabels(), visible=False)
    plt.setp(ax4.get_xticklabels(), visible=False)

    ### Annotate Signal
    if inSignal:
        ax1.annotate('In', xy=(1.02, .7), xycoords='axes fraction',
        xytext=(1.02, .3), textcoords='axes fraction',
        arrowprops=dict(facecolor='green', shrink=0.05, width=8, headwidth=15),
        fontsize=14, color='green', horizontalalignment='center', verticalalignment='bottom')

    if outSignal:
        ax1.annotate('Out', xy=(1.02, .3), xycoords='axes fraction', xytext=(1.02, .7), textcoords='axes fraction',
        arrowprops=dict(facecolor='red', shrink=0.05, width=8, headwidth=15), fontsize=14, color='red', horizontalalignment='center', verticalalignment='bottom')

    ### Save Picture
    #plt.subplots_adjust(left=.09, bottom=.14, right=.94, top=.95, wspace=.20, hspace=0)
    #plt.show(block=False)
    #fig.savefig('Images/example2.png', facecolor=fig.get_facecolor())

    return


### VARIABLES FROM FILE
### Current Price Data
def currentPull():
    currentVar = []
    currentVar = loadtxt('Zephyr Limit 1.4/Current.txt', dtype=str)
    return currentVar


### Config Settings
def configPull():
    configPullVar = []
    configPullVar = loadtxt('Zephyr Limit 1.4/Config.txt', dtype=int)
    #macdShort, macdLong, macdSignal, kPeriod, dPeriod, sLimitHigh, sLimitLow, MA1, MA2, rsiPeriod, rLimitHigh, rLimitLow, mfiPeriod, mLimitHigh, mLimitLow, B, S
    #configPullVar = [10, 30, 10, 10, 3, 80, 20, 7, 15, 15, 65, 35, 14, 70, 30, 1, 1]
    return configPullVar


### Symbol List
def listPull():
    listPullVar = []
    listPullVar = loadtxt('Zephyr Limit 1.4/List.txt', dtype=str)
    return np.atleast_1d(listPullVar)


### MENU FUNCTIONS
### Edit MACD
def setMACD():
    configVar = configPull()

    macdShort = configVar[0]
    macdLong = configVar[1]
    macdSignal = configVar[2]

    MACD = Tk.Tk()
    MACD.geometry('215x185+800+100')

    ### Title Bar
    MACD.title('Zephyr')
    MACD.iconbitmap('Zephyr Limit 1.4/Images/Favicon.ico')

    ### Text Box
    macdShortVal = Tk.IntVar(MACD, macdShort)
    macdShortLabelVal = Tk.StringVar(MACD, 'MACD Short')
    macdShortLabel = Tk.Label(MACD, textvariable=macdShortLabelVal)
    macdShortLabel.pack()
    macdShortTB = Tk.Entry(MACD, textvariable=macdShortVal, justify=Tk.CENTER)
    macdShortTB.pack()

    macdLongVal = Tk.IntVar(MACD, macdLong)
    macdLongLabelVal = Tk.StringVar(MACD, 'MACD Long')
    macdLongLabel = Tk.Label(MACD, textvariable=macdLongLabelVal)
    macdLongLabel.pack()
    macdLongTB = Tk.Entry(MACD, textvariable=macdLongVal, justify=Tk.CENTER)
    macdLongTB.pack()

    macdSignalVal = Tk.IntVar(MACD, macdSignal)
    macdSignalLabelVal = Tk.StringVar(MACD, 'MACD Signal')
    macdSignalLabel = Tk.Label(MACD, textvariable=macdSignalLabelVal)
    macdSignalLabel.pack()
    macdSignalTB = Tk.Entry(MACD, textvariable=macdSignalVal, justify=Tk.CENTER)
    macdSignalTB.pack()

    macdSaveB = Tk.Button(MACD, text='Save', command=lambda: macdSaveButton(macdShortVal, macdLongVal, macdSignalVal, configVar))
    macdSaveB.pack()


def macdSaveButton(macdShortVal, macdLongVal, macdSignalVal, configVar):
    configVar[0] = macdShortVal.get()
    configVar[1] = macdLongVal.get()
    configVar[2] = macdSignalVal.get()
    np.savetxt('Config.txt', configVar, '%-1.1u')


### Edit Stochastic
def setStoch():
    configVar = configPull()

    kPeriod = configVar[3]
    dPeriod = configVar[4]
    sLimitHigh = configVar[5]
    sLimitLow = configVar[6]

    STOCH = Tk.Tk()
    STOCH.geometry('215x235+800+100')

    ### Title Bar
    STOCH.title('Zephyr')
    STOCH.iconbitmap('Zephyr Limit 1.4/Images/Favicon.ico')

    ### Text Box
    kPeriodVal = Tk.IntVar(STOCH, kPeriod)
    kPeriodLabelVal = Tk.StringVar(STOCH, 'Stochastic K Period')
    kPeriodLabel = Tk.Label(STOCH, textvariable=kPeriodLabelVal)
    kPeriodLabel.pack()
    kPeriodTB = Tk.Entry(STOCH, textvariable=kPeriodVal, justify=Tk.CENTER)
    kPeriodTB.pack()

    dPeriodVal = Tk.IntVar(STOCH, dPeriod)
    dPeriodLabelVal = Tk.StringVar(STOCH, 'Stochastic D Period')
    dPeriodLabel = Tk.Label(STOCH, textvariable=dPeriodLabelVal)
    dPeriodLabel.pack()
    dPeriodTB = Tk.Entry(STOCH, textvariable=dPeriodVal, justify=Tk.CENTER)
    dPeriodTB.pack()

    sLimitHighVal = Tk.IntVar(STOCH, sLimitHigh)
    sLimitHighLabelVal = Tk.StringVar(STOCH, 'Upper Limit')
    sLimitHighLabel = Tk.Label(STOCH, textvariable=sLimitHighLabelVal)
    sLimitHighLabel.pack()
    sLimitHighTB = Tk.Entry(STOCH, textvariable=sLimitHighVal, justify=Tk.CENTER)
    sLimitHighTB.pack()

    sLimitLowVal = Tk.IntVar(STOCH, sLimitLow)
    sLimitLowLabelVal = Tk.StringVar(STOCH, 'Lower Limit')
    sLimitLowLabel = Tk.Label(STOCH, textvariable=sLimitLowLabelVal)
    sLimitLowLabel.pack()
    sLimitLowTB = Tk.Entry(STOCH, textvariable=sLimitLowVal, justify=Tk.CENTER)
    sLimitLowTB.pack()

    stochSaveB = Tk.Button(STOCH, text='Save', command=lambda: stochSaveButton(kPeriodVal, dPeriodVal, sLimitHighVal, sLimitLowVal, configVar))
    stochSaveB.pack()


def stochSaveButton(kPeriodVal, dPeriodVal, sLimitHighVal, sLimitLowVal, configVar):
    configVar[3] = kPeriodVal.get()
    configVar[4] = dPeriodVal.get()
    configVar[5] = sLimitHighVal.get()
    configVar[6] = sLimitLowVal.get()
    np.savetxt('Config.txt', configVar, '%-1.1u')


### Edit MAs
def setMAs():
    configVar = configPull()

    MA1 = configVar[7]
    MA2 = configVar[8]

    MAs = Tk.Tk()
    MAs.geometry('215x165+800+100')

    ### Title Bar
    MAs.title('Zephyr')
    MAs.iconbitmap('Zephyr Limit 1.4/Images/Favicon.ico')

    ### Text Box
    MA1Val = Tk.IntVar(MAs, MA1)
    MA1LabelVal = Tk.StringVar(MAs, 'Short MA Period')
    MA1Label = Tk.Label(MAs, textvariable=MA1LabelVal)
    MA1Label.pack()
    MA1TB = Tk.Entry(MAs, textvariable=MA1Val, justify=Tk.CENTER)
    MA1TB.pack()

    MA2Val = Tk.IntVar(MAs, MA2)
    MA2LabelVal = Tk.StringVar(MAs, 'Long MA Period')
    MA2Label = Tk.Label(MAs, textvariable=MA2LabelVal)
    MA2Label.pack()
    MA2TB = Tk.Entry(MAs, textvariable=MA2Val, justify=Tk.CENTER)
    MA2TB.pack()

    MAsSaveB = Tk.Button(MAs, text='Save', command=lambda: maSaveButton(MA1Val, MA2Val, configVar))
    MAsSaveB.pack()


def maSaveButton(MA1Val, MA2Val, configVar):
    configVar[7] = MA1Val.get()
    configVar[8] = MA2Val.get()
    np.savetxt('Config.txt', configVar, '%-1.1u')


### Edit RSI
def setRSI():
    configVar = configPull()

    rsiPeriod = configVar[9]
    rLimitHigh = configVar[10]
    rLimitLow = configVar[11]

    RSI = Tk.Tk()
    RSI.geometry('215x185+800+100')

    ### Title Bar
    RSI.title('Zephyr')
    RSI.iconbitmap('Zephyr Limit 1.4/Images/Favicon.ico')

    ### Text Box
    rsiPeriodVal = Tk.IntVar(RSI, rsiPeriod)
    rsiPeriodLabelVal = Tk.StringVar(RSI, 'RSI Period')
    rsiPeriodLabel = Tk.Label(RSI, textvariable=rsiPeriodLabelVal)
    rsiPeriodLabel.pack()
    rsiPeriodTB = Tk.Entry(RSI, textvariable=rsiPeriodVal, justify=Tk.CENTER)
    rsiPeriodTB.pack()

    rLimitHighVal = Tk.IntVar(RSI, rLimitHigh)
    rLimitHighLabelVal = Tk.StringVar(RSI, 'Upper Limit')
    rLimitHighLabel = Tk.Label(RSI, textvariable=rLimitHighLabelVal)
    rLimitHighLabel.pack()
    rLimitHighTB = Tk.Entry(RSI, textvariable=rLimitHighVal, justify=Tk.CENTER)
    rLimitHighTB.pack()

    rLimitLowVal = Tk.IntVar(RSI, rLimitLow)
    rLimitLowLabelVal = Tk.StringVar(RSI, 'Lower Limit')
    rLimitLowLabel = Tk.Label(RSI, textvariable=rLimitLowLabelVal)
    rLimitLowLabel.pack()
    rLimitLowTB = Tk.Entry(RSI, textvariable=rLimitLowVal, justify=Tk.CENTER)
    rLimitLowTB.pack()

    rsiSaveB = Tk.Button(RSI, text='Save', command=lambda: rsiSaveButton(rsiPeriodVal, rLimitHighVal, rLimitLowVal, configVar))
    rsiSaveB.pack()


def rsiSaveButton(rsiPeriodVal, rLimitHighVal, rLimitLowVal, configVar):
    configVar[9] = rsiPeriodVal.get()
    configVar[10] = rLimitHighVal.get()
    configVar[11] = rLimitLowVal.get()
    np.savetxt('Config.txt', configVar, '%-1.1u')


### Edit MFI
def setMFI():
    configVar = configPull()

    mfiPeriod = configVar[12]
    mLimitHigh = configVar[13]
    mLimitLow = configVar[14]

    MFI = Tk.Tk()
    MFI.geometry('215x185+800+100')

    ### Title Bar
    MFI.title('Zephyr')
    MFI.iconbitmap('Zephyr Limit 1.4/Images/Favicon.ico')

    ### Text Box
    mfiPeriodVal = Tk.IntVar(MFI, mfiPeriod)
    mfiPeriodLabelVal = Tk.StringVar(MFI, 'MFI Period')
    mfiPeriodLabel = Tk.Label(MFI, textvariable=mfiPeriodLabelVal)
    mfiPeriodLabel.pack()
    mfiPeriodTB = Tk.Entry(MFI, textvariable=mfiPeriodVal, justify=Tk.CENTER)
    mfiPeriodTB.pack()

    mLimitHighVal = Tk.IntVar(MFI, mLimitHigh)
    mLimitHighLabelVal = Tk.StringVar(MFI, 'Upper Limit')
    mLimitHighLabel = Tk.Label(MFI, textvariable=mLimitHighLabelVal)
    mLimitHighLabel.pack()
    mLimitHighTB = Tk.Entry(MFI, textvariable=mLimitHighVal, justify=Tk.CENTER)
    mLimitHighTB.pack()

    mLimitLowVal = Tk.IntVar(MFI, mLimitLow)
    mLimitLowLabelVal = Tk.StringVar(MFI, 'Lower Limit')
    mLimitLowLabel = Tk.Label(MFI, textvariable=mLimitLowLabelVal)
    mLimitLowLabel.pack()
    mLimitLowTB = Tk.Entry(MFI, textvariable=mLimitLowVal, justify=Tk.CENTER)
    mLimitLowTB.pack()

    mfiSaveB = Tk.Button(MFI, text='Save', command=lambda: mfiSaveButton(mfiPeriodVal, mLimitHighVal, mLimitLowVal, configVar))
    mfiSaveB.pack()


def mfiSaveButton(mfiPeriodVal, mLimitHighVal, mLimitLowVal, configVar):
    configVar[12] = mfiPeriodVal.get()
    configVar[13] = mLimitHighVal.get()
    configVar[14] = mLimitLowVal.get()
    np.savetxt('Config.txt', configVar, '%-1.1u')


### Edit Minimum Indicator Variables
def setLSS():
    configVar = configPull()

    L = configVar[15]
    S = configVar[16]

    LSS = Tk.Tk()
    LSS.geometry('215x185+800+100')

    ### Title Bar
    LSS.title('Zephyr')
    LSS.iconbitmap('Zephyr Limit 1.4/Images/Favicon.ico')

    ### Text Box
    LVal = Tk.IntVar(LSS, L)
    LLabelVal = Tk.StringVar(LSS, 'LS (1-4)')
    LLabel = Tk.Label(LSS, textvariable=LLabelVal)
    LLabel.pack(pady=10)
    LTB = Tk.Entry(LSS, textvariable=LVal, justify=Tk.CENTER)
    LTB.pack()

    SVal = Tk.IntVar(LSS, S)
    SLabelVal = Tk.StringVar(LSS, 'SS (1-4)')
    SLabel = Tk.Label(LSS, textvariable=SLabelVal)
    SLabel.pack()
    STB = Tk.Entry(LSS, textvariable=SVal, justify=Tk.CENTER)
    STB.pack()

    lssSaveB = Tk.Button(LSS, text='Save', command=lambda: LSSSaveButton(LVal, SVal, configVar))
    lssSaveB.pack()


def LSSSaveButton(LVal, SVal, configVar):
    configVar[15] = LVal.get()
    configVar[16] = SVal.get()
    np.savetxt('Config.txt', configVar, '%-1.1u')


### Edit Symbol List
def setSymbolList():
    SL = Tk.Tk()
    SL.geometry('215x115+800+100')

    ### Title Bar
    SL.title('Zephyr')
    SL.iconbitmap('Zephyr Limit 1.4/Images/Favicon.ico')

    ### Make Variable
    openFile = open('Zephyr Limit 1.4/List.txt')
    listVar = ''
    for i in openFile:
        listVar += i
    ### Text Box
    listBox = Tk.Text(SL)
    listBox.config(height=5, width=20)
    listBox.insert(Tk.END, listVar)
    listBox.pack()
    openFile.close()

    symbolListSaveB = Tk.Button(SL, text='Save', command=lambda: symbolListSaveButton(listBox))
    symbolListSaveB.pack()


def symbolListSaveButton(listBox):
    newList = listBox.get(1.0, Tk.END)
    outToFile = open('Zephyr Limit 1.4/List.txt', 'w')
    outToFile.write(newList)
    outToFile.close()


### Edit Current Data ***
def setCurrentData():
    CD = Tk.Tk()
    CD.geometry('215x115+800+100')

    ### Title Bar
    CD.title('Zephyr')
    CD.iconbitmap('Zephyr Limit 1.4/Images/Favicon.ico')

    ### Text Box
    currentDataVar = Tk.StringVar(CD, 'date,close,high,low,open,volume')
    currentBox = Tk.Entry(CD, textvariable=currentDataVar, justify=Tk.CENTER)
    currentBox.pack()

    currentDataSaveB = Tk.Button(CD, text='Save', command=lambda: currentDataSaveButton(currentBox))
    currentDataSaveB.pack()


def currentDataSaveButton(currentBox):
    currentData = currentBox.get()
    np.savetxt('Current.txt', currentData)
    global currentDataTF
    currentDataTF = True
    return