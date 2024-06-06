import segyio
import numpy as np


def read_segy(fname : str):    
    with segyio.open(fname, ignore_geometry=True) as f:
        dt = f.bin[segyio.BinField.Interval]                
        traces = [f.trace[i] for i in range(f.tracecount)]        
    return np.array(traces).T, dt/1000000

def get_spectrum(traces : np.ndarray, dt : float):
    # Calculate the FFT of each trace (time axis)   
    fft_data = np.fft.ifft(traces, axis=0)
    # Calculate the amplitude spectrum of each trace
    amp_spectrum = np.abs(fft_data)
    # Calculate the average amplitude spectrum across all traces
    avg_amp_spectrum = np.mean(amp_spectrum, axis=1)
    freq = np.fft.fftfreq(traces.shape[0], d=dt)
    pos_freq_idx = freq >= 0 # Get indices of positive frequencies
    pos_freq = freq[pos_freq_idx]
    pos_spec = avg_amp_spectrum[pos_freq_idx]
    return pos_freq, pos_spec

def scale_data_for_showing(data : np.ndarray) -> np.ndarray:
    min_val = np.min(data)
    max_val = np.max(data)
    scaled_array = (data - min_val) / (max_val - min_val)
    uint8_array = (scaled_array * 255).astype(np.uint8)
    return uint8_array


                 
                 


def normalize_data(data):
    normalized = np.zeros_like(data)
    for i in range(data.shape[1]):
        normalized[:, i] = data[:, i]/np.max(np.abs(data[:, i]))
    return normalized         
