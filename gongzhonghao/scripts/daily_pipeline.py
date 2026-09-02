#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
公众号「每天一个测试」自动推文流水线
每天自动：从题库选题 → 生成推文 Markdown（无收费字眼）→ 转微信 HTML → 发布到公众号草稿箱 → 记日志

用法:
  python daily_pipeline.py                     # 自动选题（按日期轮换题库）并发布
  python daily_pipeline.py --dry-run           # 只生成不发布（预览）
  python daily_pipeline.py --question qid      # 指定题库 id 生成
  python daily_pipeline.py --force             # 强制重新生成（跳过今日已发布检查）

配置: scripts/config.local.json (不入库)
  {"appid": "...", "secret": "...", "gzh": "每天一个测试"}
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import subprocess
import sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
QUESTIONS_DIR = os.path.join(BASE, "questions")
OUTPUT_DIR = os.path.join(BASE, "output")
LOGS_DIR = os.path.join(BASE, "logs")
SCRIPTS_DIR = os.path.join(BASE, "scripts")
CONFIG_PATH = os.path.join(SCRIPTS_DIR, "config.local.json")

TEST_URL = "https://tondeng.github.io/xhs/?gzh=每天一个测试"


def log(msg):
    line = "[%s] %s" % (datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), msg)
    print(line)
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(os.path.join(LOGS_DIR, "pipeline.log"), "a", encoding="utf-8") as f:
        f.write(line + "\n")


def load_config():
    if not os.path.exists(CONFIG_PATH):
        return {}
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def list_question_sets():
    """返回按日期排序的题库列表（用于轮换）"""
    sets = []
    for fn in sorted(os.listdir(QUESTIONS_DIR)):
        if fn.endswith(".json"):
            try:
                with open(os.path.join(QUESTIONS_DIR, fn), "r", encoding="utf-8") as f:
                    sets.append(json.load(f))
            except Exception as e:
                log("题库 %s 解析失败: %s" % (fn, e))
    return sets


# ---------- 发布历史（避免主题重复） ----------
HISTORY_FILE = os.path.join(LOGS_DIR, "history.json")


def load_history():
    """返回 {qid: [date1, date2, ...]} 发布历史"""
    if not os.path.exists(HISTORY_FILE):
        return {}
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_history(history):
    os.makedirs(LOGS_DIR, exist_ok=True)
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)


def record_publish(qid, date_str):
    history = load_history()
    history.setdefault(qid, []).append(date_str)
    save_history(history)


def pick_question(dry_date=None):
    """
    选题策略：优先选从未发布过的题库；
    若全部发布过，选距离上次发布最久远的题库（最大化间隔，避免近期重复）。
    """
    sets = list_question_sets()
    if not sets:
        raise RuntimeError("题库为空，请先在 questions/ 目录添加题库 JSON")
    d = dry_date or datetime.date.today()
    d_str = d.isoformat()
    history = load_history()

    # 1) 从未发布过的题库
    never_published = [s for s in sets if s["id"] not in history]
    if never_published:
        # 按题库文件顺序取第一个未发布过的
        return never_published[0], sets.index(never_published[0])

    # 2) 全部发过：选距离上次发布最久远的
    def last_gap(s):
        dates = history.get(s["id"], [])
        last = dates[-1]
        return (d - datetime.date.fromisoformat(last)).days

    # 最久未发布的优先（间隔最大）；同间隔按题库顺序
    chosen = max(sets, key=lambda s: (last_gap(s), -sets.index(s)))
    return chosen, sets.index(chosen)


def build_markdown(qset, date):
    """生成推文 Markdown（无收费字眼）"""
    title = qset["title"]
    md = []
    md.append("# %s" % title)
    md.append("")
    md.append(qset["hook"])
    md.append("")
    md.append("《%s》—— 几个小问题，凭第一直觉作答，约 3 分钟。完全免费。" % qset["topic"])
    md.append("")
    for q in qset["questions"]:
        md.append("**%s**" % q["scene"])
        md.append(q["text"])
        md.append("")
        for opt in q["opts"]:
            md.append("- %s" % opt)
        md.append("")
    md.append("选 A、选 B，还是选 D？你的选择，暴露了你真实的内心。")
    md.append("")
    md.append("🌟 测试没有对错，只有了解。来测一测，认识更真实的自己。")
    md.append("")
    md.append("**👉 点这里，免费完成完整测试：**")
    md.append("")
    md.append("[立即免费测试](%s)" % TEST_URL)
    md.append("")
    md.append("（点击上方链接，或公众号菜单「免费测试」）")
    md.append("")
    md.append("📋 **测试内容**")
    md.append("- ✅ 几道情境题，凭第一直觉作答，约 3 分钟（**免费**）")
    md.append("- ✅ 立即获得你的专属结果解读（**免费**）")
    md.append("")
    md.append("你的结果是哪一种？评论区告诉我 👇")
    md.append("")
    md.append("---")
    md.append("**如何测试：**")
    md.append("")
    md.append("1. 点击上方「测试入口」按钮（或公众号菜单「免费测试」）")
    md.append("2. 免费完成测试，立即获得完整结果解读")
    md.append("3. 觉得准？分享给朋友，一起测一测 🎉")
    md.append("")
    md.append("> 📌 测试结果仅供自我探索与娱乐参考")
    md.append("> 📌 本测试完全免费，祝你好运！")
    md.append("")
    md.append("<!-- 来源: %s -->" % qset.get("source", ""))
    return "\n".join(md)


