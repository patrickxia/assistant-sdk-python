import io
import wave

try:
    from . import audio_helpers
except (SystemError, ImportError):
    # needs ffmpeg
    import audio_helpers

import speech_recognition as sr

from gtts import gTTS
from pydub import AudioSegment

class TextSource(audio_helpers.WaveSource):
    """Audio source that uses text to speech as the
    backing store.

    Silence is returned when there is no current text.
    Args:
      text: the initial text to read.
      sample_rate: sample rate in hertz.
      sample_width: size of a single sample in bytes.
    """
    def __init__(self, text, sample_rate, sample_width):
        self._text = text
        self._sample_rate = sample_rate
        self._sample_width = sample_width
        self._sleep_until = 0
        self._wavep = None

        if text:
            self.reset_text(text)

    def reset_text(self, text):
        self._text = text
        with io.BytesIO() as fp:
            tts = gTTS(text, 'en')
            tts.write_to_fp(fp)
            fp.seek(0)
            data = AudioSegment.from_mp3(fp)._data
            self._fp = io.BytesIO(data)

    def close(self):
        """Close the underlying stream."""
        pass

class TextSink(audio_helpers.WaveSink):
    def __init__(self, sample_rate, sample_width):
        self._sample_rate = sample_rate
        self._sample_width = sample_width

        self._r = sr.Recognizer()
        self.reset()

    def recognize(self):
        self._buf.seek(0)
        with sr.AudioFile(self._buf) as source:
            audio = self._r.record(source)
        text = self._r.recognize_google(audio)
        return text

    def reset(self):
        self._buf = io.BytesIO()
        super().__init__(self._buf, self._sample_rate, self._sample_width)


