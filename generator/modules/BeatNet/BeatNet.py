# Adapted from https://github.com/mjhydri/BeatNet
# Heydari, Mojtaba, Frank Cwitkowitz, and Zhiyao Duan. "BeatNet: CRNN and particle filtering for online joint beat downbeat and meter tracking." arXiv preprint arXiv:2108.03576 (2021).
# Modified by Raghavasimhan Sankaranarayanan on 10/02/2022

import os
from sunau import AUDIO_FILE_ENCODING_ADPCM_G723_5
import torch
import numpy as np
from madmom.features import DBNDownBeatTrackingProcessor
from .logSpect import LOG_SPECT
from .model import BDA


class BeatNet:
    def __init__(self, model: int = 1, sr: int = 22050, fps = 50, beats_per_bar = [2, 4]):
        self.model = model
        # self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        self.device = 'cpu'
        self.sr = sr
        self.log_spec_hop_length = int(20 * 0.001 * self.sr)
        self.log_spec_win_length = int(64 * 0.001 * self.sr)
        self.proc = LOG_SPECT(sample_rate=self.sr, win_length=self.log_spec_win_length,
                              hop_size=self.log_spec_hop_length, n_bands=[24])
        self.estimator = DBNDownBeatTrackingProcessor(beats_per_bar=beats_per_bar, fps=fps)

        script_dir = os.path.dirname(__file__)
        # assiging a BeatNet CRNN instance to extract joint beat and downbeat activations
        # Beat Downbeat Activation detector
        self.model = BDA(272, 150, 2, self.device)
        # loading the pre-trained BeatNet CRNN weigths
        if model == 1:  # GTZAN out trained model
            self.model.load_state_dict(torch.load(os.path.join(
                script_dir, 'models/model_1_weights.pt')), strict=False)
        elif model == 2:  # Ballroom out trained model
            self.model.load_state_dict(torch.load(os.path.join(
                script_dir, 'models/model_2_weights.pt')), strict=False)
        elif model == 3:  # Rock_corpus out trained model
            self.model.load_state_dict(torch.load(os.path.join(
                script_dir, 'models/model_3_weights.pt')), strict=False)
        else:
            raise RuntimeError(f'Failed to open the trained model: {model}')
        self.model.eval()
    
    def get_downbeats(self, audio: np.ndarray):
        # Using BeatNet causal Neural network to extract activations
        preds = self.activation_extractor(audio)
        # Using DBN offline inference to infer beat/downbeats
        output = self.estimator(preds)
        # beats gives an array [[beat, beat_number]] -> taking the first beat of each bar
        return output[output[:, 1] == 1].T[0]

    def activation_extractor(self, audio: np.ndarray):
        with torch.no_grad():
            if len(np.shape(audio)) > 1:
                audio = np.mean(audio, axis=1)
            
            feats = self.proc.process_audio(audio).T
            feats = torch.from_numpy(feats)
            feats = feats.unsqueeze(0).to(self.device)
            # extracting the activations by passing the feature through the NN
            preds = self.model(feats)[0]
            preds = self.model.final_pred(preds)
            preds = preds.cpu().detach().numpy()
            preds = np.transpose(preds[:2, :])
        return preds
