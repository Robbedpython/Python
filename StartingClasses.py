# -*- coding: utf-8 -*-
import numpy as np
import time
import datetime
from numpy import loadtxt
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import matplotlib.dates as mdates
import matplotlib
import pandas as pd
import pylab
import tkinter as Tk
import yfinance as yf
matplotlib.rcParams.update({'font.size': 9})

class stockData:

    def __init__(self, symbol):
        data = yf.download(symbol, start="2020-01-01", end="2021-01-01")

        #self.date = [mdates.date2num(d) for d in data.index.to_datetime()]
        self.date = data.index
        self.closep = data["Close"].values.flatten()
        self.highp = data["High"].values.flatten()
        self.lowp = data["Low"].values.flatten()
        self.openp = data["Open"].values.flatten()
        self.volume = data["Volume"].values.flatten()

    ### INDICATORS
    ### Calculate RSI
    def rsi(self, rsiPeriod):
        deltas = np.diff(self.closep)
        seed = deltas[:rsiPeriod + 1]
        up = seed[seed >= 0].sum() / rsiPeriod
        down = -seed[seed < 0].sum() / rsiPeriod
        rs = up / down
        rsi = np.zeros_like(self.closep)
        rsi[:rsiPeriod] = 100. - 100. / (1. + rs)
        for i in range(rsiPeriod, len(self.closep)):
            delta = deltas[i - 1]
            if delta > 0:
                upval = delta
                downval = 0.
            else:
                upval = 0.
                downval = -delta
            up = (up * (rsiPeriod - 1) + upval) / rsiPeriod
            down = (down * (rsiPeriod - 1) + downval) / rsiPeriod
            rs = up / down
            rsi[i] = 100. - 100. / (1. + rs)
        return rsi

    ### Calculate MFI
    def mfi(self, mfiPeriod):
        data = [self.closep, self.highp, self.lowp]
        moneyFlow = np.average(data) * self.volume
        deltas = np.diff(moneyFlow)
        mfi = np.zeros_like(moneyFlow)
        for i in range(mfiPeriod, len(moneyFlow)):
            seed = deltas[i - mfiPeriod:i - 1]
            up = seed[seed >= 0].sum()
            down = -seed[seed < 0].sum()
            mfr = up / down
            mfi[i] = 100. - 100. / (1. + mfr)
        return mfi

    ### Calculate MA
    def movingAverage(self, values, window):
        weigths = np.repeat(1.0, window) / window
        smas = np.convolve(values, weigths, 'valid')
        return smas

    ### Calculate EMA
    def expMovingAverage(self, values, window):
        weights = np.exp(np.linspace(-1., 0., window))
        weights /= weights.sum()
        a = np.convolve(values, weights, mode='full')[:len(values)]
        a[:window] = a[window]
        return a

    ### Calculate MACD
    def macd(self, macdLong, macdShort, nema):
        close = self.closep
        emaslow = self.expMovingAverage(close, macdLong)
        emafast = self.expMovingAverage(close, macdShort)
        macd = emafast - emaslow
        ema9 = self.expMovingAverage(macd, nema)
        return emaslow, emafast, macd, ema9

    ### Calculate Stochastic
    def stochastic(self, kPeriod):
        lows = np.array(self.lowp)
        highs = np.array(self.highp)
        close = np.array(self.closep)
        k = np.zeros_like(lows)
        for i in range(kPeriod, len(self.lowp)):
            low = lows[i - kPeriod:i]
            high = highs[i - kPeriod:i]
            lowest = min(low)
            highest = max(high)
            price = close[i - 1]
            k[i] = 100. * (price - lowest) / (highest - lowest)
        return k