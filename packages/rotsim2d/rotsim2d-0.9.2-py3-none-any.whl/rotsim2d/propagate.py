"""Calculate N-dimensional time/frequency spectra.

**TODO:**

- refactor in terms of :class:`rotsim2d.dressedleaf.DressedPathway` and get rid
  of `pop` attribute in `KetBra`.
- add pressure and polarization dependence here
"""
import json
import logging
from collections import namedtuple
from pathlib import Path
from typing import Dict, Mapping, Optional, Sequence, Tuple, Union

import h5py
import numpy as np
import scipy.constants as C

import rotsim2d.dressedleaf as dl

e2i = C.epsilon_0*C.c/2         #: Electric field to intensity
xs2cm = 1e2/C.c                 #: Cross section in m^2 Hz to cm^2 cm^{-1}
ignore_missing = False          #: silently ignore dynamics of missing lines

log = logging.getLogger(__name__)


def aid(x):
    return x.__array_interface__['data'][0]


def pws_autospan(pws: Sequence[dl.NDResonance], margin: float=5.0*30e9,
                 conv: float=1.0) -> Tuple[Tuple[float, ...], ...]:
    """Return min/max pump/probe frequencies from ``pws``."""
    pump_freqs, probe_freqs = [pw.nu(0) for pw in pws], [pw.nu(2) for pw in pws]
    pump_min, pump_max = min(pump_freqs), max(pump_freqs)
    probe_min, probe_max = min(probe_freqs), max(probe_freqs)

    return ((pump_min*conv - margin,
             pump_max*conv + margin,
             2*margin + conv*(pump_max-pump_min)),
            (probe_min*conv - margin,
             probe_max*conv + margin,
             2*margin + conv*(probe_max-probe_min)))


def aligned_fs(fsmin: float, fsmax: float, df: float) -> np.ndarray:
    """Return smallest ``df``-spaced zero-offset grid of values covering [``fsmin``,
    ``fsmax``] range.
    """
    def align_max(f: float):
        return np.ceil(f/df).astype(np.int64)
    def align_min(f: float):
        return np.floor(f/df).astype(np.int64)

    fsmin, fsmax = sorted((fsmin, fsmax))
    if fsmin >= 0 and fsmax > 0:
        return np.arange(align_min(fsmin), align_max(fsmax)+1)*df
    elif fsmin < 0 and fsmax > 0:
        return np.arange(-(align_max(-fsmin)), align_max(fsmax)+1)*df
    elif fsmin < 0 and fsmax <= 0:
        return np.arange(-(align_max(-fsmin)), -align_min(-fsmax)+1)*df


def leaf_term(nu: float, gam: float, coord: np.ndarray, domain: str):
    r"""Return either time or frequency domain response.

    This uses the Fourier transform defined as:

    ..math::

        \mathcal{F}(f(t)) = \int_{-\infty}^{\infty} \mathrm{d}t\, f(t) e^{i\omega t}
    """
    if domain == 'f':
        return 1.0/(gam - 1.0j*(coord-nu))
    elif domain == 't':
        return np.exp(-2.0*np.pi*coord*(1.0j*nu+gam))


def dressed_leaf_response(dl: dl.NDResonance,
                          coords: Sequence[Optional[np.ndarray]],
                          domains: Sequence[str],
                          freq_shifts: Optional[Sequence[float]]=None,
                          angles: Optional[Sequence[float]]=None,
                          p: float=1.0) -> np.ndarray:
    """Calculate response for a single DressedLeaf."""
    # validate inputs
    if len(coords) != len(domains):
        raise ValueError("len(coords) != len(domains)")
    for d in domains:
        if d not in ('t', 'f'):
            raise ValueError("domain can either be 't' or 'f'")

    freq_shifts = freq_shifts or [0.0]*len(coords)
    resps = []
    for i, coord in enumerate(coords):
        if coord is None:
            continue

        if dl.nu(i) > 0.0:
            nu = dl.nu(i)-freq_shifts[i]
        elif dl.nu(i) < 0.0:
            nu = dl.nu(i)+freq_shifts[i]
        else:
            nu = dl.nu(i)

        resps.append(leaf_term(nu, dl.gamma(i)*p, coord, domains[i]))

    resp = resps[0]*dl.amplitude(angles=angles)
    if len(resps) > 1:
        for next_resp in resps[1:]:
            resp = resp*next_resp
    return resp


def run_mixed_axes(dpws: Sequence[dl.NDResonance],
                   params: Mapping) -> Tuple[np.ndarray, np.ndarray]:
    """Prepare mixed time/frequency axes ``params``."""
    pump_limits, probe_limits = (
        params['pump_limits'], params['probe_limits'])
    if 'f' in params['coords'] and (pump_limits == 'auto' or
                                    probe_limits == 'auto'):
        pumps, probes = pws_autospan(dpws)

    if params['coords'][0] == 'f':
        if pump_limits == 'auto':
            pump_limits = pumps[:2]
        else:
            pump_limits = [lim*C.c*100.0 for lim in pump_limits]
        d_pump = params['pump_step']*C.c*100.0
    else:
        pump_limits = [lim*1e-12 for lim in pump_limits]
        d_pump = params['pump_step']*1e-12

    if params['coords'][1] == 'f':
        if probe_limits == 'auto':
            probe_limits = probes[:2]
        else:
            probe_limits = [lim*C.c*100.0 for lim in probe_limits]
        d_probe = params['probe_step']*C.c*100.0
    else:
        probe_limits = [lim*1e-12 for lim in probe_limits]
        d_probe = params['probe_step']*1e-12

    ax_pu = aligned_fs(pump_limits[0], pump_limits[1], d_pump)
    ax_pr = aligned_fs(probe_limits[0], probe_limits[1], d_probe)

    return ax_pu, ax_pr


