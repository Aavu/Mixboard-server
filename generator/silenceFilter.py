###
# Created by Raghavasimhan Sankaranarayanan on 10/01/22.
###

import numpy as np
from . import utils
from numba import njit, prange


class SilenceFilter:
    def __init__(self, downbeats, threshold: float, bar_lengths: list = [4, 8, 16, 32], lpf_alpha: float = 0.9999,
                 block_size: int = 4096, hop_size: int = 4096,
                 hole_th: int = 30, med_th: int = 50):
        self.__downbeats = downbeats
        self.__silence_th = threshold
        self.__bar_lengths = np.unique(bar_lengths)

        self.__block = block_size
        self.__hop = hop_size
        self.__hole_th = hole_th
        self.__med_th = med_th
        self.__a = lpf_alpha

    # @njit
    def get_non_silent_bounds(self, stem: np.ndarray, fs: int = 44100) -> dict:
        bounds = {}
        th, env = self.__detect_silence_core(stem, self.__block, self.__hop, self.__hole_th, self.__med_th, self.__a)
        blobs = self.__get_silence_blobs(th, self.__downbeats, self.__silence_th, fs)

        for _l in self.__bar_lengths:
            bounds[str(_l)] = []

        num_bars = 0
        for i in prange(len(blobs)):
            num_bars += blobs[i]
            if blobs[i] == 0:
                num_bars = 0
                continue

            for _l in self.__bar_lengths:
                if num_bars >= _l and num_bars % _l == 0:
                    id = i - _l + 1
                    bounds[str(_l)].append(self.__downbeats[id])

        return dict(bounds)

    @staticmethod
    @njit
    def __get_silence_blobs(activations, downbeats, threshold, fs):
        blobs = np.zeros(len(downbeats) - 1)

        for i in prange(len(downbeats) - 1):
            ss = int(downbeats[i] * fs)
            se = int(downbeats[i + 1] * fs)
            act = activations[ss:se]
            blobs[i] = int(not utils.is_silent(act, threshold))

        return blobs

    @staticmethod
    @njit
    def __fill_holes(samples, th):
        out = np.copy(samples).astype(np.float64)
        last_idx = 0
        for i in range(1, len(out)):
            if out[i - 1] - out[i] > 0:
                last_idx = i - 1
            elif out[i] - out[i - 1] > 0:
                if (i - last_idx) < th:
                    out[last_idx:i] = 1

        return out

    @staticmethod
    @njit
    def __envelope(samples, block, hop, a=0.999):
        out = np.zeros(((len(samples) - block + 1) // hop) + 1)
        x_ = np.abs(samples)

        for i in range(1, len(x_)):
            x_[i] = (a * x_[i - 1]) + ((1 - a) * x_[i])

        for i in range(len(x_) - 2, -1, -1):
            x_[i] = (a * x_[i + 1]) + ((1 - a) * x_[i])

        for i in range(len(out)):
            idx = (i * hop)
            out[i] = np.max(x_[idx:idx + block])

        return out

    @staticmethod
    @njit
    def __med_filt(samples, kernel):
        out = np.zeros_like(samples, dtype=np.float64)
        temp = out[:kernel // 2]
        for i in range(len(samples) - kernel):
            out[i:i + kernel] = np.median(samples[i:i + kernel])

        out[out > 0] = 1
        out = np.roll(out, kernel // 2)  # correct for the filter shift
        out[:kernel // 2] = temp  # Bring back initial values lost form median filtering
        return out

    @staticmethod
    # @njit
    def __detect_silence_core(samples: np.ndarray, block, hop, hole_th, med_th, a):

        out_th = np.zeros_like(samples)
        out_env = np.zeros_like(samples)

        if len(samples) == 0:
            print("WARNING: Array empty. Not detecting silence")
            return out_th, out_env

        _env = SilenceFilter.__envelope(samples, block, hop, a)
        _th = np.zeros_like(_env)
        th = np.sqrt(np.mean(np.square(_env))) / 1.5
        _th[_env > th] = 1
        _th = SilenceFilter.__fill_holes(_th, hole_th)
        _th = SilenceFilter.__med_filt(_th, med_th)

        for i in prange(len(_env)):
            out_th[i * hop: (i + 1) * hop] = _th[i]
            out_env[i * hop: (i + 1) * hop] = _env[i]

        return out_th, out_env
