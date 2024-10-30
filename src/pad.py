import essentia.standard as es
import numpy as np
from scipy.interpolate import UnivariateSpline

def pad_music(audio, sr=44100):
    # Analyze the beats
    beat_extractor = es.RhythmExtractor2013(method="multifeature")
    bpm, beats, beats_confidence, _, beats_intervals = beat_extractor(audio)

    # Extract the audio segment before the first beat
    start_time = beats[0]  # First beat time
    end_time = beats[-1]   # Last beat time
    start_sample = int(start_time * sr)  # Convert start time to sample index
    end_sample = int(end_time * sr)      # Convert end time to sample index

    audio_before_first_beat = audio[:start_sample]
    audio_after_last_beat = audio[end_sample:]

    # Calculate the target length for padding
    target_beat_length = int(sr * (60 / bpm))  # Length of one beat in samples
    combined_length = len(audio_before_first_beat) + len(audio_after_last_beat)

    # Determine the padding length
    if combined_length < target_beat_length:
        padding_length = target_beat_length - combined_length
    else:
        padding_length = 2 * target_beat_length - combined_length

    def interpolate_missing(arr1, n_missing, arr2):
        # Ensure the inputs are numpy arrays
        arr1 = np.asarray(arr1)
        arr2 = np.asarray(arr2)
        n1 = len(arr1)
        n2 = len(arr2)

        # Create a combined array for x-coordinates
        x = np.arange(n1 + n_missing + n2)
        
        # Create an array for y-coordinates with gaps for missing values
        y = np.concatenate((arr1, np.full(n_missing, np.nan), arr2))

        # Get the indices where values are not NaN
        valid_indices = np.isfinite(y)
        
        # Create the UnivariateSpline
        spline = UnivariateSpline(x[valid_indices], y[valid_indices], k=4)

        # Interpolate over the entire range of x
        interpolated_values = spline(x)

        return interpolated_values[n1:n1+n_missing]

    padding = interpolate_missing(audio_after_last_beat, padding_length, audio_before_first_beat)

    # Concatenate the audio segments and the padding
    loopable_audio = np.concatenate((audio, padding))
    return loopable_audio

def crossfade_sounds(sound1, sound2, sr=44100, overlap_duration=2.0):
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

if __name__ == '__main__':
    import os
    import soundfile as sf

    # Input and output paths
    input_path = './data/sounds/meow_mix_song.mp3'
    output_path = './output/meow_mix_loopable.wav'
    sr = 44100  # Sample rate for consistency

    # Load the audio file
    print("Loading audio file...")
    audio = es.MonoLoader(filename=input_path, sampleRate=sr)()
    
    # Pad the audio to make it loopable
    print("Padding audio to make it loopable...")
    padded_audio = pad_music(audio, sr)

    # Export the padded audio
    # Determine output format from extension
    _, ext = os.path.splitext(output_path)
    format_map = {
        '.wav': 'WAV',
        '.flac': 'FLAC',
        '.ogg': 'OGG',
        '.mp3': 'MP3'
    }
    output_format = format_map.get(ext.lower(), 'WAV')

    # Save the padded audio
    print(f"Saving padded audio to {output_path}...")
    with sf.SoundFile(output_path, mode='w', samplerate=sr, channels=1, format=output_format) as f:
        f.write(padded_audio)

    print("Export complete.")