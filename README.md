# Text to Speech and Viseme Assignment

This is a module of my AI powered animatronics pipeline.
It is responsible for taking input text and generating an
audio file as well as timestamped markers for each viseme change.

The visemes can be used to translate directly to jaw movements on
the animatronics.

## Elevenlabs

Currently the whole thing is only powered by [ElevenLabs](https://elevenlabs.io/).
You will need an account and an 
API token on your environment as `ELEVENLABS_TOKEN`.

## Starting the Server

You can run the server with `./eleven.py api` and make a request like this:

```bash
curl -L http://127.0.0.1:5000/generate \
  -X POST \
  -d voiceName="[ElevenVoices] American Female Teen" \
  -d text="this is a test" \
  -d name="test 1"
```

response:

```json
{
  "audio": "<base64 encoded hex string of the mp3 audio>",
  "audioLength": 1.1493877551020408,
  "emitRatio": 0.7,
  "mp3File": "/home/ken/projects/ai-skeletons/phone-generation/test 1.mp3",
  "outputName": "test 1",
  "prompt": "this is a test",
  "results": [
    ["0.060", "T"],
    ["0.100", "i"],
    ["0.190", "s"],
    ["0.250", "i"],
    ["0.340", "s"],
    ["0.380", "@"],
    ["0.480", "t"],
    ["0.530", "e"],
    ["0.700", "s"],
    ["0.810", "t"]
  ],
  "voiceID": "FxXx1SvSMrk96HmqFCUS",
  "voiceName": "[ElevenVoices] American Female Teen"
}
```

The results are an array containing the timestamp (in seconds)
and the viseme symbol based on
[this table](https://docs.aws.amazon.com/polly/latest/dg/ph-table-english-us.html).


## Running Manually

You can also use the tool for generation without standing up the api using `./eleven.py generateFull`

See the options [here](https://github.com/kkoch986/ai-skeletons-phoneme-generation/blob/f693fd4a6e014b5e30a526a5c8603d280ff22b77/eleven.py#L108-L113).
