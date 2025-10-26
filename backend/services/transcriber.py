import subprocess, os
import imageio_ffmpeg

def extract_audio_from_video(video_path: str):
    """
    Extracts audio from a video file using FFmpeg from imageio-ffmpeg.
    """
    audio_path = os.path.splitext(video_path)[0] + ".wav"
    ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

    command = [
        ffmpeg_exe, "-y", "-i", video_path,
        "-vn",  # no video
        "-acodec", "pcm_s16le",
        "-ar", "16000",  # 16kHz sample rate
        "-ac", "1",      # mono
        audio_path
    ]

    print(f"🎥 Extracting audio using {ffmpeg_exe}")
    subprocess.run(command, check=True)
    return audio_path


def transcribe_audio(file_path: str):
    """
    Transcribes either audio or video using Whisper.cpp.
    """
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    whisper_exe = os.path.join(base_dir, "whisper", "whisper-cli.exe")
    model_path = os.path.join(base_dir, "whisper", "models", "ggml-base.en.bin")

    ext = os.path.splitext(file_path)[1].lower()

    # 🎥 Convert video to audio first
    if ext in [".mp4", ".mkv", ".mov", ".avi"]:
        print("🎞️ Extracting audio from video before transcription...")
        file_path = extract_audio_from_video(file_path)

    output_txt = file_path + ".txt"

    command = [whisper_exe, "-m", model_path, "-f", file_path, "-otxt"]
    print("🎧 Running Whisper command:", " ".join(command))

    result = subprocess.run(command, capture_output=True, text=True)
    print(result.stdout)
    print(result.stderr)

    if result.returncode != 0:
        raise RuntimeError(f"Whisper failed with exit code {result.returncode}\n{result.stderr}")

    with open(output_txt, "r", encoding="utf-8") as f:
        transcript_text = f.read()

    return transcript_text, output_txt
