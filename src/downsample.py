import subprocess
import os
import shutil

def downsample_to_128kbps(input_path, output_path):
    # If input and output paths are the same, create a temporary output file
    temp_output_path = output_path if input_path != output_path else f"{output_path}.tmp"
    
    # Downsample to 128 kbps using ffmpeg
    subprocess.run([
        'ffmpeg', '-i', input_path, '-b:a', '128k', temp_output_path
    ], check=True)
    
    # If using a temporary file, move it to the final output path
    if temp_output_path != output_path:
        shutil.move(temp_output_path, output_path)
    
    # Delete the input file
    os.remove(input_path)
    print(f"Downsampled file saved at {output_path}")

if __name__ == '__main__':
    input_wav_path = './output/output.mp3'
    output_mp3_path = './output/meow_mix_baby_crying_loop.mp3'
    downsample_to_128kbps(input_wav_path, output_mp3_path)
