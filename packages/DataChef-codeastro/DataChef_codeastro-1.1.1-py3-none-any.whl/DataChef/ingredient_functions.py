import numpy as np
from uncertainties import unumpy
import astropy.units as U
from DataChef import gw_signal_helper


def line(x, m=1, b=0):
    '''Function to make a straight line with slope m and intercept b.

    Args:
        x (:obj:`array`): numpy vector. grid to make line on.
        m (:obj:`int` or :obj:`float`, optional): slope of the line. Default is 1.
        b (:obj:`int` or :obj:`float`, optional): intercept of the line. Default is 0.

    Returns:
        :obj:`array`: m*x + b.
    '''
    
    return np.asarray(x)*m+b
    
def parabola(x, a=1, b=0, c=0):
    '''Function to make a parabola.

    Args:
        x (:obj:`array`): numpy vector. grid to make parabola on.
        a (:obj:`int` or :obj:`float`, optional): second order coefficient. Default is 1.
        b (:obj:`int` or :obj:`float`, optional): first order coefficient. Default is 0.
        c (:obj:`int` or :obj:`float`, optional): zeroth order coefficient. Default is 0.

    Returns:
        :obj:`array`: a*x**2 + b*x + c.
    '''

    x = np.asarray(x)
    return a*x**2 + b*x + c

def cubic(x, a=1, b=0, c=0, d=0):
    '''Function to make a cubic.

    Args:
        x (:obj:`array`): numpy vector. grid to make cubic on.
        a (:obj:`int` or :obj:`float`, optional): third order coefficient. 
        b (:obj:`int` or :obj:`float`, optional): second order coefficient. Default is 1.
        c (:obj:`int` or :obj:`float`, optional): first order coefficient. Default is 0.
        d (:obj:`int` or :obj:`float`, optional): zeroth order coefficient. Default is 0.

    Returns:
        :obj:`array`: a*x**3 + b*x**2 + c*x + d.
    '''

    x = np.asarray(x)
    return a*x**3 + b*x**2 + c*x + d

def sinusoid(x, phase=0, amplitude=1, period=2*np.pi):
    '''Function to make a sinusoid.

    Args:
        x (:obj:`array`): numpy vector. grid to make cubic on.
        phase (:obj:`int` or :obj:`float`, optional): third order coefficient. Default is 0.
        amplitude (:obj:`int` or :obj:`float`, optional): second order coefficient. Default is 1.
        period (:obj:`int` or :obj:`float`, optional): first order coefficient. Default is 2*pi.

    Returns:
        :obj:`array`: A * sin(Bx + C), where A is the amplitude, B is 2*pi / period, C is the initial phase.
    '''

    x = np.asarray(x)
    return amplitude*np.sin(2*np.pi / period*x + phase)

def uniform(x, shift=0, scale=1, seed=None):
    '''Function to generate random white noise.

    Args:
        x (:obj:`array`): numpy vector. grid to make white noise on.
        shift (:obj:`int` or :obj:`float`, optional): shift to the uniform distribution. Default is 0.
        scale (:obj:`int` or :obj:`float`, optional): scale to the uniform distribution. Default is 1.

    Returns:
        :obj:`array`: uniform distribution.
    '''

    if seed is not None:
        np.random.seed(seed)
    return scale * np.random.rand(len(x)) + shift

def gaussian(x, mean=0, stdev=1, seed=None):
    '''Function to generate random gaussian noise.

    Args:
        x (:obj:`array`): numpy vector. grid to make gaussian noise on.
        mean (:obj:`int` or :obj:`float`, optional): mean of the Gaussian distribution. Default is 0.
        stdev (:obj:`int` or :obj:`float`, optional): standard deviation to the Gaussian distribution. Default is 1.

    Returns:
        :obj:`array`: Gaussian distribution.
    '''

    if seed is not None:
        np.random.seed(seed)
    return np.random.normal(loc=mean, scale=stdev, size=len(x))

def poisson(x, lam=0, seed=None):
    '''Function to generate random Poisson noise.

    Args:
        x (:obj:`array`): numpy vector. grid to make white noise on.
        lam (:obj:`int` or :obj:`float`, optional): expectation of interval, must be >= 0.

    Returns:
        :obj:`array`: Poisson distribution.
    '''

    if seed is not None:
        np.random.seed(seed)
    return np.random.poisson(lam=lam, size=len(x))

def gw_signal(x, m1=10, m2=10, orb_period=80, r=12, redshift=0, Phi=4, Theta=1.3, i=None, seed=1 ):

    '''
    Generate 2nd-order post newtonian gravitational waveform (plus polarization) from inspiral binary. Spin not considered.

    Args:
        x (:obj:`array`): numpy vector. grid to make GW signal on.
                        Notice that x shoud be evenly spaced, 
                        also the step (dx) should be less than 1/50 orbital period to make the signal clear.
        m1, m2 (:obj:`int` or :obj:`float`, [M_sun], optional): mass of the binary stars in unit of sorlar mass.
        orb_period (:obj:`int` or :obj:`float`, [s], optional): orbital period of the binary stars in unit of second.
        r (:obj:`int` or :obj:`float`, [kpc], optional): distance of the binary to the detector in unit of kpc.
        redshift (:obj:`int` or :obj:`float`, optional): cosmological redshift of the binary to the detector in unit of kpc.
        Phi (:obj:`int` or :obj:`float`, [rad], optional): ecliptic angular coodinate of the binary, longtitude
        Theta (:obj:`int` or :obj:`float`, [rad], optional): ecliptic angular coodinate of the binary, lattitude(polar angle)
        i (:obj:`int` or :obj:`float`, [rad], optional): inclination of the binary system. Default is a random angle between [0, pi]
        seed (:obj:`int`, optional): A seed for random number generation via the numpy package.

    Returns:
        :obj:`array`: The gravitional waves waveform (plus polarization) calculated with 2nd-order post Newtonian formula from: arXiv:gr-qc/9602024
                        Notice that this waveform will fail if the state of binary is approaching merger.
    '''
    
    nsteps = len(x)
    dt = np.diff(x)[0]

    dt = dt * U.s
    m1 = m1 * U.M_sun
    m2 = m2 * U.M_sun
    p_orb = orb_period * U.s
    r = r * U.kpc
    Phi = Phi * U.rad
    Theta = Theta * U.rad
    np.random.seed(seed)

    rs = redshift
    R_L = r * (1+rs)

    if i == None:
        i = np.random.rand() * np.pi * U.rad
    phi_0 = np.random.rand() * 2 * np.pi * U.rad

    semiaixs,t_c,tau,eta,delta = gw_signal_helper.get_computing_variable(m1,m2,p_orb)

    t_i = 0*U.s
    h_c = np.zeros(nsteps); h_p = np.zeros(nsteps) # waveforms from detector frame

    omega_s0 = gw_signal_helper.get_orb_freq(eta,tau,t_c,t_i/(1+rs)) # orbital frequency at initial observation time
    I_0 = 0.0

    for n in range(nsteps):
        t_n = n * dt ; t_sn = t_n / (1+rs) ; t_n1 = t_n + dt
        omega_s = gw_signal_helper.get_orb_freq(eta,tau,t_c,t_sn)
        phi_s = gw_signal_helper.get_orb_phase(eta,tau,t_c,t_sn)

        phi_r = gw_signal_helper.get_gw_phase(Phi,Theta,omega_s,t_n,t_n1,rs,phi_0,phi_s,I_0)

        h_p[n],h_c[n] = gw_signal_helper.get_waveform(tau,eta,delta,i,R_L,phi_r,omega_s)
    
    return h_p
