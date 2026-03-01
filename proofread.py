# ==========================================
# proofread.py · 弹幕辅助 ASR 校对
# ==========================================
from openai import OpenAI

from api_client import call_llm_api
from utils import extract_mapping
from config import PROOFREAD_BATCH_SIZE


def run_smart_proofread(client: OpenAI, asr_data, danmu_data, bg_params):
    """以弹幕为参考，批量调用 LLM 对 ASR 结果进行智能校对。"""
    print(f"📡 [Step 3/4] 正在执行智能校对...")
    context_str = f"Host: {bg_params['host_info']} | Title: {bg_params['stream_title']}"
    final = []
    total = len(asr_data)
    matched_count = 0

    for i in range(0, total, PROOFREAD_BATCH_SIZE):
        batch = asr_data[i : i + PROOFREAD_BATCH_SIZE]
        w_s, w_e = max(0, batch[0]["start"] - 15), batch[-1]["end"] + 15
        relevant_dm = [d for d in danmu_data if w_s <= d["_sec"] <= w_e]

        dm_in = "\n".join([f"{d['_sec']:.1f}s: {d['text']}" for d in relevant_dm])
        asr_in = "\n".join(
            [f"[S{i+idx+1:05d}] {s['text']}" for idx, s in enumerate(batch)]
        )

        messages = [
            {
                "role": "system",
                "content": (
                    f"执行日语 ASR 文本校对任务。校对背景：{context_str}。"
                    "依据 [Host] 确定讲话人背景，依据 [Title] 确定话题起始背景。"
                    "根据同期参考弹幕修正 ASR 中的错误。\n"
                    "【约束】1.保留 [Sxxxxx] 标签格式。2.无需修改则原样返回。3.禁止输出解释。"
                ),
            },
            {
                "role": "user",
                "content": f"[参考弹幕]\n{dm_in}\n\n[待校对ASR]\n{asr_in}",
            },
        ]
        try:
            content = call_llm_api(client, messages)
            mapping = extract_mapping(content)
            for idx, s in enumerate(batch):
                tid = f"S{i+idx+1:05d}"
                res_text = mapping.get(tid, s["text"])
                if res_text != s["text"]:
                    matched_count += 1
                final.append({"start": s["start"], "end": s["end"], "ja": res_text})
        except:
            for s in batch:
                final.append({"start": s["start"], "end": s["end"], "ja": s["text"]})

    print(f"✅ 校对完成，共订正 {matched_count} 处。")
    return final
