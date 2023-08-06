from curses import use_default_colors
from curses.panel import bottom_panel
import os
import pdb
from loguru import logger as log
import traceback
from pandas import DataFrame
import numpy as np
from dycifer.read import readSignals
from dycifer.utils import plotPrettyFFT
from modelling_utils import stof, timer


def mixedSignalsDynamicEval(subparser, *args, **kwargs):
    import warnings

    warnings.filterwarnings("ignore")  # supress pandas warnings
    """_summary_
    Dynamic performance evaluation of Mixed Signals circuits
    """
    argv = None
    # read data
    sysargs = args[0]
    try:
        argv = subparser.parse_args(sysargs[1:])
    except Exception as e:
        log.error(traceback.format_exc())
    # from the signals argument (containing the signals file filepath)
    # extract the signals
    signals = readSignals(argv.signals[0])
    if argv.analog_to_digital:
        sampling_freq = stof(
            argv.sampling_frequency[0]
        )  # convert the parsed string to a float
        res = argv.bit_resolution[0] if bool(argv.bit_resolution) else -1
        v_source = argv.voltage_source[0] if bool(argv.voltage_source) else 1.0
        harmonics = argv.harmonics[0] if bool(argv.harmonics) else 7
        signal_span = argv.signal_span[0] if bool(argv.signal_span) else 0.0
        noise_power = argv.noise_power[0] if bool(argv.noise_power) else -1.0
        # pdb.set_trace()
        # perform dynamic performance evaluation
        (
            spectrum,
            target_harmonics,
            signal_power,
            dc_power,
            sfdr,
            thd,
            snr,
            sndr,
            enob,
            hd2,
            hd3,
        ) = adcDynamicEval(
            signals,
            sampling_freq,
            n_bits=res,
            v_source=v_source,
            harmonics=harmonics,
            signal_span_factor=signal_span,
            asceding_bit_order=argv.ascending,
            noise_power=noise_power,
        )
        # prepare to plot resulting information
        dynamic_eval_indicators = DataFrame(
            data={
                "Signal Power (dB)": signal_power,
                "DC Power (dB)": dc_power,
                "SFDR (dB)": sfdr,
                "THD (dB)": thd,
                "SNR (dB)": snr,
                "SNDR (dB)": sndr,
                "ENOB": enob,
                "HD2 (dB)": hd2,
                "HD3 (dB)": hd3,
            },
            index=["Dynamic Evaluation Indicators"],
        )
        if argv.plot:
            plotPrettyFFT(
                spectrum[
                    spectrum.index.values >= 0
                ].index,  # plot only positive frequencies spectrum
                spectrum[spectrum.index.values >= 0]["power_db"],
                title="Signal Spectrum (dB)",
                xlabel="Frequency (GHz)",
                ylabel="Power (dB)",
                show=True,
                target_harmonics=target_harmonics,
                plot_to_terminal=argv.plot_to_terminal,
                xscale="G",
            )
        if bool(argv.output_file):
            plotPrettyFFT(
                spectrum[
                    spectrum.index >= 0
                ].index,  # plot only positive frequencies spectrum
                spectrum[spectrum.index.values >= 0]["power_db"],
                title="Signal Spectrum (dB)",
                xlabel="Frequency (GHz)",
                ylabel="Power (dB)",
                show=False,
                file_path=argv.output_file[0] + ".png",
                target_harmonics=target_harmonics,
                xscale="G",
            )
            if argv.generate_table:
                tablename = argv.output_file[0]
                dynamic_eval_indicators.to_csv(tablename + ".csv")
                dynamic_eval_indicators.to_json(tablename + ".json")
                dynamic_eval_indicators.to_markdown(tablename + ".md")
                dynamic_eval_indicators.to_latex(tablename + ".tex")
        # print indicators to console
        print()
        print(dynamic_eval_indicators.T)
    elif bool(argv.digital_to_analog):
        raise NotImplementedError("digital_to_analog: Not implemented yet.")
    elif bool(argv.sigma_delta_adc):
        raise NotImplementedError("sigma_delta_adc: Not implemented yet.")
    elif bool(argv.sigma_delta_dac):
        raise NotImplementedError("sigma_delta_dac: Not implemented yet.")
    else:
        raise ValueError(
            "No mixed-signals system class was specified was specified. Missing --analog-to-digital, --digital-to-analog, --sigma-delta-adc or --sigma-delta-dac."
        )
    print("\nPerformance evaluation finished.")
    return


