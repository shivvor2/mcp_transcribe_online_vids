import logging
import os
import shutil
from typing import Literal, Optional

from dotenv import load_dotenv
from fastmcp import Context, FastMCP

# Local imports
from video_transcription.get_media import get_bilibili, get_youtube
from video_transcription.host_files import upload_file_to_zerox
from video_transcription.pre_processing.convert_audio_format import convert_to_wav
from video_transcription.transcribe import get_transcription_from_replicate
from video_transcription.transcript_formatting import reformat_segments

load_dotenv()

temp_file_path = os.getenv("TEMP_FILE_PATH")

logger = logging.getLogger(__name__)
logger.setLevel(os.getenv("LOGGING_LEVEL", "INFO"))


def get_name(file_path: str):
    _, name = os.path.split(file_path)
    name, _ = os.path.splitext(name)
    return name


def transciption_pipeline(
    file_path: str,
    sampling_rate: int = 16000,
    cloud_transcribe_model_name: Literal["medium", "large-v2", "large-v3"] = "large-v3",
    cloud_transcribe_kwargs: Optional[dict] = None,
):
    """Provide a local supported file (by file path) and obtain it's transcription

    Args:
        file_path (str): The path to the file to be transcribed, must be a video/ audio file supported by ffmpeg
        sampling_rate (int, optional): Sample rate when preforming transcription. Defaults to 16000.
        cloud_transcribe_model_name (str, optional): Version of whisperX to be used during transcription on replicate. There is no reason to change it. Defaults to "large-v3".
        cloud_transcribe_kwargs (Optional[dict], optional): Optional arguments to be provided to replicate for the transcription process. Defaults to None.

    Returns:
        str: Reformatted transcription of the provided file
    """

    audio = convert_to_wav(file_path, sample_rate=sampling_rate, overwrite=False)
    cloud_transcribe_kwargs = cloud_transcribe_kwargs if cloud_transcribe_kwargs else {}

    # Directly supply the file for inference or upload the file depending on size
    size = os.path.getsize(audio)
    print(f"Converted audio size: {(size / 1024) /1024:.1f} MB")
    if size < float(os.getenv("LOCAL_FILE_SIZE_LIMIT")) * 1024 * 1024:
        print("Upload file directly to inference endpoint")
        audio = open(audio, "rb")
    else:
        print("Exceeded size limit, uploading to file host before performing inference")
        audio = upload_file_to_zerox(audio, 3600)
        print("Uploaded File")

    # Transcribing and reformating the audio

    print("Start Transcription")
    transcript = get_transcription_from_replicate(
        audio, model_name=cloud_transcribe_model_name, **cloud_transcribe_kwargs
    )
    transcript = transcript["segments"]
    transcript_txt = reformat_segments(transcript)

    return transcript_txt


mcp = FastMCP("Video Transcription")


@mcp.tool()
async def get_youtube_transcript(url: str, ctx: Context):
    """Provide a youtube url and obtain a timestamped transcript of that youtube video

    Args:
        url (str): A url of the youtube video

    Returns:
        str: The timestamped transcript of the youtube video
    """
    try:
        media_path = get_youtube(url, temp_file_path)
        transcript = transciption_pipeline(media_path)
        return transcript
    except Exception as e:
        await ctx.error(f"Encountered the following error: {str(e)}")
        raise  # This part is correct - raising after logging
    finally:
        shutil.rmtree(media_path)


@mcp.tool()
async def get_bilibili_transcript(url: str, ctx: Context):
    """Provide a bilibili url and obtain a timestamped transcript of that bilibili video

    Args:
        url (str): A url of the bilibili video

    Returns:
        str: The timestamped transcript of the youtube video
    """
    try:
        media_path = get_bilibili(url, temp_file_path)
        transcript = transciption_pipeline(media_path)
        return transcript
    except Exception as e:
        await ctx.error(f"Encountered the following error: {str(e)}")
        raise  # This part is correct - raising after logging
    finally:
        shutil.rmtree(media_path)


if __name__ == "__main__":
    mcp.run()
