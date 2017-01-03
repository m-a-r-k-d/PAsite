#!/usr/bin/python3.5
# -*- coding: utf-8 -*-
"""
Created on Sat Sep  3 15:31:52 2016

@author: Mark D

This program gets the data table from the AMPS website for the MCM 5 day
forecast. It plots the data using timestamps. Once the data is plotted the
timestamps are converted to New Zealand time.

The method used to convert the timestamps to a date in the NZ timezone uses
the function Date_fmt and matplotlib's ticker.FuncFormatter. I could not
get the DateFormatter method to work. Al times were in UTC even if I set the
timezone.
"""

import pandas as pd
from matplotlib import pyplot as plt
import matplotlib as mpl
import numpy as np
import datetime as dati
import pytz
from pytz import timezone #This is for convenience

pi = np.pi

#This is the function used to convert the x-axis timestamps to NZ timezone
def Date_fmt(dt,x=None):
    return dati.datetime.fromtimestamp(\
        dt, tz = timezone('Pacific/Auckland')).strftime('%Y-%m-%d %H:%M')

#This function converts Altimeter setting to pressure using the formula from
#NOAA (http://www.srh.noaa.gov/images/epz/wxcalc/stationPressure.pdf). It
#takes height in meters, and altimeter setting in inHg. I convert that to
#mbar using that factor of 33.8639.
def P(height, altim):
    return 33.8639*altim*((288-height*0.0065)/288)**(5.2561)

def tbl_plot(path,file,today):
    '''Function used to plot the McM wx table scraped off AMPS site.'''

    #print('pandas version: ', pd.__version__)
    wx = pd.read_csv(path+file, sep = '\s+',\
    skiprows = 3, engine = 'python', skipfooter = 7,\
    header = 0)
    print()

    wx = wx.iloc[1:,:]

    wx = wx.rename(columns = {'FCST': 'FCST HR'})

    wx['FCST HR'] = wx['FCST HR'].astype(float)
    wx['T'] = wx['T'].astype(float)
#The dewpoint temp from the table is frequently above the predicted
#air temp. This is not the case for the 'regular' 5 day forecast, and
#I also don't believe that they get dew that frequently at McM. I'm
#not going to plot this.
#    wx['Td'] = wx['Td'].astype(float)
    wx['Spd'] = wx['Spd'].astype(float)
    wx['Dir'] = wx['Dir'].astype(float)
    wx['Gust'] = wx['Gust'].astype(float)
    wx['Altim'] = wx['Altim'].astype(float)

    #Here is my solution to plotting the graphs in NZ time (i.e. tz =
    #'Pacific/Auckland'). I will take the time in UTC and convert to timestamp
    #using the datetime.timestamp() function. The resulting plot will have an
    #x-axis with time since 1-1-1970 00:00
    #
    #Create a function that will convert the timestamp to a datetime with the
    #New Zealand timezone. The function just uses datetime.fromtimestamp() -
    #fromtimestamp alows you to speify the timezone. You
    #then use that function in matplotlib's ticker.FuncFormatter() to give the
    #correct format to the x-axis dates. This works.
    #
    #I tried using matplotlib's DateFormatter, but, although you can enter the
    #timezone, the result is always in UTC. Is this another bug in handling
    #timezones?

    #Used the next 2 lines during testing
    #today = '2016-09-03'
    #today_utc = dati.datetime.strptime(today, '%Y-%m-%d')

    today_utc = dati.datetime.strptime(today, '%Y%m%d')
    today_utc = today_utc.replace(tzinfo = pytz.utc) #only use replace with utc!!
    today_tstamp = today_utc.timestamp()

    #Make a list of timestamps each element is today's timestamp. This will
    #be used with the forecast hour from the AMPS table to create the list
    #of timestamps for the plot.
    tstamp_x = [today_tstamp]*41
    for i, stamp in enumerate(tstamp_x):
        tstamp_x[i] = today_tstamp + wx['FCST HR'].iloc[i]*3600


    #Calculate the vector components of the wind velocity
    U = -wx['Spd']*np.sin(wx['Dir']*pi/180)
    V = -wx['Spd']*np.cos(wx['Dir']*pi/180)

    #Set up the fig using subplots. The top graph is for wind the bottom is for T
    fig, (ax1, ax2) = plt.subplots(2, 1, sharex = True)
    ax2_P = ax2.twinx()

    ax1.plot(tstamp_x, wx['Spd'])

    #Read the y limits from the wind speed plot to find where to put the
    #wind barbs on the Y-axis.
    y_rng = ax1.get_ylim()[1] - ax1.get_ylim()[0]
    Y = np.ones(41)*0.75*y_rng

    #Plot the barbs
    ax1.barbs(tstamp_x, Y, U, V, fill_empty = True, length = 6,\
    rounding = True, flip_barb = True)

    ax2.plot(tstamp_x, wx['T'])
    ax2_P.plot(tstamp_x, P(2835, wx['Altim']), 'r')

    x_fmt = mpl.ticker.FuncFormatter(Date_fmt)
    ax1.get_xaxis().set_major_formatter(x_fmt)

    ax1.set_xlim(left=tstamp_x[0], right=tstamp_x[-1])
    xtick_arr = np.arange(tstamp_x[0], tstamp_x[-1]+12*3600, 24*3600)
    ax1.set_xticks(xtick_arr)
    ax1.set_ylabel('Wind Sp (kn)')
    ax2.set_ylabel('Temp (C)')
    ax2.legend('T', loc = 'lower left')
    ax2_P.set_ylabel('P (mbar)')
    ax2_P.legend('P', loc = 'lower right')
    ax1.grid(True, axis = 'x')
    ax2.grid(True, axis = 'x')
    ax1.set(title = 'South Pole Forecast %s' % today)

    fig.autofmt_xdate() #All this is doing is rotating the tick lables
    fig.set_size_inches(8,6)
    fig.tight_layout()

    fig.savefig(path+'spl_tbl_plot.png')

if __name__=='main':
    print('main!')
#    path = '/home/markd/www/static/images/'
    path = 'C:\\Users\\owner\\Documents\\website\\PAsite20170102\\static\\images\\'
    file = '10km.spl.table.txt'
    today = dati.datetime.utcnow().strftime('%Y%m%d')

    tbl_plot(path, file, today)

