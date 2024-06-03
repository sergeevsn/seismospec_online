import segyio
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

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

def get_img_fig(data, dt):
    x_axis = np.arange(1, data.shape[1]+1)
    y_axis = np.arange(0, data.shape[0]*dt*1000, dt*1000)
    fig = px.imshow(data, 
               x = x_axis,
               y = y_axis,
               labels=dict(x="Trace", 
                                    y="Time, ms", 
                                    color="Amp"),     
               width=600,
               height=600,
               aspect='auto',                
               binary_string=False,  
               color_continuous_scale='gray',               
    )
    
                 
                 
               
    
    fig.update_layout(
   
        dragmode="drawrect",   
        newshape=dict(fillcolor="cyan", opacity=0.3, line=dict(color="darkblue", width=1)),
        xaxis={'side': 'top'}
        
    )
# xaxis_title="Trace Number",
#        yaxis_title="Time, ms"    
#yaxis = {'tickvals': np.arange(0, (data.shape[0]//10)*100+100, 100), 'ticktext' : [str(n) for n in np.arange(0, data.shape[0]*dt*1000 + 100*dt*1000, 100*dt*1000)]}
    return fig

def normalize_data(data):
    normalized = np.zeros_like(data)
    for i in range(data.shape[1]):
        normalized[:, i] = data[:, i]/np.max(np.abs(data[:, i]))
    return normalized         


def get_spec_fig(data, dt):
    spec, freq = get_spectrum(data, dt)
    pos_freq_idx = freq >= 0 # Get indices of positive frequencies
    pos_freq = freq[pos_freq_idx]
    pos_spec = spec[pos_freq_idx]
    fig = go.Figure(data=[go.Scatter(x=pos_freq, y=pos_spec, fill='tozerox', mode='lines', 
                                 line=dict(color='red'), fillcolor='rgba(255, 0, 0, 0.5)')])
    fig.update_layout(
    title="Amplitude Spectrum",
    xaxis_title="Frequency, Hz",
    yaxis_title="Amplitude",
    xaxis={'tickformat': ".0f", 'side': 'top', 'tickvals' : np.arange(0, int(1/dt/2)+10, 20)},
    autosize=False,
    width=600,
    height=600,    
   
    )
    fig.update_xaxes(range=[0, 1/dt/2])
    fig.update_yaxes(range=[np.min(spec), np.max(spec)+0.05*np.max(spec)])  
    return fig    