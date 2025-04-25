"""Converts files format using using ffmpeg"""

import os
import subprocess
import warnings
from typing import Optional

SUPPORTED_FORMATS = {
    ".mp3",
    ".wav",
    ".m4a",
    ".flac",
    ".ogg",
    ".aac",
    ".wma",
    ".aiff",
    ".aif",
    ".aifc",
    ".mp4",
    ".mpeg",
    ".webm",
    ".opus",
}  # Might be wrong


def convert_to_wav(
    input_path: str,
    output_path: Optional[str] = None,
    output_file_name: Optional[str] = None,
    sample_rate: int = 16000,
    audio_codec: str = "pcm_s16le",
    overwrite: bool = True,
) -> str:
    """Converts the provided audio file to .wav format

    Args:
        input_path (str): Path of the input file
        output_path (str, optional): Path for the output folder. If the folder doesnt exist yet, the function will attempt to create it (and then store the file in it). If no value is provided, the file will be stored at the folder the input file resides.
        output_file_name (str, optional): Specifies the name of the output file, if not provided, the converted file will have the same name as the input file
        sample_rate (int, optional): Sample rate for the .wav audio. Defaults to 16000.
        audio_codec (str, optional): Audio codec to use, see [availiable pcm audio codecs](https://trac.ffmpeg.org/wiki/audio%20types) (Append "pcm_" in front). Defaults to "pcm_s16le".
        overwrite (bool, optional): Whether or not to overwrite if a file of the same target name exists. Defaults to True.

    Returns:
        str: Path of the converted file
    """

    extension = check_and_reject_format(input_path)

    # Early exit if no need for conversion
    if extension == ".wav":
        return input_path

    # Get output file path
    output_path = get_output_file_path(input_path, output_path, output_file_name)

    # Dont overwrite if extended
    if not overwrite and os.path.isfile(output_path):
        warnings.warn(f"File already exist: {output_path}, reusing it")
        return output_path

    convert_ffmpeg(input_path, output_path, sample_rate, audio_codec, overwrite)

    verify_output(output_path)

    return output_path


def check_and_reject_format(input_path: str) -> str:
    """Rejects unsupported files and returns file type (for early stopping)

    Args:
        input_path (str): Path of the input file

    Raises:
        ValueError: If file extension is not supported, most common containers are supported (e.g. ".mp3", ".mp4', ".m4a", ".ogg" )

    Returns:
        str: Extension of the input file e.g. ".mp3", ".wav" etc.
    """
    _, extension = os.path.splitext(input_path)
    if extension not in SUPPORTED_FORMATS:
        raise ValueError(f"Format not supported: {extension}, file name: {input_path}")
    return extension


def get_output_file_path(
    input_path: str,
    output_path: Optional[str] = None,
    output_file_name: Optional[str] = None,
) -> str:
    """Util function to get the final output path

    Args:
        input_path (str): Path of the input file
        output_path (str, optional): Path for the output folder, if no value is provided, the folder where the input file resides will be used.
        output_file_name (str, optional): Specifies the name of the output file, if not provided, the "name" of the input file will be used (without the extension of course)

    Raises:
        OSError: If the output path cannot be created/ accessed

    Returns:
        str: The path of the final output file (to be supplied to the ffmpeg wrapper)
    """

    input_folder, input_file = os.path.split(input_path)
    input_file_name, _ = os.path.splitext(input_file)

    output_file_name = input_file_name if output_file_name is None else output_file_name
    output_folder = input_folder if output_path is None else output_path

    output_file_path = os.path.join(output_folder, output_file_name + ".wav")

    try:
        os.makedirs(output_folder, exist_ok=True)
    except OSError as e:
        raise e

    return output_file_path


def convert_ffmpeg(
    input_path: str,
    output_path: str,
    sample_rate: int,
    audio_codec: str,
    overwrite: bool,
) -> None:
    """Creates the ffmpeg call, converts the file, and stores the converted file in the specified output path

    Args:
        input_path (str): Path of the input file
        output_path (str): Path of the output file
        sample_rate (int): Sample rate for the output file
        audio_codec (str): Audio codec to use (e.g., "pcm_s16le", "pcm_s24le", etc.), see [availiable pcm audio codecs](https://trac.ffmpeg.org/wiki/audio%20types) (Append "pcm_" in front).
        overwrite (bool): Whether or not to overwrite if a file of the same target name exists.

    Raises:
        RuntimeError: When the ffmpeg call either fails to start, or results in an error
    """
    # FFmpeg call
    cmd = [
        "ffmpeg",
        "-i",
        input_path,  # Input file
        "-vn",  # Disable video if present
        "-acodec",
        audio_codec,  # Audio codec
        "-ar",
        str(sample_rate),  # Sample rate
        "-af",
        "aresample=resampler=soxr",
        *(["-y"] if overwrite else ["-n"]),  # Overwrite output file if exists
        output_path,
    ]

    try:
        # Run FFmpeg command
        result = subprocess.run(cmd, capture_output=True, text=True)

        # Check if conversion was successful
        if result.returncode != 0:
            raise RuntimeError(f"FFmpeg conversion failed: {result.stderr}")

    except subprocess.SubprocessError as e:
        raise RuntimeError(f"FFmpeg execution failed: {str(e)}")


def verify_output(output_path: str) -> None:
    """Verifies that the output file exists and is not empty

    Args:
        output_path (str): Path of the output file to verify

    Raises:
        RuntimeError: If the file doesn't exist or is empty
    """

    if not os.path.exists(output_path):
        raise RuntimeError("Conversion failed: Output file doesn't exist")

    if os.path.getsize(output_path) == 0:
        raise RuntimeError("Conversion Error: Output file is empty")
