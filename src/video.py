from moviepy.editor import ImageClip, AudioFileClip

def create_video(image_path, audio_path, output_path):
    # Load image and set duration from the audio file
    audio = AudioFileClip(audio_path)
    image = ImageClip(image_path).set_duration(audio.duration)

    # Set the audio to the image clip
    video = image.set_audio(audio)

    # Export the video file with a low fps
    video.write_videofile(output_path, fps=1, codec="libx264", audio_codec="aac")

    print(f"Video saved to {output_path}")

if __name__ == '__main__':
    create_video('./data/pics/cia_flag.png', './output/meow_mix_baby_crying_loop.mp3', 'output/video.mp4')
