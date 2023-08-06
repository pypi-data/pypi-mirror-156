# Copyright (C) 2017-2022 elphmod Developers
# This program is free software under the terms of the GNU GPLv3 or later.

"""Step and delta smearing functions."""

from __future__ import division

import numpy as np

try:
    from scipy.special import erf
except ImportError:
    import math

    erf = np.vectorize(math.erf)

xmax = 709.0 # approx. log([max. double] / 2 - 1)

def fermi_dirac(x):
    """Calculate Fermi function."""

    # return 1 - 0.5 * np.tanh(0.5 * x)

    x = np.minimum(x, xmax)

    return 1 / (np.exp(x) + 1)

def fermi_dirac_delta(x):
    """Calculate negative derivative of Fermi function."""

    x = np.minimum(np.absolute(x), xmax)

    return 1 / (2 * np.cosh(x) + 2)

def fermi_dirac_delta_prime(x):
    """Calculate negative 2nd derivative of Fermi function."""

    x = np.sign(x) * np.minimum(np.absolute(x), xmax)

    return -np.sinh(x) / (2 * (np.cosh(x) + 1) ** 2)

fermi_dirac.delta = fermi_dirac_delta
fermi_dirac.delta_prime = fermi_dirac_delta_prime

def gauss(x):
    """Calculate Gaussian step function."""

    return 0.5 * (1 - erf(x))

def gauss_delta(x):
    """Calculate negative derivative of Gaussian step function."""

    return np.exp(-x * x) / np.sqrt(np.pi)

def gauss_delta_prime(x):
    """Calculate negative 2nd derivative of Gaussian step function."""

    return -2 * x * np.exp(-x * x) / np.sqrt(np.pi)

gauss.delta = gauss_delta
gauss.delta_prime = gauss_delta_prime

def marzari_vanderbilt(x):
    """Calculate Marzari-Vanderbilt (cold smearing) step function."""

    y = x + 1 / np.sqrt(2)

    return (erf(-y) + 1) / 2 + np.exp(-y * y) / np.sqrt(2 * np.pi)

def marzari_vanderbilt_delta(x):
    """Calculate negative derivative of Marzari-Vanderbilt step function."""

    y = x + 1 / np.sqrt(2)

    return (np.sqrt(2) * y + 1) * np.exp(-y * y) / np.sqrt(np.pi)

def marzari_vanderbilt_delta_prime(x):
    """Calculate negative 2nd derivative of Marzari-Vanderbilt step function."""

    y = x + 1 / np.sqrt(2)

    return (np.sqrt(2) - 2 * y
        * (np.sqrt(2) * y + 1)) * np.exp(-y * y) / np.sqrt(np.pi)

marzari_vanderbilt.delta = marzari_vanderbilt_delta
marzari_vanderbilt.delta_prime = marzari_vanderbilt_delta_prime

def methfessel_paxton_general(x, N=0):
    r"""Calculate Methfessel-Paxton step function and its negative derivative.

    From Phys. Rev. B 40, 3616 (1989):

    .. math::

        S_0(x) &= \frac {1 - erf(x)} 2 \\
        S_N(x) &= S_0(x) + \sum_{n = 1}^N A_n H_{2 n - 1}(x) \exp(-x^2) \\
        D_N(x) &= -S'(N, x) = \sum{n = 0}^N A_n H_{2 n}(x) \exp(-x^2) \\
        A_n &= \frac{(-1)^n}{\sqrt \pi n! 4^n}

    Hermite polynomials:

    .. math::

        H_0(x) &= 1 \\
        H_1(x) &= 2 x \\
        H_{n + 1}(x) &= 2 x H_n(x) - 2 n H_{n - 1}(x) \\

    For ``N = 0``, the Gaussian step function is returned.

    This routine has been adapted from Quantum ESPRESSO:

    * Step function: Modules/wgauss.f90
    * Delta function: Modules/w0gauss.f90
    """
    S = gauss(x)
    D = gauss_delta(x)
    P = gauss_delta_prime(x)

    # In the following, our Hermite polynomials (`H` and `h`) are defined such
    # that they contain the factor exp(-x^2) / sqrt(pi) = D(0, x). On the other
    # hand, our coefficient A(n) (`a`) does not contain the factor 1 / sqrt(pi).

    H = 0 # H(-1, x)
    h = D # H( 0, x)

    a = 1.0
    m = 0

    for n in range(1, N + 1):
        H = 2 * x * h - 2 * m * H # H(1, x), H(3, x), ...
        m += 1

        h = 2 * x * H - 2 * m * h # H(2, x), H(4, x), ...
        m += 1

        a /= -4 * n

        S += a * H
        D += a * h
        P -= a * (2 * x * h - 2 * m * H) # H(3, x), H(5, x), ...

    return S, D, P

