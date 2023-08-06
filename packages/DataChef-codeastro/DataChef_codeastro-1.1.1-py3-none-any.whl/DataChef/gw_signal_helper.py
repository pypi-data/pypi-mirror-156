import numpy as np
import astropy.units as U
import astropy.constants as CONST
import scipy.integrate

G = CONST.G
c = CONST.c
Omega = (2 * np.pi * U.rad / (1 * U.yr)).to(U.rad/U.s)  # angular frequency earth's orbit around sun
R = 1 * U.AU


def get_computing_variable(m1, m2, p_orb):
    '''
    Get all the computing variables needed to obtain gw waveform. (ref:M&H)

    Parameters
    -----------
    m1,m2: float or array-like of shape (n_sources,) [M_sun]
        binary masses 
    p_orb: float or array-like of shape (n_sources,) [s]
        orbital period 

    Returns
    -----------
    a: [km]
        semi-major axis of binary obit (ref:Kepler 3rd Law)
    t_c: [s]
        time to coalescence from t_s = 0, source frame time (ref:Peters1964 eq(5.10))
    tau: [s]
        express the system's total mass in units of time (ref:M&H eq(3.2a))
    eta:
        unitless expression of the ratio of the objects' masses (ref:M&H eq(3.2b))
    delta:
        unitless expression of the difference between the bianry masses (ref:M&H eq(3.4))
        * note: eta and delta are not independent of each other: eta = 1/4*(1-delta**2)
    '''

    a = ((G * (m1 + m2) * p_orb**2).to(U.km**3) / (4*np.pi**2))**(1/3)
    t_c = (a**4 / (4 * (64/5 * G**3 * m1 * m2 * (m1+m2) / c**5))).to(U.s)

    tau = 5 * G * (m1 + m2) / c**3
    eta = m1 * m2 / (m1 + m2)**2
    delta = (m1 - m2) / (m1 + m2)

    return [a,t_c,tau,eta,delta]

def get_orb_freq(eta,tau,t_c,t):
    '''
    Obataining orbital frequency of circular binary at z=0. (ref:BIWW eq(8))

    Parameters
    -----------
    t_c: float or array-like of shape (n_sources,) [s]
        time to coalescence from t = 0 (ref:Peters1964 eq(5.10))
    tau: float or array-like of shape (n_sources,) [s]
        express the system's total mass in units of time (ref:M&H eq(3.2a))
    eta: float or array-like of shape (n_sources,)
        unitless expression of the ratio of the objects' masses (ref:M&H eq(3.2b))
    t: float or array-like of shape (n_sources,) [s]
        source frame time

    Returns
    -----------
    omega_s: [rad/s]
        source's orbital frequency at source frame time t valid up to the 2PN order 
    '''

    G_t = (eta / tau * (t_c - t)) ** (1/8)
    omega_s = 5/8 * 1/tau * (G_t**(-3) + (743/2688 + 11/32 * eta) * G_t**(-5) - 3/10 * np.pi * G_t**(-6)\
                            + (1855099/14450688 + 56975/258048 * eta + 371/2048 * eta**2) * G_t**(-7)) 
    omega_s = omega_s.to(1/U.s) * U.rad
    return omega_s

def get_orb_phase(eta,tau,t_c,t):
    '''
    Obataining orbital phase of circular binary at z=0. (ref:M&H eq(3.9),BIWW eq(7))

    Parameters
    -----------
    t_c: float or array-like of shape (n_sources,) [s]
        time to coalescence from t = 0 (ref:Peters1964 eq(5.10))
    tau: float or array-like of shape (n_sources,) [s]
        express the system's total mass in units of time (ref:M&H eq(3.2a))
    eta: float or array-like of shape (n_sources,)
        unitless expression of the ratio of the objects' masses (ref:M&H eq(3.2b))
    t: float or array-like of shape (n_sources,) [s]
        source frame time

    Returns
    -----------
    phi_s: [rad]
        source's orbital phase valid up to the 2PN order at source frame time t (ref:M&H eq(3.9),BIWW eq(7))
        * note: formula used contains information of phi_s(t=0),
          the actual form of this variable is phi_s(t)-phi_s(0)
    '''

    G_0 = (eta / tau * (t_c)) ** (1/8)
    phi_s0 = 1/eta * (G_0**5 + (3715/8064 + 55/96 * eta) * G_0**3 - 3/4 * np.pi * G_0**2 + \
            (9275495/14450688 + 284875/258048 * eta + 1855/2048 * eta**2) * G_0)
    phi_s0 = (phi_s0 * U.rad).to(U.rad)
    
    G_t = (eta / tau * (t_c - t)) ** (1/8)
    phi_s = 1/eta * ((G_t**5 + (3715/8064 + 55/96 * eta) * G_t**3 - 3/4 * np.pi * G_t**2 + \
            (9275495/14450688 + 284875/258048 * eta + 1855/2048 * eta**2) * G_t))- phi_s0.value
    phi_s = phi_s * U.rad

    return phi_s

