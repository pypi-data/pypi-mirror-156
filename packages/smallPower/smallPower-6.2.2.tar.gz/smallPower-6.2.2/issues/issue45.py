import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd,sys
from scipy import signal
from matplotlib import pyplot as plt

def s_bode_vs_freqs_vs_mano():
    b, a = signal.cheby2(4, 40, 100, 'low', analog=True)
    ##### b,a bode diagramm
    w, h = signal.freqs(b, a)
    plt.semilogx(w, 20 * np.log10(abs(h)))
    plt.title('Chebyshev Type II frequency response (rs=40)')
    plt.xlabel('Frequency [radians / second]')
    plt.ylabel('Amplitude [dB]')
    plt.margins(0, 0.1)
    plt.grid(which='both', axis='both')
    plt.axvline(100, color='green') # cutoff frequency
    plt.axhline(-40, color='green') # rs
    # plt.show()
    # NOTE:
    bode=pd.DataFrame([w/(2*np.pi),20 * np.log10(abs(h)),np.angle(h)*180/np.pi],index=['frequency(Hz)','gain(Db)','dephasage(degrees)']).T.set_index('frequency(Hz)')
    ##### b,a bode diagramm
    system = signal.TransferFunction(b,a, dt=0.05)
    s_bode=signal.dbode(system)
    s_bode=pd.DataFrame(s_bode,index=['frequency(Hz)','gain(Db)_db','dephasage(degrees)_db']).T.set_index('frequency(Hz)')
    s_bode.index=s_bode.index/(2*np.pi)
    fig1=px.scatter(s_bode.melt(ignore_index=False),facet_row='variable',log_x=True);fig1.update_traces(mode='lines+markers');fig1.update_yaxes(matches='x').show()
    fig2=px.scatter(bode.melt(ignore_index=False),facet_row='variable',log_x=True);fig2.update_traces(mode='lines+markers');fig2.update_yaxes(matches='x').show()

def sos_vs_ba_filter():
    b, a = signal.cheby2(4, 40, 100, 'low', analog=True)
    sos = signal.cheby2(4, 40, 100, 'low', analog=True,output='sos')

    b,a=signal.cheby2(12, 20, 17, 'hp', fs=1000, output='ba')
    sos=signal.cheby2(12, 20, 17, 'hp', fs=1000, output='sos')
    signal.dbode(b,a,10)
    b, a = signal.cheby2(4, 40, 100, 'hp', analog=True)
    w, h = signal.freqs(b, a)

# def analog_vs_digital():


def pid_transfer_function():
    kd,kp,ki=[1,1,1]
    ss=signal.TransferFunction([kd,kp,ki],[1,0],dt=0.5)
    w,h,phi=signal.dbode(ss)
    sys.exit()

#####
url_pid= 'https://ctms.engin.umich.edu/CTMS/index.php?example=Introduction&section=ControlPID'

