# ==========================================
# asr.py · ASR 识别
# ==========================================
import gc
from difflib import SequenceMatcher

import torch
from faster_whisper import WhisperModel

from config import (
    WHISPER_MODEL_SIZE,
    ASR_DEVICE,
    ASR_COMPUTE_TYPE,
    ASR_LANGUAGE,
    ASR_BEAM_SIZE,
    ASR_TEMPERATURE,
    ASR_WORD_TIMESTAMPS,
    ASR_LOG_PROGRESS,
    ASR_CHUNK_LENGTH,
    ASR_VAD_FILTER,
    ASR_NO_SPEECH_THRESHOLD,
    VAD_PARAMS,
    ASR_NO_REPEAT_NGRAM_SIZE,
)


def run_asr(audio_path):
    """对音频文件执行 Whisper ASR，返回去重后的片段列表。"""
    print("🎧 [Step 1/4] 正在 ASR 识别")

    model = WhisperModel(
        WHISPER_MODEL_SIZE,
        device=ASR_DEVICE,
        compute_type=ASR_COMPUTE_TYPE,
    )

    segments, _ = model.transcribe(
        audio_path,
        language=ASR_LANGUAGE,
        beam_size=ASR_BEAM_SIZE,

        # ===== decoding =====
        temperature=ASR_TEMPERATURE,
        word_timestamps=ASR_WORD_TIMESTAMPS,
        log_progress=ASR_LOG_PROGRESS,

        # ===== ngram =====
        no_repeat_ngram_size=ASR_NO_REPEAT_NGRAM_SIZE,

        # ===== chunk =====
        chunk_length=ASR_CHUNK_LENGTH,

        # ===== VAD =====
        vad_filter=ASR_VAD_FILTER,
        vad_parameters=VAD_PARAMS,
        no_speech_threshold=ASR_NO_SPEECH_THRESHOLD,
    )

    res = []
    for s in segments:
        if s.text.strip():
            res.append({
                "start": s.start,
                "end": s.end,
                "text": s.text.strip()
            })

    # 去重逻辑（工程性应对）
    if not res:
        return []
    output = [res[0]]
    for cur in res[1:]:
        prev = output[-1]
        sim = SequenceMatcher(None, prev["text"], cur["text"]).ratio()
        if sim >= 0.9 and (cur["start"] - prev["end"]) <= 0.5:
            prev["end"] = max(prev["end"], cur["end"])
            if len(cur["text"]) > len(prev["text"]):
                prev["text"] = cur["text"]
        else:
            output.append(cur)

    del model
    gc.collect()
    torch.cuda.empty_cache()
    return output