def get_gw_phase(Phi, Theta, omega_s, t_n ,t_n1, rs, phi_0, phi_s, I_0):
    '''
    Calculate the gravitational wave phase of circular binary at z=0 
    numerically or analytically. (ref:M&H eq(3.8))

    Parameters
    -----------
    Phi: float or array-like of shape (n_sources,) [rad]
        ecliptic angular coodinate, longtitude
        reference axis: Phi=0 is vector from sun to detector's center of mass when t=0
    Theta: float or array-like of shape (n_sources,) [rad]
        ecliptic angular coodinate, lattitude(polar angle)
    omega_s: float or array-like of shape (n_sources,) [rad/s]
        source's orbital frequency at source frame time t valid up to the 2PN order 
    t_n: float or array-like of shape (n_sources,) [s]
        computing time at current step (detector frame)
    t_n1: float or array-like of shape (n_sources,) [s]
        computing time at next step (detector frame)
        * note: should be t_n + dt, where dt must be smaller than 1/50 orbital period.
    rs: float or array-like of shape (n_sources,)
        cosmological redshift of the source.
    phi_0: float or array-like of shape (n_sources,) [rad]
        phase of the received wave at time detector frame t = [1+z]t_s = 0
    phi_s: [rad]
        source's orbital phase valid up to the 2PN order at source frame time(ref:M&H eq(3.9),BIWW eq(7))
        * note: formula used contains information of phi_s(t=0), the actual form of this variable is phi_s(t)-phi_s(0)
    I_0:
        initial value for the integral. (ref:M&H 3.8b)
    numerical:
        If 1, use RK4 to do the integral of I_0.
        If 0, use analytic result (consider omega_s constant) to do the integral of I_0.
        default is 1 using numerical method.
     
    Returns
    -----------
    phi_r: [rad]
            received gw phase at detector frame time (\ref:M&H eq(3.8a))            
    '''

    def I_0dot(t, x):
        '''
        first order derivative equation for the RK4 in gw phase. (ref:M&H 3.8b)
        t should be in detector frame.
        '''

        I_0dot = omega_s.value * np.sin(Omega.value * t - Phi.value)
        return I_0dot
        
    result = scipy.integrate.solve_ivp(I_0dot,[t_n.value,t_n1.value],y0=np.array([I_0]))
    I_0 = result.y[0][-1]
    phi_r = phi_0 + phi_s - Omega * R / (c * (1+rs)) * np.sin(Theta) * I_0

    return phi_r

