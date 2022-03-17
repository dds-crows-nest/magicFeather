# ---------------------------ooo0ooo---------------------------
# import required modules
import numpy as np
import time
import array
import multiprocessing

from array import array
from datetime import datetime
from datetime import timedelta

from scipy import signal

from obspy.imaging.spectrogram import spectrogram
from obspy.signal.filter import bandpass, lowpass, highpass
from obspy.imaging.cm import obspy_sequential
from obspy.signal.tf_misfit import cwt
from obspy import UTCDateTime, read, Trace, Stream
from obspy.signal.trigger import plot_trigger, z_detect
from obspy.io.xseed import Parser
from obspy.signal import PPSD

import time
import ftplib
import string

import matplotlib

# matplotlib.use('Agg') #prevent use of Xwindows
from matplotlib import pyplot as plt
import matplotlib.gridspec as gridspec
from matplotlib.ticker import MultipleLocator, FormatStrFormatter

import matplotlib.dates as mdates
import statistics  # used by median filter
import os
import gc

from tkinter import filedialog
# from tkinter import * #for file opening dialog
import tkinter as tk


# ---------------------------ooo0ooo---------------------------
# ---------------------------ooo0ooo---------------------------

def plotFiltered(Data, samplingFreq, startDT):
    N = len(Data)
    mean_removed = np.ones_like(Data) * np.mean(Data)
    # Data0 = Data - mean_removed
    Data0 = Data

    lowCut1 = 0.001
    highCut1 = 2.0
    Data1 = butter_bandpass_filter(Data0, lowCut1, highCut1, samplingFreq, order=3)
    # legend1=

    lowCut2 = 2.0
    highCut2 = 5.0
    Data2 = butter_bandpass_filter(Data0, lowCut2, highCut2, samplingFreq, order=3)

    lowCut3 = 05.0
    highCut3 = 10.0
    Data3 = butter_bandpass_filter(Data0, lowCut3, highCut3, samplingFreq, order=3)

    xN = np.linspace(1, (N / samplingFreq), N)
    x = np.divide(xN, 60)
    TitleString = ('A: Raw  B:' + str(lowCut1) + '-' + str(highCut1) + ' Hz  C:' + str(lowCut2) + '-' + str(
        highCut2) + ' Hz  D:' + str(lowCut3) + '-' + str(highCut3) + ' Hz')

    fig = plt.figure()
    fig.canvas.set_window_title('start U.T.C. - ' + startDT)

    plt.subplots_adjust(hspace=0.001)
    gs = gridspec.GridSpec(4, 1)

    ax0 = plt.subplot(gs[0])
    ax0.plot(x, Data0, label='unfiltered')

    ax1 = plt.subplot(gs[1], sharex=ax0)
    ax1.plot(x, Data1, label=(str(lowCut1) + '-' + str(highCut1) + 'Hz'))

    ax2 = plt.subplot(gs[2], sharex=ax0)
    ax2.plot(x, Data2, label='unfiltered')

    ax3 = plt.subplot(gs[3], sharex=ax0)
    ax3.plot(x, Data3, label='unfiltered')

    xticklabels = ax0.get_xticklabels() + ax1.get_xticklabels() + ax2.get_xticklabels()
    plt.setp(xticklabels, visible=False)

    fig.tight_layout()
    fig.show()

    # plt.show()
    # ---------------------------ooo0ooo---------------------------