def methfessel_paxton(x):
    """Calculate first-order Methfessel-Paxton step function."""

    return methfessel_paxton_general(x, N=1)[0]

def methfessel_paxton_delta(x):
    """Calculate negative derivative of first-order MP step function."""

    return methfessel_paxton_general(x, N=1)[1]

def methfessel_paxton_delta_prime(x):
    """Calculate negative 2nd derivative of first-order MP step function."""

    return methfessel_paxton_general(x, N=1)[2]

methfessel_paxton.delta = methfessel_paxton_delta
methfessel_paxton.delta_prime = methfessel_paxton_delta_prime

def lorentz(x):
    """Calculate Lorentz step function.

    Used to simulate the influence of a wide box-shaped hybridization function
    at low temperatures. Formula derived by Tim O. Wehling and Erik G.C.P. van
    Loon. Here, we have :math:`x = \epsilon / h` with the height :math:`h` of
    the hybridization, instead of :math:`x = \epsilon / k T` with the
    temperature :math:`T`.
    """
    return 0.5 - np.arctan(x / np.pi) / np.pi

def lorentz_delta(x):
    """Calculate negative derivative of Lorentz step function."""

    return 1.0 / (x * x + np.pi * np.pi)

def lorentz_delta_prime(x):
    """Calculate negative 2nd derivative of Lorentz step function."""

    return -2 * x / (x * x + np.pi * np.pi) ** 2

lorentz.delta = lorentz_delta
lorentz.delta_prime = lorentz_delta_prime

def heaviside(x):
    """Calculate (reflected) Heaviside function."""

    return 0.5 - 0.5 * np.sign(x)

def heaviside_delta(x):
    """Calculate negative derivative of (reflected) Heaviside function."""

    delta = np.copy(x)

    zero = delta == 0

    delta[zero] = np.inf
    delta[~zero] = 0.0

    return delta

def heaviside_delta_prime(x):
    """Calculate negative 2nd derivative of (reflected) Heaviside function."""

    delta_prime = np.copy(x)

    zero = delta_prime == 0

    delta_prime[zero] = -np.copysign(np.inf, delta_prime[zero])
    delta_prime[~zero] = 0.0

    return delta_prime

heaviside.delta = heaviside_delta
heaviside.delta_prime = heaviside_delta_prime

def fermi_dirac_matsubara(x, nmats=1000):
    """Calculate Fermi function as Matsubara sum."""

    inu = 1j * (2 * np.arange(nmats) + 1) * np.pi

    return 0.5 + 2 * np.sum(np.subtract.outer(inu, x) ** -1, axis=0).real

def fermi_dirac_matsubara_delta(x, nmats=1000):
    """Calculate negative derivative of Fermi function as Matsubara sum."""

    inu = 1j * (2 * np.arange(nmats) + 1) * np.pi

    return -2 * np.sum(np.subtract.outer(inu, x) ** -2, axis=0).real

def fermi_dirac_matsubara_delta_prime(x, nmats=1000):
    """Calculate negative 2nd derivative of Fermi function as Matsubara sum."""

    inu = 1j * (2 * np.arange(nmats) + 1) * np.pi

    return -4 * np.sum(np.subtract.outer(inu, x) ** -3, axis=0).real

fermi_dirac_matsubara.delta = fermi_dirac_matsubara_delta
fermi_dirac_matsubara.delta_prime = fermi_dirac_matsubara_delta_prime

def smearing(name='gaussian'):
    """Select smearing function via name used in Quantum ESPRESSO.

    Parameters
    ----------
    name : str, default 'gaussian'
        Any available option for PWscf input parameter ``smearing``.

    Returns
    -------
    function
        Smearing function.
    """
    name = name.lower()

    if name in {'gaussian', 'gauss'}:
        return gauss
    if name in {'methfessel-paxton', 'm-p', 'mp'}:
        return methfessel_paxton
    if name in {'marzari-vanderbilt', 'cold', 'm-v', 'mv'}:
        return marzari_vanderbilt
    if name in {'fermi-dirac', 'f-d', 'fd'}:
        return fermi_dirac
