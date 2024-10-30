# For testing code.

import numpy as np
import essentia.standard as es
import soundfile as sf

# Load audio file using essentia
def load_audio(filepath):
    loader = es.MonoLoader(filename=filepath)
    return loader()

# Crossfade function remains the same
def crossfade_sounds(sound1, sound2, sr, overlap_duration=2.0):
    # Ensure the inputs are numpy arrays
    sound1 = np.asarray(sound1)
    sound2 = np.asarray(sound2)
    
    # Calculate the overlap in samples
    overlap_samples = int(overlap_duration * sr)
    
    # Ensure both sounds have enough length for the overlap
    if len(sound1) < overlap_samples or len(sound2) < overlap_samples:
        raise ValueError("Sounds must be longer than the overlap duration")

    # Separate the non-overlapping and overlapping parts
    sound1_main = sound1[:-overlap_samples]
    sound1_overlap = sound1[-overlap_samples:]
    sound2_overlap = sound2[:overlap_samples]
    sound2_main = sound2[overlap_samples:]
    
    # Create fade-out for the end of sound1 and fade-in for the start of sound2
    fade_out_curve = np.linspace(1, 0, overlap_samples)
    fade_in_curve = np.linspace(0, 1, overlap_samples)
    
    # Apply the fades
    sound1_faded = sound1_overlap * fade_out_curve
    sound2_faded = sound2_overlap * fade_in_curve
    
    # Combine the crossfaded part
    crossfaded_section = sound1_faded + sound2_faded
    
    # Concatenate everything to form the continuous sound
    continuous_sound = np.concatenate((sound1_main, crossfaded_section, sound2_main))
    
    return continuous_sound

# Select random segments from an audio array
def get_random_segments(audio, sr, segment_duration=3.0):
    segment_length = int(segment_duration * sr)
    if len(audio) < segment_length:
        raise ValueError("Audio is too short for the requested segment length")
    
    # Randomly pick start points for sound1 and sound2
    start1 = np.random.randint(0, len(audio) - segment_length)
    start2 = np.random.randint(0, len(audio) - segment_length)
    
    sound1 = audio[start1:start1 + segment_length]
    sound2 = audio[start2:start2 + segment_length]
    
    return sound1, sound2

# Example usage
sr = 44100  # Sample rate (in Hz)
audio = load_audio('./data/sounds/baby_crying.mp3')

# Get two random segments from the audio
sound1, sound2 = get_random_segments(audio, sr, segment_duration=10.0)

# Crossfade the two sounds with a 2-second overlap
continuous_sound = crossfade_sounds(sound1, sound2, sr, overlap_duration=2.0)

output_filepath = './output/baby_crying_loopable.wav'
sf.write(output_filepath, continuous_sound, sr)

print(f"Continuous sound saved at {output_filepath}")
