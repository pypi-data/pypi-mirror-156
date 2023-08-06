# Imports used through the rest of the notebook.
import hashlib
from datetime import datetime

import torchaudio

from ruth_tts_transformer.ruth_tts.api import TextToSpeech
from ruth_tts_transformer.ruth_tts.utils.audio import load_voice


class TTS:
    def __init__(self):
        self.gen = None
        self.preset = "ultra_fast"
        self.voice = "hendry"
        self.tts = TextToSpeech()

    def generate(self, text):
        voice_samples, conditioning_latents = load_voice(self.voice)
        gen = self.tts.tts_with_preset(text, voice_samples=voice_samples, conditioning_latents=conditioning_latents,
                                       preset=self.preset)
        self.gen = gen

    def parse(self):
        file_name = hashlib.sha1(str(datetime.now()).encode("UTF-8"))
        torchaudio.save(file_name.hexdigest() + '.wav', self.gen.squeeze(0).cpu(), 24000)
        return file_name.hexdigest()