def plotBands(tr):
    print('Filtering and plotting bands')

    legendLoc = 'upper left'
    xMin = 0.0
    xMax = 24.0

    N = len(tr.data)

    samplingFreq = tr.stats.sampling_rate

    yscale = 5.0

    lowCut1 = 0.01
    highCut1 = 0.5
    tr1 = tr.copy()
    tr1.filter('bandpass', freqmin=lowCut1, freqmax=highCut1, corners=4, zerophase=True)

    lowCut2 = 0.5
    highCut2 = 1.0
    tr2 = tr.copy()
    tr2.filter('bandpass', freqmin=lowCut2, freqmax=highCut2, corners=4, zerophase=True)

    lowCut3 = 1.0
    highCut3 = 2.0
    tr3 = tr.copy()
    tr3.filter('bandpass', freqmin=lowCut3, freqmax=highCut3, corners=4, zerophase=True)

    lowCut4 = 2.0
    highCut4 = 3.0
    tr4 = tr.copy()
    tr4.filter('bandpass', freqmin=lowCut4, freqmax=highCut4, corners=4, zerophase=True)

    lowCut5 = 3.0
    highCut5 = 5.0
    tr5 = tr.copy()
    tr5.filter('bandpass', freqmin=lowCut5, freqmax=highCut5, corners=5, zerophase=True)

    lowCut6 = 5.0
    highCut6 = 10.0
    tr6 = tr.copy()
    tr6.filter('bandpass', freqmin=lowCut6, freqmax=highCut6, corners=4, zerophase=True)

    lowCut7 = 10.0
    highCut7 = 15.0
    tr7 = tr.copy()
    tr7.filter('bandpass', freqmin=lowCut7, freqmax=highCut7, corners=4, zerophase=True)

    x = np.linspace(1, (N / tr.stats.sampling_rate), N)
    x = np.divide(x, 3600)

    fig = plt.figure()
    fig.suptitle(str(tr.stats.starttime) + ' Filtered ')
    fig.canvas.set_window_title('start U.T.C. - ' + str(tr.stats.starttime))

    plt.subplots_adjust(hspace=0.001)
    gs = gridspec.GridSpec(8, 1)

    ax0 = plt.subplot(gs[0])
    ax0.plot(x, tr)
    ax0.set_xlim(xMin, xMax)
    ax0.legend(['raw data'], loc=legendLoc, fontsize=10)

    ax1 = plt.subplot(gs[1], sharex=ax0)
    ax1.plot(x, tr1)
    ax1.legend([str(lowCut1) + '-' + str(highCut1) + 'Hz'], loc=legendLoc, fontsize=10)

    ax2 = plt.subplot(gs[2], sharex=ax1)
    ax2.plot(x, tr2)
    ax2.legend([str(lowCut2) + '-' + str(highCut2) + 'Hz'], loc=legendLoc, fontsize=10)

    ax3 = plt.subplot(gs[3], sharex=ax1)
    ax3.plot(x, tr3)
    ax3.legend([str(lowCut3) + '-' + str(highCut3) + 'Hz'], loc=legendLoc, fontsize=10)

    ax4 = plt.subplot(gs[4], sharex=ax1)
    ax4.plot(x, tr4)
    ax4.legend([str(lowCut4) + '-' + str(highCut4) + 'Hz'], loc=legendLoc, fontsize=10)

    ax5 = plt.subplot(gs[5], sharex=ax1)
    ax5.plot(x, tr5)
    ax5.legend([str(lowCut5) + '-' + str(highCut5) + 'Hz'], loc=legendLoc, fontsize=10)

    ax6 = plt.subplot(gs[6], sharex=ax1)
    ax6.plot(x, tr6)
    ax6.legend([str(lowCut6) + '-' + str(highCut6) + 'Hz'], loc=legendLoc, fontsize=10)

    ax7 = plt.subplot(gs[7], sharex=ax1)
    ax7.plot(x, tr7)
    ax7.legend([str(lowCut7) + '-' + str(highCut7) + 'Hz'], loc=legendLoc, fontsize=10)

    xticklabels = ax0.get_xticklabels() + ax1.get_xticklabels() + ax2.get_xticklabels() + ax3.get_xticklabels() \
                  + ax4.get_xticklabels() + ax5.get_xticklabels() + ax6.get_xticklabels()

    plt.setp(xticklabels, visible=False)

    ax7.set_xlabel(r'$\Delta$t - hr', fontsize=12)

    fig.tight_layout()
    fig.show()

    # ---------------------------ooo0ooo---------------------------


