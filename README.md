# 自动字幕

YouTube日语直播音频 → 中日双语 SRT 字幕。                   ※运行于 Google Colab（CUDA，T4 GPU）。自用为主，仅作分享。【该项目硬件需求为近0，你需要一台能看YouTube直播的计算机即可】

```
音频文件（默认设置，可修改部分在前置参数config.py中）
    ↓
[1] ASR 识别        faster-whisper large-v3，日语，VAD 过滤 + 去重
    ↓
[2] 弹幕清洗        解析 YouTube 回放弹幕 JSON，汉字过滤 + 模糊去重
    ↓
[3] 日语校对（含prompt）以弹幕为参考，LLM 批量纠正 ASR 错误
    ↓
[4] AI翻译（含prompt）LLM 日语 → 中文，分块并发翻译，保留人名/自造词
    ↓
输出 *_bilingual.srt（日文 + 中文双轨）
```

---

## 文件结构

```
auto_srt/
├── config.py          # 所有可调参数
├── utils.py           # 工具函数：时间转换、SRT 格式化、ID 解析
├── api_client.py      # OpenAI 客户端、重试器、Token 统计
├── asr.py             # Whisper ASR 识别与去重
├── danmaku_clean.py   # 弹幕清洗
├── proofread.py       # LLM 辅助 ASR 校对
├── translate.py       # LLM 翻译
├── main.py            # 入口：串联全流程，输出 SRT
└── requirements.txt
```

---

## 快速开始

### 1. 环境

推荐 Google Colab（已预装 CUDA / torch ）。

```bash
pip install -r requirements.txt
```

### 2. 参数配置

编辑 `config.py`，按需调整：

| 参数 | 说明 | 默认值 |
|---|---|---|
| `OPENAI_BASE_URL` | API 代理地址（免费例：GPT_API_free） | `https://api.chatanywhere.tech/v1` |
| `MODEL_NAME` | 使用的模型 | `gpt-5.2` |（600轴字幕的视频大概10万token左右消耗，示例中的免费版目前上限4k，且有调用次数限制。）
| `MAX_WORKERS` | 并发翻译线程数 | `4` |
| `RETRY_MAX_ATTEMPTS` | API 失败重试次数 | `3` |
| `WHISPER_MODEL_SIZE` | Whisper 模型规格 | `large-v3` |
| `VAD_PARAMS` | VAD 静音检测参数 | 见文件 |
| `MAX_CHARS_PER_CHUNK` | 单次翻译最大字符数 | `3000` |
| `PROOFREAD_BATCH_SIZE` | 单批校对轴数 | `100` |

### 3. 运行

```bash
python main.py
```

运行后依次提示：
1. 输入 API Key
2. 输入配信者信息（用于校对上下文）
3. 上传音频文件
4. 上传弹幕 JSON 文件

完成后自动下载 `<音频文件名>_bilingual.srt`。

---

## 输入格式

**音频**：faster-whisper 支持的格式（mp3、m4a、wav、mp4 等音频）

**弹幕 JSON**：YouTube 直播回放弹幕，每行一条 JSON，格式示例：
```json
{"replayChatItemAction": {"actions": [{"addChatItemAction": {"item": {"liveChatTextMessageRenderer": {"timestampText": {"simpleText": "1:23"}, "message": {"runs": [{"text": "弹幕内容"}]}}}}}]}}
```
一般使用 [yt-dlp](https://github.com/yt-dlp/yt-dlp) 获取。

---

## 输出格式

标准 SRT，每条字幕包含日文原文和中文译文双行：

```
1
00:00:03,120 --> 00:00:05,880
今日も来てくれてありがとう！
今天也谢谢大家来看直播！

2
00:00:06,200 --> 00:00:09,440
...
```

---

## 依赖

| 库 | 用途 |
|---|---|
| `faster-whisper` | ASR 识别 |
| `rapidfuzz` | 清洗低参考度弹幕 |
| `openai` | LLM 调用 |
| `tenacity` | API 重试 |
| `torch` | GPU 推理后端 |


## 注意

**本项目代码由 AI 辅助生成**

本项目所实现srt主要用作是能够极大提高校对效率，不保证0人工级的效果。不懂日语慎用。

*重要前提* 
1. 你需要拥有能够链接youtube的网络。
2. 你需要注册Google colab的账号（有Google账号即可注册）。
3. 你需要有大语言模型的API，例子中使用[GPT_API_free](https://github.com/chatanywhere/GPT_API_free)。3.1. api的使用需要消耗token费用，token费用受轴数量和弹幕数量影响。（600轴，1600清洗后弹幕，token消耗约1.5元）3.2.[GPT_API_free](https://github.com/chatanywhere/GPT_API_free)以外的api需要改动可调参数文件里的base_url，不适用下方的超快运行方法。
4. 当用户不提供弹幕json文件时，输入在询问框no即可得到一般无校对的AI轴翻结果。可以用来对比一下本工作的含校对版。
 

*超快运行方法*：直接在你的顶部搜索栏复制粘贴以下两个链接

https://githubtocolab.com/ushi-C/jpVTuberlivesrtja-zh-allAItool/blob/main/run.ipynb

右上角连接选择更改运行时，选择T4 GPU。然后点击左上的全部运行，按要求输入 **API** 和上传 **音频** 和 **弹幕** 文件。（GPU免费时长有限，超过2h的音频慎重）

简易的直播音频和弹幕下载方法（不需要开启T4）

https://githubtocolab.com/ushi-C/jpVTuberlivesrtja-zh-allAItool/blob/main/audio_danmaku_download.ipynb
