# ==========================================
# danmaku_clean.py · 弹幕清洗
# ==========================================
import json
import re
from collections import defaultdict

from rapidfuzz import fuzz

from utils import time_to_seconds


def run_danmaku_cleaning(file_name):
    """读取弹幕 JSON 文件，过滤低质量条目并去重，返回按时间排序的弹幕列表。"""
    print("🧹 [Step 2/4] 正在清洗参考弹幕...")
    buckets, clean_res = defaultdict(list), []
    KANJI = re.compile(r"[\u4E00-\u9FFF]")
    try:
        with open(file_name, "r", encoding="utf-8") as f:
            for line in f:
                data = json.loads(line)
                items = data.get("replayChatItemAction", {}).get("actions", [])
                for a in items:
                    renderer = (
                        a.get("addChatItemAction", {})
                        .get("item", {})
                        .get("liveChatTextMessageRenderer")
                    )
                    if not renderer:
                        continue
                    ts = renderer.get("timestampText", {}).get("simpleText", "0:00")
                    msg = "".join(
                        r.get("text", "")
                        for r in renderer.get("message", {}).get("runs", [])
                    )
                    if len(msg) < 2 or not KANJI.search(msg):
                        continue
                    key = (msg[0], len(msg) // 2)
                    if any(fuzz.ratio(msg, old) >= 80 for old in buckets[key]):
                        continue
                    buckets[key].append(msg)
                    clean_res.append({"_sec": time_to_seconds(ts), "text": msg})
    except Exception as e:
        print(f"弹幕清洗出错: {e}")
    return sorted(clean_res, key=lambda x: x["_sec"])
