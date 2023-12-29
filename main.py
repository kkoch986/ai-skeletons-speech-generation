#!/usr/bin/env python3
from allosaurus.app import read_recognizer
from elevenlabs import generate, save, set_api_key, voices
from os import path
from pydub import AudioSegment
import csv
import json
import os
import sys
import time
import argparse
import base64
from tabulate import tabulate
from flask import Flask, json, request, abort
from urllib.parse import parse_qs

cli = argparse.ArgumentParser(
        prog='SkeletonSpeechGenerator',
        description='Generates audio and timestamped phonemes for use in automatically generating animatronic skeleton speech. This can be used in conjunction with the chatainge module to dynamically control skeletons')

subparsers = cli.add_subparsers(dest="subcommand")

# some plumbing so we can create a clean CLI interface
# taken mostly from https://mike.depalatis.net/blog/simplifying-argparse.html
def argument(*name_or_flags, **kwargs):
    return ([*name_or_flags], kwargs)
def subcommand(args=[], parent=subparsers):
    def decorator(func):
        parser = parent.add_parser(func.__name__, description=func.__doc__)
        for arg in args:
            parser.add_argument(*arg[0], **arg[1])
        parser.set_defaults(func=func)
    return decorator

#############################################
# api will start up an API server which can
# be used to generate metadatas
############################################
@subcommand()
def api(args = [], parent=subparsers):
    set_api_key(os.environ.get("ELEVENLABS_TOKEN"))
    api = Flask(__name__)

    # create a map of the allophones to phonemes
    print("loading phonemes mappings...")
    phonemeMap = alloToPhoneme()

    # load the english model
    print("loading phonemes model...")
    model = read_recognizer('eng2102')

    @api.route('/test', methods=['POST'])
    def test():
        time.sleep(2)
        with open('last.json', 'r') as openfile:
            json_object = json.load(openfile)
        return json_object

    @api.route('/generate', methods=['POST'])
    def generate():
        args = parse_qs(request.get_data(cache=False, as_text=True))
        print(args)
        voiceName = args['voiceName'][0]
        voiceID = args.get('voiceID', [None])[0]
        text = args['text'][0]
        outputName = args['name'][0]
        emitRatio = 0.7 # TODO: make this an arg too

        if text == "" or text == None:
            print("no text provided, aborting")
            abort(400)

        if voiceID == None:
            voiceID = findVoice(voiceName)
            if voiceID == None:
                print("\nUnable to locate voice for " + voiceName + "\n")
                abort(500)

        # generate and return the audio and metadata
        metadata = generateInternal(text, voiceID, voiceName, phonemeMap, model, outputName, emitRatio)
        with open("last.json", "w") as outfile:
            json.dump(metadata, outfile)
        return json.dumps(metadata)

    api.run()

#############################################
# listVoices will just print a table of the available voices
#############################################
@subcommand()
def listVoices(args = [], parent=subparsers):
    set_api_key(os.environ.get("ELEVENLABS_TOKEN"))
    table = [
            ["category", "id", "name", "labels"],
    ]
    for v in voices():
        table.append([v.category, v.voice_id, v.name, v.labels])

    print(tabulate(table, headers='firstrow'))

#############################################
# generateFull will run the full pipeline:
#  1. generate audio for the given text input and voice
#  2. store the mp3 and convert the audio to a mono wav
#  3. run allosaurus to generate the phonemes
#  4. output a metadata file with the timed phonemes
#############################################
@subcommand([
    argument("text", help="The text to generate"),
    argument("--voice-name", "-v", help="The name of the voice to use", default="gomez-test"),
    argument("--voice-id", help="The ID of the voice to use. If provided, will ignore `voice-name`."),
    argument("--output-name", "-o", help="A stub to use for naming all of the output files. There will be <outputName>.(mp3|wav|json) files created.", default="out"),
    argument("--emit-ratio", "-e", help="The emit value to pass to allosaurus, increasing means more phonemes will be generated", type=float, default=0.7),
])
def generateFull(args = [], parent=subparsers):
    set_api_key(os.environ.get("ELEVENLABS_TOKEN"))
    text = args.text
    voiceID = args.voice_id
    voiceName = args.voice_name
    emitRatio = args.emit_ratio
    outputName = args.output_name
    metadataFile = outputName + ".json"

    if text == "" or text == None:
        print("no text provided, aborting")
        exit(1);

    if voiceID == None:
        print("locating voice ID...")
        voiceID = findVoice(voiceName)
        if voiceID == None:
            print("\nUnable to locate voice for " + voiceName + "\n")
            exit(1);

    # create a map of the allophones to phonemes
    print("loading phonemes mappings...")
    alloToPhoneme = alloToPhoneme()

    # load the english model
    print("loading phonemes model...")
    model = read_recognizer('eng2102')

    # generate and return the audio and metadata
    metadata = generateInternal(text, voiceID, voiceName, alloToPhoneme, model, outputName, emitRatio)

    data = json.dumps(metadata, sort_keys=True, indent=4)
    f = open(metadataFile, "w")
    f.write(data)
    f.close()

