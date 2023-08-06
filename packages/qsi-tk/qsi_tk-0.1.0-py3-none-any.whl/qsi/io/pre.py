#### Pre-processing ####
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np

def butter_highpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype = "high", analog = False)
    return b, a

def butter_highpass_filter(data, cutoff, fs, order=5):
    b, a = butter_highpass(cutoff, fs, order=order)
    y = signal.filtfilt(b, a, data)
    return y

def butter_lowpass(cutoff, fs, order=5):
    nyq = 0.5 * fs
    normal_cutoff = cutoff / nyq
    b, a = signal.butter(order, normal_cutoff, btype='low', analog=False)
    return b, a

def butter_lowpass_filter(data, cutoff, fs, order=5):
    b, a = butter_lowpass(cutoff, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y

def butter_bandpass(lowcut, highcut, fs, order=5):
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = signal.butter(order, [low, high], btype='band')
    return b, a

def butter_bandpass_filter(data, lowcut, highcut, fs, order=5):
    b, a = butter_bandpass(lowcut, highcut, fs, order=order)
    y = signal.lfilter(b, a, data)
    return y

def filter(x, sr, lc=None, hc=None, order = 5, display = True):
    '''
    Filter signal with low-pass/high-pass/band-pass Butterworth filter.

    Parameters
    ----------
    x : input signal
    sr : sampling rate. 
        nyq = 0.5 * sr gets the frequency upper limit by the Nyquist Theorem.
    lc : low cutoff freq
    hc : high cutoff freq
    order : Butterworth order
    '''

    if lc is None and hc is None: # do nothing
        return x
    elif lc is None and hc > 0:
        b, a = butter_lowpass(hc, sr, order=order)
    elif lc > 0 and lc is None:
        b, a = butter_highpass(lc, sr, order=order)
    elif lc > 0 and hc > 0:
        b, a = butter_bandpass(lc, hc, sr, order=order)
    else:
        b, a = 0, 0

    y = signal.lfilter(b, a, x)
    
    if display:
        
        # Plotting the frequency response.
        w, h = signal.freqz(b, a, worN=8000)
        plt.subplot(2, 1, 1)
        plt.plot(0.5*sr*w/np.pi, np.abs(h), 'b')
        if lc > 0:
            plt.plot(lc, 0.5*np.sqrt(2), 'ko')
            plt.axvline(lc, color='k')
        if hc > 0:
            plt.plot(hc, 0.5*np.sqrt(2), 'ko')
            plt.axvline(hc, color='k')
        plt.xlim(0, 0.5*sr)
        plt.title("Filter Frequency Response")
        plt.xlabel('Frequency [Hz]')
        plt.grid()

        plt.subplot(2, 1, 2)
        plt.plot(x, 'b-', label='data')
        plt.plot(y, 'g-', linewidth=2, label='filtered data')
        plt.xlabel('Time [sec]')
        plt.grid()
        plt.legend()

        plt.subplots_adjust(hspace=0.35)
        plt.show()

    return y