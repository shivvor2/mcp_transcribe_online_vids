"""Transcribes audio files locally"""

import gc
import os
from typing import Literal, Union

import torch
import whisperx


def get_transcription(
    file_path: str,
    model_name: Literal["medium", "large-v2", "large-v3"] = "large-v2",
    device: Union[torch.device, str] = "cuda",
    batch_size: int = 16,
    compute_type: Literal["float16", "int8"] = "float16",
    assign_speaker_labels: bool = True,
    diarization_model_name: str = None,
    min_speakers: int = None,
    max_speakers: int = None,
    hugging_face_token: str = None,
    model_save_dir: str = None,
    delete_model: bool = True,
):
    """Transcribes an audio file locally

    Args:
        file_path (str): relative path to the locally stored file
        device (str, optional): Device to run models on. Defaults to "cuda".
        batch_size (int, optional): _description_. Defaults to 16.
        compute_type (Literal[&quot;float16&quot;, &quot;int8&quot;], optional): Decides the precision to run the model on. Defaults to "float16".
        hugging_face_token (str, optional): HuggingFace token to access the diarization (speaker assignment) model. If no value is provided, the function attempts to get a huggingface token from the environment using os.getenv("HF_TOKEN")
        diarization_model_name (str, optional): Custom diarization model to be used, by default, "[pyannote/speaker-diarization-3.1](https://huggingface.co/pyannote/speaker-diarization-3.1)" is used
        min_speakers (int, optional), Specifies the minimum speakers present in the audio, leave blank if unknown
        max_speakers (int, optional), Specifies the maximum speakers present in the audio, leave blank if unknown
        hugging_face_token: (str, optional), huggingface token for model access.
        model_save_dir (str, optional): Local path to save the downloaded whisper model to.
        delete_model (bool, optional): whether to delete the model from memory after running that section, defaults to true.

    """
    # Basically stolen from whisperX page

    audio = whisperx.load_audio(file_path)

    # 1. Transcribing audio
    transcribe_model = whisperx.load_model(
        model_name, device, compute_type=compute_type, download_root=model_save_dir
    )
    result = transcribe_model.transcribe(audio, batch_size=batch_size)

    # Deletes transcribing model if required
    if delete_model:
        _delete_model(transcribe_model)

    # 2. Align output
    align_model, metadata = whisperx.load_align_model(
        language_code=result["language"], device=device
    )
    result = whisperx.align(
        result["segments"],
        align_model,
        metadata,
        audio,
        device,
        return_char_alignments=False,
    )

    if delete_model:
        _delete_model(align_model)

    # 3. Assign speaker labels
    if not assign_speaker_labels:
        return result["segments"]

    # See original code for [Diarization pipeline](https://github.com/m-bain/whisperX/blob/main/whisperx/diarize.py#L10)
    diarization_model_name = (
        diarization_model_name
        if diarization_model_name
        else "pyannote/speaker-diarization-3.1"
    )

    auth_token = hugging_face_token or os.getenv("HF_TOKEN")
    diarize_model = whisperx.DiarizationPipeline(
        use_auth_token=auth_token,
        device=device,
        model_name=diarization_model_name,
    )
    diarize_segments = diarize_model(
        audio, min_speakers=min_speakers, max_speakers=max_speakers
    )

    result = whisperx.assign_word_speakers(diarize_segments, result)

    return result


def _delete_model(model):
    """Deletes the provided model"""
    gc.collect()
    torch.cuda.empty_cache()
    del model
