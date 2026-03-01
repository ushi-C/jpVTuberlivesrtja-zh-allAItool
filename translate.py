# ==========================================
# translate.py · 翻译
# ==========================================
from concurrent.futures import ThreadPoolExecutor, as_completed

from openai import OpenAI

from api_client import call_llm_api
from utils import extract_mapping
from config import MAX_WORKERS, MAX_CHARS_PER_CHUNK, TRANSLATE_SYSTEM_PROMPT, TRANSLATE_USER_TEMPLATE
from typing import List, Tuple, Dict

def _translate_worker(client: OpenAI, chunk: List[Tuple[str, str]], idx: int, total: int) -> Dict[str, str]:
    input_block = "\n".join([f"[{sid}] {txt}" for sid, txt in chunk])
    messages = [
        {"role": "system", "content": TRANSLATE_SYSTEM_PROMPT},
        {"role": "user", "content": TRANSLATE_USER_TEMPLATE.format(input_block=input_block)},
    ]
    try:
        content = call_llm_api(client, messages)
        mapping = extract_mapping(content)

        # 检测解析失败的 ID，逐条单独重试
        missing = [(sid, txt) for sid, txt in chunk if sid not in mapping]
        if missing:
            print(f"   ⚠️ chunk {idx}/{total}: {len(missing)} 条解析失败，逐条重试...")
            for sid, txt in missing:
                try:
                    single = call_llm_api(client, [
                        {"role": "system", "content": TRANSLATE_SYSTEM_PROMPT},
                        {"role": "user", "content": f"只输出中文译文，不要任何其他内容：{txt}"},
                    ])
                    mapping[sid] = single.strip()
                except Exception:
                    mapping[sid] = txt  # 保留日语原文

        return mapping

    except Exception as e:
        print(f"   ❌ chunk {idx}/{total} 整体失败: {e}，保留原文")
        return {sid: txt for sid, txt in chunk}  # 整体失败时保留原文，不返回空字典


def run_parallel_translation(client: OpenAI, segments: List[dict]) -> List[dict]:
    print(f"🚀 [Step 4/4] 启动并发翻译 (并发: {MAX_WORKERS})...")
    items = [(f"S{i+1:05d}", s["ja"]) for i, s in enumerate(segments)]

    chunks, cur_chunk, cur_len = [], [], 0
    for sid, txt in items:
        line = f"[{sid}] {txt}"
        if cur_chunk and cur_len + len(line) > MAX_CHARS_PER_CHUNK:
            chunks.append(cur_chunk)
            cur_chunk, cur_len = [], 0
        cur_chunk.append((sid, txt))
        cur_len += len(line)
    if cur_chunk:
        chunks.append(cur_chunk)

    all_zh: Dict[str, str] = {}
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {
            executor.submit(_translate_worker, client, c, i + 1, len(chunks)): i
            for i, c in enumerate(chunks)
        }
        for f in as_completed(futures):
            all_zh.update(f.result())

    # 仍缺失的 ID 用日语原文填充
    failed = 0
    for i, s in enumerate(segments):
        sid = f"S{i+1:05d}"
        s["zh"] = all_zh.get(sid) or s["ja"]
        if not all_zh.get(sid):
            failed += 1

    if failed:
        print(f"   ⚠️ 最终仍有 {failed} 条未翻译，已用日语原文填充")
    else:
        print("   ✅ 全部翻译完成")
    return segments