def bode_first_order():
    a=10
    b=1
    s=signal.TransferFunction([1],[a,b])
    massRessort_d=signal.TransferFunction([1],[a,b],dt=0.0000001)

    x=np.logspace(-3,3,100)
    H=1/(1j*a*x+b)
    # w, h = signal.freqresp(massRessort)
    # bode1=pd.DataFrame([w/(2*np.pi),20 * np.log10(abs(h)),np.angle(h)*180/np.pi],index=['frequency(Hz)','gain(Db)','dephasage(degrees)']).T.set_index('frequency(Hz)')
    # bode2=pd.DataFrame([w/(2*np.pi),20 * np.log10(abs(h)),np.angle(h)*180/np.pi],index=['frequency(Hz)','gain(Db)','dephasage(degrees)']).T.set_index('frequency(Hz)')
    bode_c=pd.DataFrame(s.bode(),index=['frequency(Hz)','gain(dB)','dephasage(degrees)_db']).T.set_index('frequency(Hz)')
    bode_d=pd.DataFrame(massRessort_d.bode(),index=['frequency(Hz)','gain(dB)','dephasage(degrees)_db']).T.set_index('frequency(Hz)')
    bode_m=pd.DataFrame([x,20*np.log10(np.abs(H)),np.angle(H)*180/np.pi],index=['frequency(Hz)','gain(dB)','dephasage(degrees)_db']).T.set_index('frequency(Hz)')

    # bode_d=pd.DataFrame(signal.dbode(massRessort_d),index=['frequency(Hz)','gain(Db)_db','dephasage(degrees)_db']).T.set_index('frequency(Hz)')

    bode_c.index=bode_c.index/(2*np.pi)
    bode_d.index=bode_d.index/(2*np.pi)
    bode_m.index=bode_m.index/(2*np.pi)


    fig=go.Figure(go.Scatter(x=bode_c.index,y=bode_c['gain(dB)'],name='continuous'))
    fig.add_trace(go.Scatter(x=bode_m.index,y=bode_m['gain(dB)'],marker_color='red',name='manual'))
    fig.add_trace(go.Scatter(x=bode_d.index,y=bode_d['gain(dB)'],marker_color='green',name='discrete'))
    fig.update_xaxes(showgrid=True, gridwidth=2, gridcolor='black',type='log')
    fig.update_yaxes(showgrid=True, gridwidth=2, gridcolor='black')
    fig.update_traces(mode='lines+markers').show()

    px.line(pd.DataFrame(s.step()).T.set_index(0)).show()
    sys.exit()
    fig1=px.scatter(bode_c.melt(ignore_index=False),facet_row='variable',log_x=True);
    fig1.update_xaxes(showgrid=True, gridwidth=2, gridcolor='black')
    fig1.update_yaxes(showgrid=True, gridwidth=2, gridcolor='black')
    fig1.update_traces(mode='lines+markers');fig1.update_yaxes(matches='x').show()

    fig2=px.scatter(bode_d.melt(ignore_index=False),facet_row='variable',log_x=True);
    fig2.update_xaxes(showgrid=True, gridwidth=2, gridcolor='black')
    fig2.update_yaxes(showgrid=True, gridwidth=2, gridcolor='black')
    fig2.update_traces(mode='lines+markers');fig2.update_yaxes(matches='x').show()

    # fig3=px.scatter(bode_m.melt(ignore_index=False),facet_row='variable',log_x=True);
    # fig3.update_xaxes(showgrid=True, gridwidth=2, gridcolor='black')
    # fig3.update_yaxes(showgrid=True, gridwidth=2, gridcolor='black')
    # fig3.update_traces(mode='lines+markers');fig3.update_yaxes(matches='x').show()

# def bode_resonant():
m = 10  # kg
b = 10 # N s/m
k = 20 # N/m
F = 1  # N
s=signal.TransferFunction([1],[m,b,k])
massRessort_d=signal.TransferFunction([1],[m,b,k],dt=1.5)

x=np.logspace(-2,3,100)
H=1/(-m*x**2+1j*b*x+k)
# w, h = signal.freqresp(massRessort)
# bode1=pd.DataFrame([w/(2*np.pi),20 * np.log10(abs(h)),np.angle(h)*180/np.pi],index=['frequency(Hz)','gain(Db)','dephasage(degrees)']).T.set_index('frequency(Hz)')
# bode2=pd.DataFrame([w/(2*np.pi),20 * np.log10(abs(h)),np.angle(h)*180/np.pi],index=['frequency(Hz)','gain(Db)','dephasage(degrees)']).T.set_index('frequency(Hz)')
bode_c=pd.DataFrame(s.bode(),index=['frequency(Hz)','gain(dB)','dephasage(degrees)_db']).T.set_index('frequency(Hz)')
bode_d=pd.DataFrame(massRessort_d.bode(),index=['frequency(Hz)','gain(dB)','dephasage(degrees)_db']).T.set_index('frequency(Hz)')
bode_m=pd.DataFrame([x,20*np.log10(np.abs(H)),np.angle(H)*180/np.pi],index=['frequency(Hz)','gain(dB)','dephasage(degrees)_db']).T.set_index('frequency(Hz)')

# bode_d=pd.DataFrame(signal.dbode(massRessort_d),index=['frequency(Hz)','gain(Db)_db','dephasage(degrees)_db']).T.set_index('frequency(Hz)')

bode_c.index=bode_c.index/(2*np.pi)
bode_d.index=bode_d.index/(2*np.pi)
bode_m.index=bode_m.index/(2*np.pi)

fig=go.Figure(go.Scatter(x=bode_c.index,y=bode_c['gain(dB)'],name='continuous'))
fig.add_trace(go.Scatter(x=bode_m.index,y=bode_m['gain(dB)'],marker_color='red',name='manual'))
fig.add_trace(go.Scatter(x=bode_d.index,y=bode_d['gain(dB)'],marker_color='green',name='discrete'))
fig.update_xaxes(showgrid=True, gridwidth=2, gridcolor='black',type='log')
fig.update_yaxes(showgrid=True, gridwidth=2, gridcolor='black')
fig.update_traces(mode='lines+markers')

# fig.show()
#### response to step function
r1=pd.DataFrame(s.step(T=np.linspace(0,25,1000))).T.set_index(0).squeeze()
fig=go.Figure(go.Scatter(x=r1.index,y=r1,name='step'))
fig.show()
sys.exit()