# abstract the core generation logic to this function to be leveraged by the api or cli
def generateInternal(text, voiceID, voiceName, alloToPhoneme, model, outputName = "out", emitRatio = 0.7):
    mp3File = outputName + ".mp3"
    wavFile = outputName + ".wav"

    print("generating speech audio using Voice ID `" + voiceID + "`...")
    audio = generate(text=text, voice=voiceID)
    save(audio, mp3File)

    print("converting to wav file...")
    sound = AudioSegment.from_mp3(mp3File)
    sound.export(wavFile, format="wav", parameters=["-acodec", "pcm_s16le", "-ac", "1", "-ar", "16000"])

    print("running phoneme model...")
    r = model.recognize(wavFile, timestamp=True, lang_id='eng', topk=1, emit=emitRatio)

    print("outputting metadata...")
    lines = r.split('\n')

    results = []
    for line in lines:
        parts = line.split()
        time = parts[0]
        allophone = parts[2]
        phoneme = alloToPhoneme.get(allophone, allophone)
        results.append([time, phonemeToViseme.get(phoneme, 'unk')])

    base64Audio = ""
    with open(mp3File, "rb") as f:
        base64Audio = base64.b64encode(f.read()).hex()

    metadata = {}
    metadata["outputName"] = outputName
    metadata["prompt"] = text
    metadata["voiceName"] = voiceName
    metadata["voiceID"] = voiceID
    metadata["mp3File"] = os.getcwd() + "/" + mp3File
    metadata["emitRatio"] = emitRatio
    metadata["results"] = results
    metadata["audioLength"] = sound.duration_seconds
    metadata["audio"] = base64Audio
    return metadata

def alloToPhoneme():
    alloToPhoneme = {}
    with open('./inventory-full.csv') as csvfile:
        r = csv.reader(csvfile, delimiter=',')
        r.__next__()
        for row in r:
            allophones = row[7].split()
            for p in allophones:
                alloToPhoneme[p] = row[6]
    with open('./inventory.csv') as csvfile:
        r = csv.reader(csvfile, delimiter=',')
        r.__next__()
        for row in r:
            allophones = row[7].split()
            for p in allophones:
                alloToPhoneme[p] = row[6]
    return alloToPhoneme

# convert a voice name to a voice ID using the elevenlabs api
def findVoice(voiceName):
    for v in voices():
        if v.name == voiceName:
            return v.voice_id
    return None

# map phonemes to visemes
# https://docs.aws.amazon.com/polly/latest/dg/ph-table-english-us.html
phonemeToViseme = {
    "e": "e",
    "eː": "e",
    "e̞": "e",
    "kʰ": "k",
    "a": "a",
    "aː": "a",
    "b": "p",
    "d": "t",
    "d̠": "t",
    "f": "f",
    "h": "k",
    "i": "i",
    "iː": "i",
    "j": "i",
    "k": "k",
    "l": "t",
    "m": "p",
    "n": "t",
    "p": "p",
    "ð": "T",
    "θ": "T",
    "pʰ": "p",
    "s": "s",
    "t": "t",
    "tʰ": "t",
    "t̠": "t",
    "u": "u",
    "uː": "u",
    "v": "f",
    "w": "u",
    "x": "k",
    "z": "s",
    "æ": "a",
    "ə": "@",
    "əː": "@",
    "ɛ": "E",
    "ɛː": "E",
    "ɜː": "E",
    "ɡ": "k",
    "ɪ": "i",
    "ɵː": "T",
    "ɹ": "r",
    "ʃ": "S",
    "ʒ": "S",
    "ŋ": "k",
    "ɒ": "O",
    "ɒː": "O",
    "ʊ": "u",
    "ʌ": "E",

    "o": "NM",
    "oː": "NM",
    "r": "NM",
    "øː": "NM",
    "ɐ": "NM",
    "ɐː": "NM",
    "ɑ": "NM",
    "ɑː": "NM",
    "ɔ": "NM",
    "ɔː": "NM",
    "ɘ": "NM",
    "ɪ̯": "NM",
    "ɯ": "NM",
    "ɻ": "NM",
    "ʉ": "NM",
    "ʉː": "NM",
    "ʍ": "NM",
    "ʔ": "NM",
}

if __name__ == "__main__":
    args = cli.parse_args()
    if args.subcommand is None:
        cli.print_help()
    else:
        args.func(args)
