# ==========================================
# main.py · 入口执行
# ==========================================
from pathlib import Path

from google.colab import files

from api_client import init_openai_client, usage_stats
from asr import run_asr
from danmaku_clean import run_danmaku_cleaning
from proofread import run_smart_proofread
from translate import run_parallel_translation
from utils import format_srt_time


def main():
    client = init_openai_client()
    print("=== 直播背景信息 ===")
    host_info = input("1. 请输入【配信者/所属/ファンネーム】(例如：ななしいんく所属 涼海ネモ): ").strip()
    stream_title = input("2. 请输入【直播标题】(例如：雑談): ").strip()

    # 自动打包
    my_bg = {
        "host_info": host_info if host_info else "未提供",
        "stream_title": stream_title if stream_title else "通用直播",
    }

    print("\n--- 背景信息已记录，请上传文件 ---")

    print("📤 上传音频:")
    audio_path = list(files.upload().keys())[0]

    print("📤 是否上传弹幕 JSON？(yes/no)")
    use_dm = input().strip().lower()

    if use_dm == "yes":
        print("📤 上传弹幕 JSON:")
        uploaded_dm = files.upload()
        dm_path = list(uploaded_dm.keys())[0] if uploaded_dm else None
    else:
        dm_path = None

    raw_asr = run_asr(audio_path)

    if dm_path:
        clean_dm = run_danmaku_cleaning(dm_path)
        proofed_data = run_smart_proofread(client, raw_asr, clean_dm, my_bg)
    else:
        print("⏭️ 已跳过弹幕校对")
        proofed_data = [{"start": s["start"], "end": s["end"], "ja": s["text"]} for s in raw_asr]

    final_data = run_parallel_translation(client, proofed_data)

    srt_file = f"{Path(audio_path).stem}_bilingual.srt"
    with open(srt_file, "w", encoding="utf-8") as f:
        for i, s in enumerate(final_data, 1):
            f.write(
                f"{i}\n"
                f"{format_srt_time(s['start'])} --> {format_srt_time(s['end'])}\n"
                f"{s['ja']}\n{s['zh']}\n\n"
            )

    print(f"\n✅ 任务结束。Token 消耗估算: {usage_stats.total_tokens}")
    files.download(srt_file)


if __name__ == "__main__":
    main()