def plotMultiple(tr1, tr2, tr3, tr4, yMin, yMax, lowCut, highCut):
    N1 = len(tr1.data)
    N2 = len(tr2.data)
    N3 = len(tr3.data)
    N4 = len(tr4.data)

    samplingFreq = (
                               tr1.stats.sampling_rate + tr2.stats.sampling_rate + tr3.stats.sampling_rate + tr4.stats.sampling_rate) / 4.0

    x1 = np.linspace(1, (N1 / samplingFreq), N1)
    x1 = np.divide(x1, 3600)

    x2 = np.linspace(1, (N2 / samplingFreq), N2)
    x2 = np.divide(x2, 3600)

    x3 = np.linspace(1, (N3 / samplingFreq), N3)
    x3 = np.divide(x3, 3600)

    x4 = np.linspace(1, (N4 / samplingFreq), N4)
    x4 = np.divide(x4, 3600)

    TitleString = str(lowCut) + '-' + str(highCut) + ' Hz'
    fig = plt.figure(figsize=(14, 9))
    fig.canvas.set_window_title(TitleString)
    fig.suptitle('Filtered ' + str(lowCut) + '--' + str(highCut) + 'Hz')

    plt.subplots_adjust(hspace=0.001)
    gs = gridspec.GridSpec(4, 1)

    ax1 = plt.subplot(gs[0])
    ax1.plot(x1, tr1, color='k')
    ax1.set_xlim([0, 24])
    ax1.set_ylim([yMin, yMax])
    ax1.legend([str(tr1.stats.starttime.date)], loc='upper right', fontsize=12)

    ax2 = plt.subplot(gs[1])
    ax2.plot(x2, tr2, color='k')
    ax2.set_xlim([0, 24])
    ax2.set_ylim([yMin, yMax])
    ax2.legend([str(tr2.stats.starttime.date)], loc='upper right', fontsize=12)
    ax2.axvline(x=7.4, color='r')

    ax3 = plt.subplot(gs[2])
    ax3.plot(x3, tr3, color='k')
    ax3.set_xlim([0, 24])
    ax3.set_ylim([yMin, yMax])
    ax3.legend([str(tr3.stats.starttime.date)], loc='upper right', fontsize=12)
    ax3.axvline(x=17, color='b')

    ax4 = plt.subplot(gs[3], sharex=ax1)
    ax4.plot(x4, tr4, color='k')
    ax4.set_xlim([0, 24])
    ax4.set_ylim([yMin, yMax])
    ax4.legend([str(tr4.stats.starttime.date)], loc='upper right', fontsize=12)
    ax4.set_xlabel(r'$\Delta$t - hr', fontsize=12)

    fig.tight_layout()
    fig.show()


# ---------------------------ooo0ooo---------------------------
def butter_bandpass(lowcut, highCut, samplingFreq, order=5):
    nyq = 0.5 * samplingFreq
    low = lowcut / nyq
    high = highCut / nyq
    b, a = butter(order, [low, high], btype='band')
    return b, a


# ---------------------------ooo0ooo---------------------------

def butter_bandpass_filter(data, lowcut, highCut, samplingFreq, order=5):
    b, a = butter_bandpass(lowcut, highCut, samplingFreq, order=order)
    y = lfilter(b, a, data)
    return y


# ---------------------------ooo0ooo---------------------------

def plotPeriodogram(tr, fMin, fMax):
    print('plotting Welch Periodogram....')
    Data = tr.data
    samplingFreq = tr.stats.sampling_rate

    N = len(Data)  # Number of samplepoints
    xN = np.linspace(1, (N / samplingFreq), N)
    # xN = np.divide(xN, 60)
    t1 = np.divide(xN, (samplingFreq * 60))

    x0 = int(startT * samplingFreq)
    x1 = int(endT * samplingFreq)
    if (x0 < 0):
        x0 = 0
    if (x1 > N):
        x1 = N - 1
    subSetLen = x1 - x0

    WINDOW_LEN = int((subSetLen / samplingFreq) * 1)
    OVERLAP_LEN = WINDOW_LEN / 8

    topX = np.linspace((x0 / samplingFreq) + 1, (x1 / samplingFreq), subSetLen)

    f, Pxx = signal.welch(Data[x0:x1], samplingFreq, scaling='spectrum')
    Pxx = np.divide(Pxx, 60)

    fig = plt.figure(figsize=(8, 8))
    gs = gridspec.GridSpec(2, 1, height_ratios=[1, 1])

    ax0 = plt.subplot(gs[0])
    ax0.plot(f, Pxx)
    ax0.set_xlim([0.1, fMax])
    ax0.set_xlabel(r'f - Hz', fontsize=14)

    ax1 = plt.subplot(gs[1])
    # ax1.plot(f, Pxx)
    ax1.semilogy(f, Pxx)
    # ax1.set_xlim([0.01,fMax])
    ax1.set_xlabel(r'f - Hz', fontsize=14)
    ax1.set_ylabel(r't - s', fontsize=14)

    xticklabels = ax0.get_xticklabels()
    plt.setp(xticklabels, visible=False)

    fig.tight_layout()
    fig.show()