def run_propagate(dpws: Sequence[dl.NDResonance],
                  params: Mapping) -> Tuple[np.ndarray, ...]:
    """Calculate mixed time/frequency resposne."""
    ax_pu, ax_pr = run_mixed_axes(dpws, params)
    resp = np.zeros((ax_pu.size, ax_pr.size), dtype=np.complex128)
    for dl1 in dpws:
        resp[:, :] += dressed_leaf_response(
            dl1, [ax_pu[:, None], params['tw']*1e-12, ax_pr[None, :]],
            [params['coords'][0], 't', params['coords'][1]],
            p=params['pressure'],
            angles=params['angles'])

    return ax_pu, ax_pr, resp


def run_save(path: Union[str, Path],
             fs_pu: np.ndarray, fs_pr: np.ndarray, spec2d: np.ndarray,
             metadata: Mapping=None):
    """Save calculated 2D spectrum or time-domain response."""
    with h5py.File(path, mode='w') as f:
        f.create_dataset("pumps", data=fs_pu)
        f.create_dataset("probes", data=fs_pr)
        f.create_dataset("spectrum", data=spec2d)
        if metadata:
            f.attrs['metadata'] = json.dumps(metadata)


Spectrum2D = namedtuple("Spectrum2D",
                        ["pumps", "probes", "spectrum", "params"],
                        defaults=[None])

def run_load(path: Union[str, Path]):
    """Load calculated 2D spectrum."""
    with h5py.File(path, mode='r') as f:
        return Spectrum2D(
            f['pumps'][()], f['probes'][()], f['spectrum'][()],
            json.loads(f.attrs['metadata']))


def run_update_metadata_mixed(params: Dict) -> Dict:
    """Update `spectrum` metadata from file if needed."""
    with h5py.File(params['spectrum']['from_file'], 'r') as f:
        pumps = f['pumps'][()]
        probes = f['probes'][()]
        h5_params = json.loads(f.attrs['metadata'])

    # pump
    if params['spectrum']['coords'][0] == 'f':
        params['spectrum']['pump_limits'] = [pumps[0]/C.c/100.0,
                                             pumps[-1]/C.c/100.0]
        params['spectrum']['pump_step'] = (pumps[1]-pumps[0])/C.c/100.0
    elif params['spectrum']['coords'][0] == 't':
        params['spectrum']['pump_limits'] = [pumps[0]*1e12, pumps[-1]*1e12]
        params['spectrum']['pump_step'] = (pumps[1]-pumps[0])*1e12

    # probe
    if params['spectrum']['coords'][1] == 'f':
        if params['pathways']['direction'] == \
           h5_params['pathways']['direction']:
            params['spectrum']['probe_limits'] = [
                probes[0]/C.c/100.0, probes[-1]/C.c/100.0]
        else:
            params['spectrum']['probe_limits'] = [
                -probes[-1]/C.c/100.0, -probes[0]/C.c/100.0]
        params['spectrum']['probe_step'] = \
            abs((probes[1]-probes[0])/C.c/100.0)
    elif params['spectrum']['coords'][1] == 't':
        params['spectrum']['probe_limits'] = [
            probes[0]*1e12, probes[-1]*1e12]
        params['spectrum']['probe_step'] = (probes[1]-probes[0])*1e12

    # pressure
    params['spectrum']['pressure'] = h5_params['spectrum']['pressure']

    return params


def run_update_metadata(params: Dict) -> Dict:
    """Update `spectrum` metadata if needed.

    Tries to load frequency axis and pressure from `path` if
    `params['spectrum']['from_file']` contains a file name.
    """
    if "from_file" in params['spectrum'] and\
       params['spectrum']['from_file']:
        return run_update_metadata_mixed(params)
    else:
        return params


def time_integral(P: float, frep: float, w: float, tp: float) -> float:
    """Squared time-integral of the electric field at the peak.

    The pulse is `exp(-t**2/tp**2)`.

    Parameters
    ----------
    P
        Average power in W.
    frep
        Repetition rate.
    w
        Amplitude beam radius.
    tp
        Amplitude Gaussian pulse duration.
    """
    peak_fluence = 2*P/np.pi/w**2/frep
    E02 = 2*np.sqrt(2)/C.c/C.epsilon_0/np.sqrt(np.pi)/tp*peak_fluence
    ti = np.sqrt(E02)*np.sqrt(np.pi)*tp

    return ti


def conc(p: float, T: float, unit='Pa'):
    """Concentration in 1/m^3 from pressure and temp.

    Parameters
    ----------
    p
        Pressure
    T
        Temperature in K
    unit
        unit of pressure: 'Pa', 'Torr' or 'atm'
    """
    if unit == 'atm':
        p *= 101325
    elif unit == 'Torr':
        p *= 101325/760
    elif unit != 'Pa':
        raise ValueError("Unknown unit '{:s}'".format(unit))

    return p/C.k/T


def amp_to_abscoeff(amp2d: np.ndarray, probes: np.ndarray,
                    E12: float, conc: float) -> np.ndarray:
    """Convert pathway amplitude to abs. coeff. spectrum.

    Parameters
    ----------
    amp2d : np.ndarray
        2D spectrum as returned by :func:`dressed_leaf_response`.
    probes : np.ndarray
        Probe frequencies.
    E12 : float
        Product of field integrals of pump pulses.
    conc : float
        Concentration in 1/m**3.
    """
    return -np.imag(amp2d)*conc*E12*\
        2*np.pi*probes/C.c/C.epsilon_0/4.0
