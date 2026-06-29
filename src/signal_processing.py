import numpy as np
import librosa
import scipy.integrate as integrate
from scipy.interpolate import PchipInterpolator

def apply_filter(mel_specgram, filt_weights):
    """_summary_

    Args:
        mel_specgram (_type_): _description_
        filt_weights (_type_): _description_

    Returns:
        _type_: _description_
    """
    # applies to a power spectrogram S (not on a dB/log scale)
    filtered_mel_specgram = mel_specgram * (
        np.tile(filt_weights, (mel_specgram.shape[1], 1)).T
    )
    return filtered_mel_specgram



def get_energy(
    spectrum: PchipInterpolator,
    f_min: int,
    f_max: int,
    A_weighting=False,
    verbose=False,
):
    """Compute the total power/energy of the function with given spectrum between f_min and f_max.
    Using Pa units, maybe not a good idea for numerical integration (dB SPL use 20micropascal as ref)

    Args:
        spectrum (PchipInterpolator): spectrum: f -> e(f) magnitude spectrum in dB SPL at frequency f (in Hz)
        f_min (int): lower integration bounds (in Hz)
        f_max (int): upper integration bounds (in Hz)
        A_weighting (bool, optional): whether to use A-weighting. Defaults to False.
        verbose (bool, optional): _description_. Defaults to False.

    Returns:
        _type_: _description_
    """
    if A_weighting:
        fun = lambda f: librosa.db_to_power(
            spectrum(f) + librosa.A_weighting(f), ref=0.000020
        )
    else:
        fun = lambda f: librosa.db_to_power(spectrum(f), ref=0.000020)
    total_energy, abs_err = integrate.quad(
        fun, f_min, f_max, limit=1000000, epsabs=1e-06, epsrel=1e-06
    )
    if verbose:
        abs_err_dB = librosa.power_to_db(abs_err, ref=0.000020)
        print(
            f"scipy.integrate.quad estimate of absolute integration error {abs_err} Pa or {abs_err_dB} dB SPL"
        )
    total_energy_dB = librosa.power_to_db(total_energy, ref=0.000020)
    return total_energy_dB

def one_third_octave_powers_to_spectral_densities(oto_center_frequencies, oto_powers):
    return oto_powers-10*np.log10((2**(1/6)-2**(-1/6))*oto_center_frequencies)

def apply_system(
    input_signal_spectrum: PchipInterpolator, gain_function: PchipInterpolator
):
    # apply linear system to input signal
    # - arguments
    #  - input_signal_spectrum: f -> i(f) input magnitude spectrum in dB SPL at frequency f (in Hz)
    #  - gain_function: f -> g(f) system gain in dB SPL at frequency f (in Hz)
    # - output: output_signal_spectrum : f -> o(f) output magnitude spectrum in dB SPL at frequency f (in Hz)
    def output_signal_spectrum(f):
        return input_signal_spectrum(f) + gain_function(f)

    return output_signal_spectrum

def compute_fmin_fmax(freqs_paper, freqs_LTASS):
    fmin = max(min(freqs_paper), min(freqs_LTASS)) + 1
    fmax = min(max(freqs_paper), max(freqs_LTASS)) - 1
    return fmin, fmax

def compute_overall_attenuation(spectrum_speech, attenuated_spectrum_speech, fmin, fmax, A_weighting=False):
    e_in = get_energy(spectrum_speech, fmin, fmax, verbose=False)
    e_out = get_energy(attenuated_spectrum_speech, fmin, fmax, verbose=False, A_weighting=A_weighting)
    total_energy_attenuation = e_in-e_out  # in dB SPL
    return total_energy_attenuation 