# ---------------------------ooo0ooo---------------------------
def plotSpectrogram(tr, lowCut, highCut):
    print('plotting Spectrogram....')


    tr2.spectrogram(log=True)

    samplingFreq = tr.stats.sampling_rate

    N = len(Data)  # Number of samplepoints
    xN = np.linspace(1, (N / samplingFreq), N)
    # xN = np.divide(xN, 60)
    t1 = np.divide(xN, (samplingFreq * 60))

    fig = plt.figure()
    fig.canvas.set_window_title('FFT Spectrum ' + str(tr1.stats.starttime.date))

    ax1 = fig.add_axes([0.1, 0.75, 0.7, 0.2])  # [left bottom width height]
    ax2 = fig.add_axes([0.1, 0.1, 0.7, 0.60], sharex=ax1)
    ax3 = fig.add_axes([0.83, 0.1, 0.03, 0.6])
    # ax2.set_ylim([1.0,3.0])

    #  t = np.arange(spl1[0].stats.N) / spl1[0].stats.sampling_rate
    ax1.plot(xN, Data, 'k')

    # ax,spec = spectrogram(Data, samplingFreq, show=False, axes=ax2)

    ax = spectrogram(Data, samplingFreq, show=False, axes=ax2)
    mappable = ax2.images[0]
    plt.colorbar(mappable=mappable, cax=ax3)

    ax1.set_ylabel(r'$\Delta$ P - Pa')
    ax2.set_ylabel(r'f - Hz', fontsize=14)
    ax2.set_xlabel(r'$\Delta$t - s', fontsize=12)
    ax2.set_ylim([0.0,6])
    # ax2.set_ybound(lower=None, upper=(highCut*2.0))
    ax2.set_ybound(lower=None, upper=(highCut))

    fig.show()
    return

# ---------------------------ooo0ooo---------------------------
def plotWaveletTransform(tr1):
    print('Calculating Wavelet Transform')
    N = len(tr.data)  # Number of samplepoints
    dt = tr.stats.delta

    x0 = 0
    x1 = N - 1

    t = np.linspace(x0, x1, num=N)
    t1 = np.divide(t, (tr.stats.sampling_rate * 60))

    fig = plt.figure()
    fig.suptitle('Wavelet Transform ' + str(tr.stats.starttime.date), fontsize=12)
    fig.canvas.set_window_title('Wavelet Transform ' + str(tr.stats.starttime.date))
    # ax2 = fig.add_axes([0.1, 0.1, 0.7, 0.60])
    ax1 = fig.add_axes([0.1, 0.75, 0.7, 0.2])  # [left bottom width height]
    ax2 = fig.add_axes([0.1, 0.1, 0.7, 0.60], sharex=ax1)

    print ("x1", x1, "len t", len(t), "len t1", len(t1))

    ax1.plot(t1, tr.data, 'k')
    ax1.set_ylabel(r'$\Delta$P - Pa')

    f_min = 0.01
    f_max = 15.0

    scalogram = cwt(tr.data[x0:x1], dt, 8, f_min, f_max)

    x, y = np.meshgrid(t1, np.logspace(np.log10(f_min), np.log10(f_max), scalogram.shape[0]))

    ax2.pcolormesh(x, y, np.abs(scalogram), cmap=obspy_sequential)

    ax2.set_xlabel("Time  [min]")
    ax2.set_ylabel("Frequency [Hz]")
    ax2.set_yscale('log')
    ax2.set_ylim(f_min, f_max)

    fig.show()

