# -*- coding: utf-8 -*-
"""为题库 JSON 添加主题色 cover_color"""
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

BASE = r"D:\projects\xhs\gongzhonghao\questions"

# 每套题库主题色：gold金 / purple紫 / blue蓝 / green绿 / pink粉
colors = {
    "sbti-abstract": "purple",     # SBTI 抽象人格 → 神秘紫
    "attachment-style": "pink",    # 恋爱依恋类型 → 温柔粉
    "spending-persona": "green",   # 消费人格 → 清爽绿
    "qizongzui-v2": "gold",        # 七宗罪 → 经典金
}

for fn in os.listdir(BASE):
    if not fn.endswith(".json"):
        continue
    path = os.path.join(BASE, fn)
    with open(path, "r", encoding="utf-8") as f:
        data = json.load(f)
    qid = data.get("id", "")
    if qid in colors:
        data["cover_color"] = colors[qid]
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("已设置主题色:", qid, "->", colors[qid])
    else:
        print("跳过(无配置):", fn)
