import os
import pandas as pd
import numpy as np
import scipy as sp
from scipy.signal import butter, filtfilt
import joblib
import random
from scipy.stats import skew, kurtosis, entropy
import pywt
import matplotlib.pyplot as plt

class Detector:
    def __init__(self):
        self.model = joblib.load(os.getcwd() + "/api_detector/models/data/model.joblib")
        self.scaler = joblib.load(os.getcwd() + "/api_detector/models/data/scaler.joblib")

    # Function to create a bandpass filter
    def butter_bandpass(self, lowcut, highcut, fs, order=5):
        nyquist = 0.5 * fs
        low = lowcut / nyquist
        high = highcut / nyquist
        b, a = butter(order, [low, high], btype='band')
        return b, a

    # Function to apply the bandpass filter
    def bandpass_filter(self, data, lowcut, highcut, fs, order=5):
        b, a = self.butter_bandpass(lowcut, highcut, fs, order=order)
        y = filtfilt(b, a, data)
        return y

    def extract_features(self, segment):
        features = {}
        velocities = segment['velocity(m/s)'].values
        times = segment['time_rel(sec)'].values
        accelerations = segment['acceleration'].values
        fft_magnitudes = segment['fft_magnitude'].values
        filtered_velocities = segment['filtered_velocity'].values

        # Statistical Features
        features['vel_mean'] = np.mean(velocities)
        features['vel_std'] = np.std(velocities)
        features['vel_var'] = np.var(velocities)
        features['vel_skew'] = skew(velocities)
        features['vel_kurtosis'] = kurtosis(velocities)

        features['acc_mean'] = np.mean(accelerations)
        features['acc_std'] = np.std(accelerations)
        features['acc_var'] = np.var(accelerations)
        features['acc_skew'] = skew(accelerations)
        features['acc_kurtosis'] = kurtosis(accelerations)

        # Frequency-Domain Features
        features['fft_mean'] = np.mean(fft_magnitudes)
        features['fft_std'] = np.std(fft_magnitudes)
        features['fft_max'] = np.max(fft_magnitudes)
        features['fft_min'] = np.min(fft_magnitudes)

        # Peak Features
        features['vel_max'] = np.max(velocities)
        features['vel_min'] = np.min(velocities)
        features['acc_max'] = np.max(accelerations)
        features['acc_min'] = np.min(accelerations)

        # Zero-Crossing Rate
        zero_crossings = np.where(np.diff(np.sign(velocities)))[0]
        features['zero_crossing_rate'] = len(zero_crossings) / len(velocities)

        # Energy of the signal
        features['signal_energy'] = np.sum(velocities ** 2)

        # Entropy Features
        features['vel_entropy'] = entropy(np.abs(velocities))
        features['acc_entropy'] = entropy(np.abs(accelerations))

        # Spectral Entropy
        psd = np.abs(np.fft.fft(velocities)) ** 2
        psd_norm = psd / np.sum(psd)
        features['spectral_entropy'] = entropy(psd_norm)

        # Wavelet Transform Features
        coeffs = pywt.wavedec(velocities, 'db4', level=5)
        for i, coeff in enumerate(coeffs):
            features[f'wavelet_coeff_mean_{i}'] = np.mean(coeff)
            features[f'wavelet_coeff_std_{i}'] = np.std(coeff)
            features[f'wavelet_coeff_energy_{i}'] = np.sum(coeff ** 2)

        return features

    def predict(self, data):

        # An array of tuples is expected, where each tuple contains the time_rel(sec) and velocity(m/s) values
        data = pd.DataFrame(data, columns=['time_rel(sec)', 'velocity(m/s)'])

        # Compute acceleration
        data['acceleration'] = np.gradient(data['velocity(m/s)'], data['time_rel(sec)'])

        # FFT of velocities
        velocities = data['velocity(m/s)'].values
        fft_values = np.fft.fft(velocities)
        fft_magnitudes = np.abs(fft_values)
        data['fft_magnitude'] = fft_magnitudes

        # Bandpass filter
        low_freq = 0.5
        high_freq = 1.0
        sampling_rate = 6
        order = 4
        data['filtered_velocity'] = self.bandpass_filter(data['velocity(m/s)'].values, low_freq, high_freq, sampling_rate, order)

        # Extract features
        features = self.extract_features(data)

        # Scale features
        X_new = pd.DataFrame([features])

        # Scaled for model 5
        X_new_scaled = self.scaler.transform(X_new)

        # Predict
        y_proba = self.model.predict_proba(X_new_scaled)
        threshold = 0.5
        y_pred = (y_proba[:, 1] > threshold).astype(int)

        if y_pred == 0:
            return False, -1
        else:
            peaks, _ = sp.signal.find_peaks(data['velocity(m/s)'], height=np.percentile(data['velocity(m/s)'], 99), distance=50)

            peak_groups = []

            for peak in peaks:
                if not peak_groups:
                    peak_groups.append([peak])
                else:
                    if peak - peak_groups[-1][-1] < 300:
                        peak_groups[-1].append(peak)
                    else:
                        peak_groups.append([peak])

            peak_group = max(peak_groups, key=len)

            peak = peak_group[0]
            peak_before = peak - 750 if peak - 750 > 0 else 0

            peak_time = data['time_rel(sec)'].iloc[peak_before]

            return True, peak_time
