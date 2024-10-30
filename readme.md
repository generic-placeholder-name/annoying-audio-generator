# Annoying Audio Generator

Ever wanted to listen to the most annoying sounds imaginable? Want to experience the Guantanamo Bay musical experience? Look no further!

Here is a loop of the Meow Mix theme song overlaid on the sound of a baby crying, courtesy of [an eccentric DJ from the CIA](https://www.theguardian.com/world/2008/jun/19/usa.guantanamo):
[![Watch the Guantánamo Bay Music Experience](https://img.youtube.com/vi/oP2nsX5EufY/0.jpg)](https://www.youtube.com/watch?v=oP2nsX5EufY)


### What This Thing Does
It stitches together multiple audio files in a loop, taking care to make sure that transitions aren't jarring. 

### To Run
1. Clone the repo:
   ```bash
   git clone <repo-url>
   ```
2. Install the required packages:
   ```bash
   pip install essentia soundfile scipy
   ```

### Generate the Audio File
1. Go to the project directory.
2. Run:
   ```bash
   python src/gen.py
   ```
3. Edit `config.json` to customize your audio mix.

#### Sample Config File
```json
{
    "output_path": "./output/output.mp3",
    "decibels": -9,
    "target_length": 36000,
    "audio": [
      {
        "filename": "./data/sounds/baby_crying.mp3",
        "type": "noise",
        "relative_loudness": 0.35
      },
      {
        "filename": "./data/sounds/meow_mix_song.mp3",
        "type": "music",
        "relative_loudness": 1
      }
    ]
  }
```

#### Config File Fields
- **output_path**: Path for the generated output file.
- **decibels**: Desired loudness level of the final audio (in decibels). Value should be generally in the range of `-35` to `-5`. Higher or lower values may cause errors.
- **target_length**: Approximate duration of the output audio (in seconds). Final length may vary slightly.

Each **audio** entry includes:
- **filename**: Path to the input audio file.
- **type**: Either `"music"` or `"noise"`; used to apply specific audio processing.
- **relative_loudness**: Relative loudness of this input file in the final mix, weighted against the other entries.

### To Downsample the Output
Run the following:
```bash
python src/downsample.py
```
This will convert the audio file to a compressed 128 kbps MP3. Ensure you have `ffmpeg` installed for this step.

### To Turn Audio into Video
If you need to turn your audio file into video, you can do it as well!

First, you must ensure that you have installed `moviepy`:
```bash
pip install moviepy
```

Run the following:
```bash
python src/video.py
```