# ---------------------------ooo0ooo---------------------------
def CalcRunningMeanPower(tr, lowCut, highCut, deltaT):
    N = len(tr)
    dt = tr.stats.delta
    newStream = tr.copy()

    newStream.filter('bandpass', freqmin=lowCut, freqmax=highCut, corners=4, zerophase=True)
    x = newStream.data

    x = x ** 2

    nSamplePoints = int(deltaT / dt)
    runningMean = np.zeros((N - nSamplePoints), np.float32)

    # determie first tranche
    tempSum = 0.0

    for i in range(0, (nSamplePoints - 1)):
        tempSum = tempSum + x[i]

        runningMean[i] = tempSum

    # calc rest of the sums by subracting first value and adding new one from far end
    for i in range(1, (N - (nSamplePoints + 1))):
        tempSum = tempSum - x[i - 1] + x[i + nSamplePoints]
        runningMean[i] = tempSum
    # calc averaged acoustic intensity as P^2/(density*c)
    density_times_c = (1.2 * 330)
    runningMean = runningMean / (density_times_c)

    newStream.data = runningMean
    newStream.stats.npts = len(runningMean)

    return newStream

# ---------------------------ooo0ooo---------------------------
def DayPlotAcousticPower(tr, lowCut, highCut, deltaT):
    st2 = CalcRunningMeanPower(tr, lowCut, highCut, deltaT)
    st2.plot(type="dayplot", title='test', data_unit='$Wm^{-2}$', interval=60, right_vertical_labels=False,
             one_tick_per_line=False, color=['k', 'r', 'b', 'g'], show_y_UTC_label=False)


# ---------------------------ooo0ooo---------------------------
def PlotAcousticPower(tr, lowCut, highCut):
    st2 = CalcRunningMeanPower(tr, lowCut, highCut)
    st2.plot(title='test', data_unit='$Wm^{-2}$', show_y_UTC_label=False)


# ---------------------------ooo0ooo---------------------------
def plotMany():
    st1 = opendataFile()
    st2 = opendataFile()
    st3 = opendataFile()
    st4 = opendataFile()
    # st.plot()
    st1.detrend(type='demean')
    st2.detrend(type='demean')
    st3.detrend(type='demean')
    st4.detrend(type='demean')

    tr1 = st1[0].copy()
    tr2 = st2[0].copy()
    tr3 = st3[0].copy()
    tr4 = st4[0].copy()

    lowCut = 0.05
    highCut = 2.0
    yMax = 30
    yMin = 0

    tr1.filter('bandpass', freqmin=lowCut, freqmax=highCut, corners=4, zerophase=True)
    tr2.filter('bandpass', freqmin=lowCut, freqmax=highCut, corners=4, zerophase=True)
    tr3.filter('bandpass', freqmin=lowCut, freqmax=highCut, corners=4, zerophase=True)
    tr4.filter('bandpass', freqmin=lowCut, freqmax=highCut, corners=4, zerophase=True)

    deltaT = 5.0
    tr11 = CalcRunningMeanPower(tr1, deltaT, lowCut, highCut)
    tr12 = CalcRunningMeanPower(tr2, deltaT, lowCut, highCut)
    tr13 = CalcRunningMeanPower(tr3, deltaT, lowCut, highCut)
    tr14 = CalcRunningMeanPower(tr4, deltaT, lowCut, highCut)

    plotMultiple(tr11, tr12, tr13, tr14, yMin, yMax, lowCut, highCut)


# ---------------------------ooo0ooo---------------------------



























# ---------------------------ooo0ooo---------------------------
def plotDayplot(tr, lowCut, highCut):
    tr.filter('bandpass', freqmin=lowCut, freqmax=highCut, corners=4, zerophase=True)
    tr.plot(type="dayplot", title='my title', data_unit='$\Delta$Pa', interval=60, right_vertical_labels=False,
            one_tick_per_line=False, color=['k', 'r', 'b', 'g'], show_y_UTC_label=False)
    return

# ---------------------------ooo0ooo---------------------------
def simplePlot(tr, lowCut, highCut):
    tr.filter('bandpass', freqmin=lowCut, freqmax=highCut, corners=4, zerophase=True)
    tr.plot()
    return

# ---------------------------ooo0ooo---------------------------

