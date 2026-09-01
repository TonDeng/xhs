# -*- coding: utf-8 -*-
"""为题库 JSON 添加封面字段（cover_title / cover_sub）"""
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = r"D:\projects\xhs\gongzhonghao\questions"

# 每个题库的封面文案（主标题 ≤ 10 字，副标题 ≤ 14 字）
covers = {
    "sbti-abstract": {
        "cover_title": "SBTI 抽象人格",
        "cover_sub": "你是哪种精神状态 · 免费测",
    },
    "attachment-style": {
        "cover_title": "恋爱依恋类型",
        "cover_sub": "你的相处模式是哪种 · 免费测",
    },
    "spending-persona": {
        "cover_title": "消费人格测试",
        "cover_sub": "你是哪种花钱人格 · 免费测",
    },
    "qizongzui-v2": {
        "cover_title": "七宗罪 × 七美德",
        "cover_sub": "测出你的主罪与主德 · 免费测",
    },
}

for fn in os.listdir(BASE):
    if not fn.endswith(".json"):
        continue
    path = os.path.join(BASE, fn)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    qid = data.get("id", "")
    if qid in covers:
        data["cover_title"] = covers[qid]["cover_title"]
        data["cover_sub"] = covers[qid]["cover_sub"]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("已更新:", fn, "->", data["cover_title"], "|", data["cover_sub"])
    else:
        print("跳过(无封面配置):", fn)
