import essentia.standard as es
import numpy as np
import json
import soundfile as sf
import math
import random
import copy
import os

from pad import pad_music, crossfade_sounds

def generate_file(config_file):
    # Load the config
    with open(config_file, 'r') as file:
        config = json.load(file)

    decibels = config['decibels']
    target_length = config['target_length']
    sr = 44100  # Sample rate
    output_file_path = config['output_path']

    # Detect output format based on file extension
    _, ext = os.path.splitext(output_file_path)
    ext = ext.lower()
    format_map = {
        '.wav': 'WAV',
        '.flac': 'FLAC',
        '.ogg': 'OGG',
        '.aiff': 'AIFF'
    }
    output_format = format_map.get(ext, 'WAV')  # Default to WAV if the format is not recognized

    final_audio = []
    music_length_lcm = 1
    tot_relative_loudness = sum([audio_config['relative_loudness'] for audio_config in config['audio']])
    
    # Load and process each audio file
    for audio_config in config['audio']:
        filename = audio_config['filename']
        audio_type = audio_config['type']
        relative_loudness = audio_config['relative_loudness']

        print(f"Processing file {filename}")
        
        # Load audio file
        audio = es.MonoLoader(filename=filename, sampleRate=sr)()
        
        # Adjust volume based on relative loudness
        current_db = 20 * np.log10(np.sqrt(np.mean(audio**2)) + 1e-6)
        scaling_factor = 10 ** ((decibels - current_db) / 20)
        audio = audio * scaling_factor * (relative_loudness / tot_relative_loudness)

        # If the file is music, pad it to make it loopable
        if audio_type == 'music':
            print(f"Padding file {filename}")
            audio = pad_music(audio, sr)
            print("Done padding")

            if music_length_lcm // sr < 2 * target_length: # Only do this if the lcm is small enough that it makes sense
                music_length_lcm = math.lcm(audio.shape[0], music_length_lcm)
        
        # Append processed audio to list
        final_audio.append(audio)
    
    print("Done preprocessing sounds")

    # Determine final output length close to target length
    target_sample_length = int(target_length * sr)
    repetitions = (target_sample_length + music_length_lcm - 1) // music_length_lcm
    final_length = repetitions * music_length_lcm

    # Final length determined by lcm is too large
    if final_length / target_sample_length > 1.1:
        # Generate candidate lengths
        iters = 100000
        lower_bound = int(target_sample_length * 0.9)
        upper_bound = int(target_sample_length * 1.1)
        
        # Generate random int64 values within the specified range
        candidates = np.random.randint(lower_bound, upper_bound + 1, size=iters, dtype=np.int64)
        
        # Calculate the total remainder for each candidate
        total_remainder = np.zeros(iters)
        music_lengths = [len(audio) for i, audio in enumerate(final_audio) if config['audio'][i]['type'] == 'music']
        for length in music_lengths:
            total_remainder += np.remainder(candidates, length)

        # Find the candidate with the lowest total remainder
        best_candidate_index = np.argmin(total_remainder)
        final_length = candidates[best_candidate_index]

    print(f"Final length of audio: {final_length} seconds")

    # Initialize the buffer
    audio_buffer = copy.deepcopy(final_audio)

    # Initialize writer for output file with detected format
    with sf.SoundFile(output_file_path, mode='w', samplerate=sr, channels=1, format=output_format) as f:
        for second in range((final_length + sr - 1) // sr):
            if second % 100 == 0:
                print(f"Processing second number {second}")

            final_second = (second + 1) * sr >= final_length
            frames = final_length % sr if (final_second and (final_length % sr != 0)) else sr
            audio_this_second = np.zeros(frames)
            
            # Process each audio source
            for i in range(len(final_audio)):
                audio_type = config['audio'][i]['type']

                # If buffer is shorter than needed frames, handle looping or noise blending
                if audio_type == 'music' and len(audio_buffer[i]) < frames:
                    audio_buffer[i] = np.concatenate((audio_buffer[i], final_audio[i]))
                if audio_type == 'noise': 
                    if len(audio_buffer[i]) < 5 * sr:
                        # Sample a random segment from the original audio and crossfade it
                        min_length = max(len(final_audio[i]) // 4, 5 * sr)
                        sample_length = random.randint(min_length, len(final_audio[i]))
                        start_idx = random.randint(0, len(final_audio[i]) - sample_length)
                        noise_sample = final_audio[i][start_idx:start_idx + sample_length]
                        audio_buffer[i] = crossfade_sounds(audio_buffer[i], noise_sample, sr)

                    # Fade out for the last second if this is the final second
                    if final_second:
                        fade_out_samples = frames  # Use the number of frames to fade out
                        fade_out_curve = np.linspace(1, 0, fade_out_samples)  # Create a linear fade-out curve
                        audio_buffer[i][:fade_out_samples] *= fade_out_curve # Apply fade-out to the noise audio buffer for the last segment

                # Directly take the frames and add them to `audio_this_second`
                audio_this_second += audio_buffer[i][:frames]
                audio_buffer[i] = audio_buffer[i][frames:]  # Remove used frames from buffer
                
            # Write the second’s audio to file
            f.write(audio_this_second)

    print(f"Generated file saved at {output_file_path}")

if __name__ == '__main__':
    generate_file(config_file='./config.json')