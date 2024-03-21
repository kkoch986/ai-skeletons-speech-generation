import time
import threading
from pydub import AudioSegment
from elevenlabs import generate, save, set_api_key, voices

class Generator:
    """
        generate should generate the audio and write an mp3 and wav file
        based on the baseFileName and returns the duration in seconds of
        the generated audio
    """
    def generate(self, baseFileName: str, voiceID: str, text: str) -> float:
        raise NotImplementedError()

    """
        getVoiceID will return the voiceID for the provided voice name
    """
    def getVoiceID(self, voiceName: str) -> str:
        raise NotImplementedError()

"""
    ElevenLabsGenerator uses the ElevenLabs API to generate speech audio
"""
class ElevenLabsGenerator(Generator):
    def __init__(self, token):
        set_api_key(token)

    def generate(self, baseFileName: str, voiceID: str, text: str) -> float:
        mp3File = baseFileName + ".mp3"
        wavFile = baseFileName + ".wav"
        audio = generate(text=text, voice=voiceID)
        save(audio, mp3File)
        sound = AudioSegment.from_mp3(mp3File)
        sound.export(wavFile, format="wav", parameters=["-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000"])
        return sound.duration_seconds

    def getVoiceID(self, voiceName: str) -> str:
        for v in voices():
            if v.name == voiceName:
                return v.voice_id
        raise ValueError("unable to locate voice name " + voiceName)

"""
    FestivalGenerator will use a locally installed instance of festival to generate
    speech audio.
    see: http://www.cstr.ed.ac.uk/projects/festival/
    see: https://github.com/techiaith/pyfestival/tree/master
"""
class FestivalGenerator(Generator):
    # TODO: add more configurables for this
    def __init__(self):
        pass

    def generate(self, baseFileName: str, voiceID: str, text: str) -> float:
        # kinda hacky but the festival library freaks out if its run from 2 different threads
        # couldnt really figure out something that worked until i hit on this :shrug:
        def generate():
            import festival
            tmpFile = festival.textToWavFile("this is a test of festival")
            # TODO: remove the tmpFile
            print(tmpFile)
            AudioSegment.from_wav(tmpFile).export(baseFileName + ".wav", format="wav", parameters=["-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000"])
            AudioSegment.from_wav(tmpFile).export(baseFileName + ".mp3", format="mp3", bitrate="128k", parameters=["-r", "44100"])
            del festival
        t1 = threading.Thread(target=generate)
        t1.start()
        t1.join()

    def getVoiceID(self, voiceName: str) -> str:
        # TODO: support changing the voice name
        return voiceName