@timer
def adcDynamicEval(
    signals: DataFrame,
    f_sampling: float,
    n_bits: int = -1,
    v_source: float = 1.0,
    harmonics: int = 7,
    signal_span_factor: float = 0.0,
    asceding_bit_order: bool = False,
    noise_power: float = -1.0,
) -> tuple[DataFrame, float, float, float, float, float, float, float]:
    print("\nPerforming Dynamic performance evaluation of ADC...")
    """_summary_
    Dynamic performance evaluation of Analog-to-Digital Converter circuits
    Args:
        signals (DataFrame): The signals corresponding to each of the bits generated by the ADC to be analysed.
        NOTE: signals can either be:
            - dataframe with index = time axis, and columns = digital word (in decimal, from 0 to 2^n_bits-1)
            - dataframe with index = time axis, and columns = rectangular signals corresponding to each bit of the digital word
        time_col (bool, optional): If True, the csv file is assume to have a time column. Otherwise, time column is not present.
        f_sampling (float, optional): The sampling frequency (in Hertz (Hz)) corresponding to the resolution of each signal sample. Defaults to 0.0
        v_source (float, optional): The voltage source used to feed the ADC, establishing the bottom and top voltage level decks. Defaults to 1.0 V
        n_bits (int, optional): The number of bits (resolution) of the ADC. Defaults to -1.
        harmonics (int, optional): The number of harmonics considered in the analysis of the harmonic distortion of the ADC. Defaults to 7.
        singal_span_factor (float, optional): Percentual factor determining how much of the signal's
                                                power is dispersed onto the remanescent spectrum of the signal's spectrum. Defaults to 0.0
        ascending_bit_order (bool, optional): When parsing bit signals (and not output word), indicate if the columns of each bit (in the signals dataframe)
                                                are in ascending or descending order. Defaults to False.
        noise_power (float, optional):Artificially added noise power (in dBm) to the signal. Defaults to -1.0
    Returns:
        tuple(DataFrame, float(1), float(2), float(3), float(4), float(5), float(6), float(7)):
            DataFrame: The frequency spectrum of the ADC's output signal in volt, volt squared (power) and decibels.
            float(1): Signal's power in decibels
            float(2): Signal's DC power
            float(3): Spurious Free Dynamic Range metric
            float(4): Total Harmonic Distortion metric
            float(5): Signal to Noise Ratio metric
            float(6): Signal to Noise & Distortion Ratio metric
            float(7): Effective Number of Bits (effective ADC resolution) metric
    """

    # extract the sampling frequency from the function inputs
    ts = 1.0 / f_sampling
    fs = f_sampling
    downsampling = 1
    if bool(signals.index.name):
        downsampling = int(
            round(
                (1.0 / f_sampling) / (signals.index.values[1] - signals.index.values[0])
            )
        )
        if downsampling < 1:
            raise ValueError(
                "Sampling time period must be equal or higher than the signals' time resolution."
            )
    else:
        # in case there is no time axis frame
        # automatically generate one from the sampling frequency
        t = np.arange(0, len(signals) * ts, ts)
        signals.set_index(t, inplace=True)

    # downsample the signals to the sampling frequency effectively parsed as input
    signals = signals[::downsampling]
    """
    * ***********************************************************************************
    * * If the resolution of the ADC was parsed as input, it is assumed that the signals
    * * data frame already contains the constructed dout decimal words.
    * ***********************************************************************************
    """
    if n_bits > 0 and len(signals.columns) > 1:
        raise ValueError(
            f"The number of bits was provided as input, but the signals data frame does not present the constructed digital output word of the ADC. Expected {1} signal, found {len(signals.columns)} signals."
        )
    # extract the number of bits of the ADC
    resolution = n_bits if n_bits > 0 else len(signals.columns)
    # v_step = v_source / ((2 ** resolution)-1)

    """
    * ***********************************************************************************
    * * Compute the Dout signal if no resolution is provided as input, otherwise
    * * the Dout signal is already available in the signals DataFrame in the required format
    * ***********************************************************************************
    """
    # compute the Dout signal for each row of the signals DataFrame
    dout = signals[signals.columns].copy()
    vsource = v_source
    if n_bits < 0:
        # find the average value for the signals
        means = {}
        maxis = []
        minies = []
        for col in signals.columns:
            means[col] = signals[col].mean()
            maxis.append(signals[col].max())
            minies.append(signals[col].min())

        vsource = max(maxis) + min(minies)

        for col in dout.columns:
            dout[col][dout[col] <= means[col]] = 0
            dout[col][dout[col] > means[col]] = 1

        def join_bits(row):
            if not asceding_bit_order:
                return "".join(map(lambda b: str(int(b)), row.values))
            else:
                return "".join(map(lambda b: str(int(b))), np.flipud(row.values))

        dout["bin_word"] = dout.apply(join_bits, axis=1)
        dout["dec_word"] = dout["bin_word"].apply(lambda bin: int(bin, 2))
        # recenter the decoded word in 0 and scale it to [-1; +1]
        dout["vout"] = dout["dec_word"] / (2**resolution - 1) * 2 - 1.0
        dout["vout"] = dout["vout"] * vsource
    else:
        dout["vout"] = dout[dout.columns] / (2**resolution - 1) * 2 - 1.0
        dout["vout"] = dout["vout"] * vsource
    if noise_power > 0:
        noise_watt = (10 ** (noise_power / 10)) * 1e-3
        dout["vout"] = dout["vout"] + np.random.normal(
            0, np.sqrt(noise_watt), size=len(dout)
        )
    dout = dout["vout"]
    n_samples = len(dout)
    """
    * ***********************************************************************************
    * * Fast Fourier Transform (FFT) of the Dout Signal
    * ***********************************************************************************
    """
    vout = np.abs(np.fft.fftshift(np.fft.fft(dout.values) / n_samples))  # [V]
    freq = np.fft.fftshift(np.fft.fftfreq(n_samples, ts))  # [Hz]
    power = (
        vout * vout
    )  # [V^2] - square the voltage spectrum to obtain the power spectrum
    power_db = 10 * np.log10(power)  # [dB] - convert the power spectrum to dB
    spectrum = DataFrame(
        index=freq, data={"vout": vout, "power": power, "power_db": power_db}
    )
    # positive frequencies spectrum
    pspectrum = spectrum[spectrum.index >= 0].copy()
    """
    * ***********************************************************************************
    * * Computation of :
    * * SFDR - Spurious Free Dynamic Range
    * * THD - Total Harmonic Distortion
    * * SNR - Signal to Noise Ratio
    * * SNDR - Signal to Noise and Distortion Ratio
    * * ENOB - Effective Number Of Bits
    * * INL - Integral Non-Linearity (TODO)
    * * DFL - Differential Non-Linearity (TODO)
    * ***********************************************************************************
    """
    # ********************************************
    # Obtaining the ADC's output signal power
    # ********************************************
    # determine the span of the signal's spectrum to consider it's total dispersed power
    span = np.max([1, int(np.floor(signal_span_factor * len(pspectrum.index)))])
    # obtain the signal frequency bin
    signal_bin = pspectrum["power"][
        0 + span :
    ].idxmax()  # don't count DC signal when searching for the signal bin
    # obtain the harmonics of the signal from the signal bin
    harmonic_bins = [
        pspectrum.index[
            np.abs(pspectrum.index - (mult * signal_bin))
            == np.min(np.abs(pspectrum.index - (mult * signal_bin)))
        ][0]
        for mult in range(1, harmonics + 1)
        if mult * signal_bin <= np.max(freq)
    ]
    # tones that surpass Fs are aliased back to [0, Fs/2] spectrum
    harmonic_bins = [
        pspectrum.index[
            np.abs(pspectrum.index - (fs - bin))
            == np.min(np.abs(pspectrum.index - (fs - bin)))
        ][0]
        if bin > fs / 2
        else bin
        for bin in harmonic_bins
    ]
    # indexes of the harmonic bins
    harmonic_bins_idxs = [pspectrum.index.get_loc(bin) for bin in harmonic_bins]
    harmonics_power = np.array(
        [
            np.sum(
                pspectrum["power"]
                .iloc[harmonic_bin_idx - span : harmonic_bin_idx + span]
                .values
            )
            for harmonic_bin_idx in harmonic_bins_idxs
        ]
    )
    # obtain the signal_power

    signal_power = harmonics_power[0]
    SIGNAL_POWER_DB = 10 * np.log10(signal_power)
    signal_dc_power = np.sum(pspectrum["power"].iloc[0 : 0 + span].values)
    DC_POWER_DB = 10 * np.log10(signal_dc_power)
    # ********************************************
    # Computing SFDR - Spurious Free Dynamic Range
    #  - Obtain the power of the
    #       strongest spurious component
    #       of the spectrum (excluding the
    #       DC component) and compute the SFDR.
    # ********************************************
    signal_bin_idx = harmonic_bins_idxs[0]  # get the index of the signal bin
    spurious_spectrum = pspectrum["power"].copy()
    # erase the signal bin from the spurious spectrum
    spurious_spectrum.iloc[signal_bin_idx - span : signal_bin_idx + span] = np.min(
        pspectrum["power"]
    )
    # erase the signal's DC component from the spurious spectrum
    spurious_spectrum.iloc[0 : 0 + span] = np.min(pspectrum["power"])
    # find the strongest spurious component
    spur_bin = spurious_spectrum.idxmax()
    spur_bin_idx = pspectrum.index.get_loc(spur_bin)
    # measure the power of the strongest spurious component
    spur_power = np.sum(
        spurious_spectrum.iloc[spur_bin_idx - span : spur_bin_idx + span].values
    )
    # compute the SFDR
    SFDR = 10 * np.log10(signal_power / spur_power)
    # ********************************************
    # Computing THD - Total Harmonic Distortion
    #  - Obtain the power of each harmonic component
    # ********************************************
    # compute the total power of the sum of the harmonics
    THD = np.nan
    SNR = np.nan
    SNDR = np.nan
    ENOB = np.nan
    HD2 = np.nan
    HD3 = np.nan
    try:
        total_distortion_power = np.sum(harmonics_power[1:])
        THD = 10 * np.log10(total_distortion_power / harmonics_power[0])
        # ********************************************
        # Computing SNR - Signal to Noise Ratio
        #  - Obtain the noise power in the spectrum
        # ********************************************
        noise_power = (
            np.sum(pspectrum["power"].values)
            - signal_dc_power
            - signal_power
            - total_distortion_power
        )
        SNR = 10 * np.log10(signal_power / noise_power)
        # ********************************************
        # Computing SNDR - Signal to Noise & Distortion Ratio
        #  - Add the noise and distortion power in
        #     the spectrum and compare them to the
        #     signal power
        # ********************************************
        SNDR = 10 * np.log10(signal_power / (noise_power + total_distortion_power))
        # ********************************************
        # Computing ENOB - Effective Number of Bits
        #  - Check deterioration of the ADC's
        #    ideal resolution because of the SNDR
        # ********************************************
        ENOB = (SNDR - 1.76) / 6.02
        # ********************************************
        # Computing HD2 and HD3 - Fractional Harmonic
        # Distortion of Second and Third order
        # harmonics
        # ********************************************
        HD2 = 10 * np.log10(harmonics_power[1] / harmonics_power[0])
        HD3 = 10 * np.log10(harmonics_power[2] / harmonics_power[0])
    except IndexError:
        log.warning(
            f"\nTried to access an harmonic that was not found in the frequency domain of the analysed spectrum.\nThis is likely due to the fact that the chosen sampling frequency is \nviolating the Nyquist Theorem in relation to the 2nd or 3rd Order Harmonics.\nTry to increase the sampling frequency."
        )
    target_harmonics = list(zip(harmonic_bins, 10 * np.log10(harmonics_power)))
    return (
        spectrum,
        target_harmonics,
        SIGNAL_POWER_DB,
        DC_POWER_DB,
        SFDR,
        THD,
        SNR,
        SNDR,
        ENOB,
        HD2,
        HD3,
    )


def dacDynamicEval(subparser, *args, **kwargs):
    """_summary_
    Dynamic performance evaluation of Digital-to-Analog Converter circuits
    """
    raise NotImplementedError("dacDynamicEval: Not implemented yet.")


def sigmaDeltaAdcDynamicEval(*args, **kwargs):
    """_summary_
    Dynamic evaluation of Sigma Delta Analog-to-Digital Converter circuits
    Raises:
        NotImplementedError: _description_
    """
    raise NotImplementedError("sigmaDeltaAdcDynamicEval: Not implemented yet")


def sigmaDeltaDacDynamicEval(*args, **kwargs):
    """_summary_
    Dynamic evaluation of Sigma Delta Analog-to-Digital Converter circuits
    Raises:
        NotImplementedError: _description_
    """
    raise NotImplementedError("sigmaDeltaAdcDynamicEval: Not implemented yet")