def plotsSimpleFFT(tr):
    print('plotting FFT....')
    print(tr.stats)

    dt = tr.stats.delta
    Fs = 1 / dt  # sampling frequency
    tracestart = tr.stats.starttime
    
    t = np.arange(startSec, endSec, dt)  # create np array for time axis
    sigTemp = tr2.data
    s = sigTemp[0:len(t)]

    fig, axes = plt.subplots(nrows=3, ncols=2, figsize=(7, 7))

    # plot time signal:
    axes[0, 0].set_title("Signal")
    axes[0, 0].plot(t, s, color='C0')
    axes[0, 0].set_xlabel("Time")
    axes[0, 0].set_ylabel("Amplitude")
    
    # plot different spectrum types:
    axes[1, 0].set_title("Magnitude Spectrum")
    axes[1, 0].magnitude_spectrum(s, Fs=Fs, color='C1')

    axes[1, 1].set_title("Log. Magnitude Spectrum")
    axes[1, 1].magnitude_spectrum(s, Fs=Fs, scale='dB', color='C1')

    axes[2, 0].set_title("Phase Spectrum ")
    axes[2, 0].phase_spectrum(s, Fs=Fs, color='C2')

    axes[2, 1].set_title("Power Spectrum Density")
    axes[2, 1].psd(s, 256, Fs, Fc=1)

    axes[0, 1].remove()  # don't display empty ax

    fig.tight_layout()
    plt.show()
    return

# ---------------------------ooo0ooo---------------------------
def plotmagnitudeSpectrum(tr):
    print('plotting magnitude spectrum....')

    dt = tr.stats.delta
    Fs = 1 / dt  # sampling frequency
    tracestart = tr.stats.starttime
    
    t = np.arange(startSec, endSec, dt)  # create np array for time axis
    sigTemp = tr2.data
    s = sigTemp[0:len(t)]

    fig, axes = plt.subplots(nrows=3, ncols=1, figsize=(7, 7))

    # plot time signal:
    axes[0].set_title("Signal")
    axes[0].plot(t, s, color='C0')
    axes[0].set_xlabel("Time")
    axes[0].set_ylabel("Amplitude")

    # plot spectrum types:
    axes[1].set_title("Magnitude Spectrum")
    axes[1].magnitude_spectrum(s, Fs=Fs, color='C1')

    axes[2].set_title("Log. Magnitude Spectrum")
    axes[2].magnitude_spectrum(s, Fs=Fs, scale='dB', color='C1')

    fig.tight_layout()
    plt.show()
    return
# ---------------------------ooo0ooo---------------------------
def opendataFile():
    root = tk.Tk()
    root.withdraw()
    root.filename = filedialog.askopenfilename(initialdir=os.getcwd(), title="Select file",
                                               filetypes=[("miniseed data files", "*.mseed")])
    st = read(root.filename)
    return st
# ---------------------------ooo0ooo---------------------------


# ---------------------------------#
#                                  #
#             Main Body            #
#                                  #
# ---------------------------------#

deltaT = 5.0  # time interval seconds to calculate running mean for acoustic power
lowCut = 0.01  # low frequency cut-off
highCut =15.0  # highfrequency cut-off


st1=opendataFile() # select a data file to work on
st1.detrend(type='demean')

tr = st1[0].copy()  # always work with a copy

#plotDayplot(tr, lowCut, highCut)

#----- seelct slice of data to work on
startMinute = 1140
endMinute = 1200
tracestart = tr.stats.starttime
startSec = (startMinute * 60)
endSec = (endMinute * 60)
tr2 = tr.trim(tracestart + startSec, tracestart + endSec)
#------------------------




plotmagnitudeSpectrum(tr2)

#plotSpectrogram(tr2, lowCut, highCut)
#plotWaveletTransform(tr2)

#plotBands(tr2)
#st2 = CalcRunningMeanPower(tr2, lowCut, highCut, deltaT)
#simplePlot(st2, lowCut, highCut)
#st2.plot(title='test', data_unit='$Wm^{-2}$', show_y_UTC_label=False)


#simplePlot(tr, lowCut, highCut)







#plotSpectrogram(tr1, lowcut, highCut, startMin, endMin)
#plotSpectrogram(tr, lowCut, highCut, 70, 90)



plotsSimpleFFT(tr,76, 95)


# ----------------------------------------------


# ---------------------------ooo0ooo---------------------------
# ---------------------------ooo0ooo---------------------------
# ---------------------------ooo0ooo---------------------------
# ---------------------------ooo0ooo---------------------------
# ---------------------------ooo0ooo---------------------------
# ---------------------------ooo0ooo---------------------------
# ---------------------------ooo0ooo---------------------------
# ---------------------------ooo0ooo---------------------------