def md2html(md_path, html_path):
    """调用 md2wechat.py 转换"""
    r = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS_DIR, "md2wechat.py"), md_path, html_path],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    if r.returncode != 0:
        raise RuntimeError("md2wechat 失败: %s" % r.stderr[-500:])
    return html_path


def publish(appid, secret, title, html_path, cover, digest):
    """调用 publish_wechat.py 发布到草稿箱"""
    r = subprocess.run(
        [sys.executable, os.path.join(SCRIPTS_DIR, "publish_wechat.py"),
         "--appid", appid, "--secret", secret,
         "--title", title, "--content", html_path,
         "--cover", cover, "--digest", digest],
        capture_output=True, text=True, encoding="utf-8", errors="replace"
    )
    out = r.stdout + r.stderr
    if "草稿创建成功" not in out:
        raise RuntimeError("发布失败: %s" % out[-600:])
    m = re.search(r"media_id:\s*(\S+)", out)
    return m.group(1) if m else "unknown"


def today_marker():
    return datetime.date.today().isoformat()


def already_done_today():
    marker = os.path.join(LOGS_DIR, "last_publish.txt")
    if not os.path.exists(marker):
        return False
    with open(marker, "r", encoding="utf-8") as f:
        return f.read().strip() == today_marker()


def mark_done(question_id):
    with open(os.path.join(LOGS_DIR, "last_publish.txt"), "w", encoding="utf-8") as f:
        f.write("%s|%s" % (today_marker(), question_id))
    record_publish(question_id, today_marker())


def generate_cover(qset, out_path):
    """按题库主题生成封面（调用 generate_cover.py，用 Anaconda Python 因有 PIL）"""
    qset_path = os.path.join(QUESTIONS_DIR, qset["id"] + ".json")
    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    # 优先 Anaconda Python（有 PIL）
    py_candidates = [
        r"D:\Users\22129\Anaconda3\python.exe",
        sys.executable,
    ]
    for py in py_candidates:
        if not os.path.exists(py):
            continue
        r = subprocess.run(
            [py, os.path.join(SCRIPTS_DIR, "generate_cover.py"), qset_path, out_path],
            capture_output=True, text=True, encoding="utf-8", errors="replace"
        )
        if r.returncode == 0 and os.path.exists(out_path):
            return out_path
        log("封面生成尝试失败(%s): %s" % (py, r.stderr[-200:]))
    raise RuntimeError("封面生成失败")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true", help="只生成不发布")
    ap.add_argument("--question", default="", help="指定题库 id")
    ap.add_argument("--force", action="store_true", help="跳过今日已发布检查")
    args = ap.parse_args()

    if not args.force and already_done_today() and not args.question and not args.dry_run:
        with open(os.path.join(LOGS_DIR, "last_publish.txt"), "r", encoding="utf-8") as f:
            prev = f.read().strip()
        log("今天已发布过（%s），跳过。如需重发加 --force" % prev)
        return

    qset, idx = pick_question()
    if args.question:
        for s in list_question_sets():
            if s["id"] == args.question:
                qset = s
                break
        else:
            raise RuntimeError("未找到题库: %s" % args.question)

    today = datetime.date.today()
    md = build_markdown(qset, today)
    date_str = today.strftime("%Y%m%d")
    md_path = os.path.join(OUTPUT_DIR, "%s-%s.md" % (date_str, qset["id"]))
    html_path = os.path.join(OUTPUT_DIR, "%s-%s.html" % (date_str, qset["id"]))
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md)
    md2html(md_path, html_path)
    log("已生成推文: %s (题库: %s, 话题: %s)" % (md_path, qset["id"], qset["topic"]))

    if args.dry_run:
        log("dry-run 模式，未发布。")
        return

    cfg = load_config()
    if not cfg.get("appid") or not cfg.get("secret"):
        raise RuntimeError("缺少凭据：请创建 %s 填入 appid/secret" % CONFIG_PATH)

    # 按当天题库主题生成动态封面
    cover = os.path.join(OUTPUT_DIR, "covers", "%s-%s.png" % (date_str, qset["id"]))
    try:
        generate_cover(qset, cover)
        log("已生成主题封面: %s" % cover)
    except Exception as e:
        cover = os.path.join(BASE, "notes", "img", "头图-900x383.png")
        log("主题封面生成失败，回退默认封面: %s" % e)

    digest = "免费测试：%s。凭第一直觉作答，立即获得完整结果解读，完全免费。" % qset["topic"]
    media_id = publish(cfg["appid"], cfg["secret"], qset["title"], html_path, cover, digest)
    mark_done(qset["id"])
    log("已发布到草稿箱 media_id=%s" % media_id)
    log("=== 完成，去公众号后台「草稿箱」确认并群发 ===")


if __name__ == "__main__":
    main()
