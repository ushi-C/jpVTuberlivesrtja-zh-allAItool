# ==========================================
# config.py · 全局配置（所有配置参数）
# ==========================================

# --- API 配置 ---
OPENAI_BASE_URL = "https://api.chatanywhere.tech/v1"
MODEL_NAME = "gpt-5.2"

# --- 并发与重试 ---
MAX_WORKERS = 4            # 并发翻译
RETRY_MAX_ATTEMPTS = 3

# ==========================================
# 🔊 ASR 配置
# ==========================================

WHISPER_MODEL_SIZE = "large-v3"

# ----- device -----
ASR_DEVICE = "cuda"         
ASR_COMPUTE_TYPE = "float16" 

# ----- decoding -----
ASR_LANGUAGE = "ja"
ASR_BEAM_SIZE = 5
ASR_TEMPERATURE = [0.0, 0.2, 0.4, 0.6]
ASR_WORD_TIMESTAMPS = False
ASR_LOG_PROGRESS = False

# ----- chunk -----
ASR_CHUNK_LENGTH = 30

# ----- ngram -----
ASR_NO_REPEAT_NGRAM_SIZE = 6

# ----- VAD -----
ASR_VAD_FILTER = True
ASR_NO_SPEECH_THRESHOLD = 0.55

VAD_PARAMS = {
    "threshold": 0.16,
    "max_speech_duration_s": 30,
    "min_speech_duration_ms": 500,
    "min_silence_duration_ms": 800,
    "speech_pad_ms": 200,
}

# ==========================================
# --- 翻译配置 ---
# ==========================================

MAX_CHARS_PER_CHUNK = 3000  # 翻译分块
PROOFREAD_BATCH_SIZE = 100  # 轴/批
TRANSLATE_SYSTEM_PROMPT = "执行字幕翻译任务：将日语翻译为中文。"
TRANSLATE_USER_TEMPLATE = (
    "请逐行将日语翻译为中文。根据上下文语境纠正突兀之处，"
    "人名和自造词保留日语原文，必须严格保持并输出所有 ID。\n"
    "格式：[ID] 中文翻译\n\n{input_block}"
)