def get_waveform(tau,eta,delta,i,r,phi_r,omega_s):
        '''
        Obataining orbital phase of circular binary at z=0. (ref:M&H eq(3.9),BIWW eq(7))

        Parameters
        -----------
        tau: float or array-like of shape (n_sources,) [s]
                express the system's total mass in units of time (ref:M&H eq(3.2a))
        eta: float or array-like of shape (n_sources,)
                unitless expression of the ratio of the objects' masses (ref:M&H eq(3.2b))
        delta: float or array-like of shape (n_sources,)
                unitless expression of the difference between the bianry masses (ref:M&H eq(3.4))
        * note: eta and delta are not independent of each other: eta = 1/4*(1-delta**2)
        i: float or array-like of shape (n_sources,) [rad]
                angle of source's orbital angular momentum vector relative to vector pointing from souce to detector
                The normal is chosen to be right-handed with respect to the sense of motion so that i between [0, pi] (ref:BIWW para btw eq(4e)&eq(5))
                default is 'random', which uses numpy to generate random angle
        r: float or array-like of shape (n_sources,) [kpc]
                source distance
                * note: if source is cosmologically distant object, should use R_L, which is luminosity distance.
        phi_r: float or array-like of shape (n_sources,) [rad]
                received gw phase (\ref:M&H eq(3.8a))
        omega_s: float or array-like of shape (n_sources,) [rad/s]
                source's orbital frequency at source frame time t valid up to the 2PN order 
                
        Returns
        -----------
        h_p, h_c:
                value of plus/cross polarization waveform (ref:M$H eq(3.1))
        '''
        # 2 PN order H
        cos = np.cos(i);sin = np.sin(i)
        # for H_+
        Hp0 = - (1 + cos**2) * np.cos(2 * phi_r)
        Hp1 = - delta / 8 * sin * ((5 + cos**2) * np.cos(phi_r )\
                                - 9 * (1 + cos**2) * np.cos(3 * phi_r))
        Hp2 = 1/6 * ((19 + 9 * cos**2 - 2 * cos**4) \
                - eta * (19 - 11 * cos**2 - 6 * cos**4)) * np.cos(2 * phi_r) \
                - 4/3 * sin**2 * (1 + cos**2) * (1 - 3 * eta) * np.cos(4 * phi_r)
        Hp3 = delta / 192 * sin * (((57 + 60 * cos**2 - cos**4) - 2 * eta   \
                                        * (49 - 12 * cos**2 - cos**4)) * np.cos(phi_r)\
                                - 27/2 * ((73 + 40 * cos**2 - 9 * cos**4) - 2 * eta   \
                                        * (25 - 8 * cos**2 - 9 * cos**4)) * np.cos(3 * phi_r)\
                                + 625/2 * (1 - 2 * eta  ) * sin**2 * (1 + cos**2) * np.cos(5 * phi_r))\
                                - 2 * np.pi * (1 + cos**2) * np.cos(2 * phi_r)
        Hp4 = 1/120 * ((22 + 396 * cos**2 + 145 * cos**4 - 5 * cos**6) + 5/3 * eta   \
                        * (706 - 216 * cos**2 - 251 * cos**4 + 15 * cos**6) - 5 * eta **2\
                        * (98 - 108 * cos**2 + 7 * cos** 4 + 5 * cos**6)) * np.cos(2 * phi_r) \
                + 2/15 * sin**2 * ((59 + 35 * cos**2 - 8 * cos**4) - 5/3 * eta   \
                        * (131 + 59 * cos**2 - 24 * cos**4) + 5 * eta**2 \
                        * (21 - 3 * cos**2 - 8 * cos** 4)) * np.cos(4 * phi_r) \
                - 81/40 * (1 - 5 * eta + 5 * eta**2) * sin**4 * (1 + cos**2) * np.cos(6 * phi_r)\
                + delta / 40 * sin * ((11 + 7 * cos**2 + 10 * (5 + cos**2) * np.log(2)) * np.sin(phi_r)\
                                - 5 * np.pi * (5 + cos**2) * np.cos(phi_r)\
                                -27 * (7 - 10 * np.log(3/2)) * (1 + cos**2) * np.sin(3 * phi_r) \
                                + 135 * np.pi * (1 + cos**2) * np.cos(3 * phi_r))
        Hp = [Hp0,Hp1,Hp2,Hp3,Hp4]

        # for H_x
        Hc0 = - 2 * cos * np.sin(2 * phi_r)
        Hc1 = - 3/4 * delta * cos * sin * (np.sin(phi_r) - 3 * np.sin(3*phi_r))
        Hc2 = cos / 3 * ((17 - 4 * cos**2) - eta * (13 - 12 * cos**2)) * np.sin(2 * phi_r)\
                - 8/3 * (1 - 3 * eta) * cos * sin**2 * np.sin(4 * phi_r)
        Hc3 = delta / 96 * sin * cos * (((63 - 5 * cos**2) - 2 * eta * (23 - 5 * cos**2)) * np.sin(phi_r)\
                                        - 27/2 * ((67 - 15 * cos**2) - 2 * eta * (19 - 15 * cos**2)) * np.sin(3 * phi_r)\
                                        + 625/2 * (1 - 2 * eta) * sin**2 * np.sin(5 * phi_r))\
                                - 4 * np.pi * cos * np.sin(2 * phi_r)
        Hc4 = cos / 60 * ((68 + 226 * cos**2 - 15 * cos**4) + 5/3 * eta * (572 - 490 * cos**2 + 45 * cos**4)\
                        - 5 * eta**2 * (56 - 70 * cos**2 + 15 * cos**4)) * np.sin(2 * phi_r)\
                + 4/15 * cos * sin**2 * ((55 - 12 * cos**2) - 5/3 * eta * (119 - 36 * cos**2) + 5 * eta**2 \
                                        * (17 - 12 * cos**2))* np.sin(4 * phi_r)\
                - 81/20 * (1 - 5 * eta + 5 * eta**2) * cos * sin**4 * np.sin(6 * phi_r)\
                - 3/20 * sin * cos * delta *((3 + 10 * np.log(2)) * np.cos(phi_r) + 5 * np.pi * np.sin(phi_r)
                                        - 9 * (7 - 10 * np.log(3/2)) * np.cos(3 * phi_r) - 45 * np.pi * np.sin(3 * phi_r))
        Hc = [Hc0,Hc1,Hc2,Hc3,Hc4]

        # waveform
        epslon = ((tau * omega_s / 5) / U.rad).to(U.dimensionless_unscaled) ** (1/3)
        h_p = ((2 * tau * c * eta) / (5 * r)).to(U.dimensionless_unscaled) * epslon**2 * \
                        (Hp [0] + epslon  * Hp [1] + epslon**2 * \
                        Hp[2] + epslon**3 * Hp[3] + epslon**4 * Hp[4])

        h_c = ((2 * tau * c * eta) / (5 * r)).to(U.dimensionless_unscaled) * epslon**2 * \
                        (Hc[0] + epslon * Hc[1] + epslon**2 * \
                        Hc[2] + epslon**3 * Hc[3] + epslon**4 * Hc[4])
        return [h_p,h_c]

