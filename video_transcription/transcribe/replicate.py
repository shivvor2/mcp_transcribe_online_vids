"""Transcribe input media (e.g. podcasts) via cloud service e.g. replicate"""

import logging
from typing import Any, Literal

import httpx
import replicate
from _io import BufferedReader

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

models = {
    "medium": "carnifexer/whisperx:1e0315854645f245d04ff09f5442778e97b8588243c7fe40c644806bde297e04",
    "large-v2": "daanelson/whisperx:9aa6ecadd30610b81119fc1b6807302fd18ca6cbb39b3216f430dcf23618cedd",
    "large-v3": "victor-upmeet/whisperx:84d2ad2d6194fe98a17d2b60bef1c7f910c46b2f6fd38996ca457afd9c8abfcb",
}

default_timeout = httpx.Timeout(
    20160.0,  # default timeout
    read=20160.0,  # 20 minutes read timeout
    write=1200.0,  # write timeout
    connect=1200.0,  # connect timeout
    pool=1200.0,  # pool timeout
)


# Input must be a .wav file
def get_transcription_from_replicate(
    audio: str | BufferedReader,
    model_name: Literal["medium", "large-v2", "large-v3"] = "large-v3",
    debug: bool = False,
    timeout: httpx.Timeout = None,
    **kwargs: Any,
) -> Any:
    """Transcribes an audio file via replicate (cloud service)

    Has multilingual support but not always guarenteed
    For other arguments, please check the available arguments for whisperX [medium](https://replicate.com/carnifexer/whisperx/api/schema), [large-v2](https://replicate.com/daanelson/whisperx/api/schema) and [large-v3](https://replicate.com/victor-upmeet/whisperx/api)
    Providing an invalid argument will likely result in an error

    Args:
        audio (str | BufferedReader): The target audio file to transcribe, can either provide a local file e.g. ( audio_obj = open(audio_path, "rb") ) or the url to the audio
        model (str): Choose which model to use, must be one of "medium", "large-v2" and "large-v3", defaults to "large-v2"
        debug (bool): If True, enable logging output. Defaults to False
        timeout (httpx.Timeout): Timeout settings for the replicate service
        kwargs: Refer to each model's schema page

    returns:
        A dictionary containing transcribed audio and sentence level timestamps
    """
    timeout = timeout if timeout is not None else default_timeout

    logger.setLevel(logging.INFO if debug else logging.WARNING)

    audio_key = "audio_file" if model_name == "large-v3" else "audio"

    # audio = open(file_path, "rb") if file_path else url
    # input = {audio_key: audio} | kwargs

    input = {audio_key: audio} | kwargs

    # Log the inputs dictionary
    logger.info(f"Model: {model_name}")
    logger.info("Inputs:")
    logger.info(f" {audio_key}: {audio}")
    for key, value in kwargs.items():
        logger.info(f"  {key}: {value}")

    output = replicate.run(models[model_name], input=input)

    return output
