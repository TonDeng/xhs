#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Markdown -> 微信公众号 HTML 转换（美化版）
- 金色主题排版：大标题、场景卡片、选项列表、按钮式测试链接
- 测试链接（单独成段的 [text](url)）渲染为可点击大按钮
- 内联样式（公众号编辑器兼容）
用法: python md2wechat.py input.md output.html
"""
import argparse
import re
import sys

# 强制 UTF-8 输出，避免 Windows GBK 编码错误
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

GOLD = "#c9a961"
GOLD2 = "#e8cf9a"
DARK = "#17120a"
TEXT = "#3b3b3b"
MUTED = "#888"


def escape(text):
    return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def inline(md, in_link=False):
    """行内元素渲染；in_link=True 时链接文本只显示文字（按钮场景）"""
    md = escape(md)
    md = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", md)
    md = re.sub(r"\*(.+?)\*", r"<em>\1</em>", md)
    md = re.sub(r"`(.+?)`", r"<code style=\"background:#f5f5f5;padding:2px 6px;border-radius:4px;font-size:0.9em;color:#c07a2a\">\1</code>", md)
    if not in_link:
        # 链接 [text](url) -> 金色带下划线链接
        md = re.sub(
            r"\[([^\]]+)\]\((https?://[^)\s]+)\)",
            r'<a href="\2" style="color:#c07a2a;text-decoration:none;border-bottom:1px solid #c07a2a">\1</a>',
            md,
        )
    return md


def render_button(text, url, emoji="👉"):
    """金色渐变大按钮（可点击标签）"""
    return (
        '<section style="text-align:center;margin:26px 0">'
        '<a href="%s" style="display:inline-block;background:linear-gradient(135deg,%s,#a8843f);'
        'color:%s;font-size:17px;font-weight:bold;letter-spacing:2px;padding:15px 46px;'
        'border-radius:50px;text-decoration:none;box-shadow:0 6px 18px rgba(201,169,97,.35);'
        '-webkit-tap-highlight-color:transparent">%s %s</a>'
        "</section>" % (url, GOLD2, DARK, emoji, text)
    )


def render_scene_header(text):
    """场景标题：金色左侧条 + 深色底标签"""
    return (
        '<section style="display:flex;align-items:center;margin:22px 0 6px">'
        '<span style="display:inline-block;width:4px;height:20px;background:linear-gradient(180deg,%s,%s);border-radius:2px;margin-right:8px"></span>'
        '<strong style="font-size:16px;color:#17120a;background:linear-gradient(90deg,rgba(232,207,154,.35),rgba(201,169,97,.12));'
        'padding:5px 14px;border-radius:6px;letter-spacing:1px">%s</strong>'
        "</section>" % (GOLD2, GOLD, text)
    )


def convert(md_text):
    lines = md_text.split("\n")
    out = []
    i = 0
    in_code = False
    while i < len(lines):
        line = lines[i]
        if line.strip().startswith("```"):
            in_code = not in_code
            i += 1
            continue
        if in_code:
            out.append('<pre style="background:#f6f8fa;padding:12px;border-radius:8px;font-size:13px;overflow-x:auto">%s</pre>' % escape(line))
            i += 1
            continue
        s = line.strip()

        # 分隔线
        if s == "---" or s == "***":
            out.append('<hr style="border:none;height:1px;background:linear-gradient(90deg,transparent,%s,transparent);margin:26px 0">' % GOLD)
            i += 1
            continue

        # 标题
        m = re.match(r"^(#{1,4})\s+(.*)$", s)
        if m:
            lvl = len(m.group(1))
            txt = inline(m.group(2))
            if lvl == 1:
                # 大标题：金色渐变 + 底部装饰线
                out.append(
                    '<h1 style="text-align:center;font-size:24px;font-weight:bold;color:#17120a;'
                    'background:linear-gradient(180deg,%s,%s);-webkit-background-clip:text;background-clip:text;'
                    '-webkit-text-fill-color:transparent;margin:28px 0 6px;letter-spacing:1px">%s</h1>'
                    '<section style="width:56px;height:3px;background:linear-gradient(90deg,%s,%s);border-radius:2px;margin:0 auto 20px"></section>'
                    % (GOLD2, GOLD, txt, GOLD2, GOLD)
                )
            elif lvl == 2:
                out.append('<h2 style="font-size:19px;font-weight:bold;color:#17120a;margin:26px 0 12px">%s</h2>' % txt)
            else:
                size = {3: "16px", 4: "15px"}[lvl]
                out.append('<h%d style="font-size:%s;font-weight:bold;color:#17120a;margin:20px 0 10px">%s</h%d>' % (lvl, size, txt, lvl))
            i += 1
            continue

        # 引用
        if s.startswith(">"):
            quoted = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quoted.append(inline(lines[i].strip()[1:].strip()))
                i += 1
            out.append(
                '<blockquote style="border-left:4px solid %s;background:#faf7f0;padding:12px 16px;'
                'color:#8a7a55;margin:16px 0;border-radius:0 8px 8px 0;font-size:14px">%s</blockquote>'
                % (GOLD, "<br>".join(quoted))
            )
            continue

        # 场景标题（**场景一 · xxx** 单独成行）
        m2 = re.match(r"^\*\*(场景[^*]+)\*\*$", s)
        if m2:
            out.append(render_scene_header(m2.group(1)))
            i += 1
            continue

        # 按钮：单独成段的 [text](url)（含 "测试入口/测试/点这里" 等关键词）
        m3 = re.match(r"^\[([^\]]+)\]\((https?://[^)\s]+)\)$", s)
        if m3:
            out.append(render_button(m3.group(1), m3.group(2)))
            i += 1
            continue

        # 列表（无序号）
        if s.startswith(("- ", "* ", "+ ")):
            items = []
            while i < len(lines):
                ls = lines[i].strip()
                m = re.match(r"^[-*+]\s+(.*)$", ls)
                if m:
                    items.append(
                        '<li style="font-size:15px;color:%s;line-height:1.9;padding:4px 0">'
                        '<span style="color:%s;margin-right:6px">▸</span>%s</li>' % (TEXT, GOLD, inline(m.group(1)))
                    )
                    i += 1
                else:
                    break
            out.append('<ul style="margin:10px 0;padding-left:8px;list-style:none">%s</ul>' % "".join(items))
            continue

        # 列表（有序）
        if re.match(r"^\d+[.、)]\s+", s):
            items = []
            while i < len(lines):
                ls = lines[i].strip()
                m = re.match(r"^\d+[.、)]\s+(.*)$", ls)
                if m:
                    items.append('<li style="font-size:15px;color:%s;line-height:1.9;padding:4px 0">%s</li>' % (TEXT, inline(m.group(1))))
                    i += 1
                else:
                    break
            out.append('<ol style="margin:10px 0;padding-left:22px;color:%s">%s</ol>' % (GOLD, "".join(items)))
            continue

        # 空行
        if s == "":
            i += 1
            continue

        # 段落（合并连续非空行；段落中仅含链接则渲染为按钮）
        para = [s]
        i += 1
        while i < len(lines) and lines[i].strip() != "" and not lines[i].strip().startswith(("#", "- ", "* ", "+ ", ">", "```", "---")) and not re.match(r"^\d+[.、)]\s+", lines[i].strip()):
            para.append(lines[i].strip())
            i += 1
        # 判断是否为独立链接段（渲染为按钮）
        joined = " ".join(para)
        m4 = re.match(r"^(?:[👉点这里测试入口：\s]*)\[([^\]]+)\]\((https?://[^)\s]+)\)[\s]*$", joined)
        if m4 and len(para) <= 2:
            out.append(render_button(m4.group(1), m4.group(2)))
            continue
        out.append('<p style="font-size:15px;color:%s;line-height:1.9;margin:12px 0">%s</p>' % (TEXT, "<br>".join(inline(p) for p in para)))
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("input")
    ap.add_argument("output")
    args = ap.parse_args()
    with open(args.input, "r", encoding="utf-8") as f:
        md = f.read()
    html = convert(md)
    full = (
        '<section style="max-width:677px;margin:0 auto;padding:0 16px;font-family:-apple-system,BlinkMacSystemFont,\'Helvetica Neue\',\'PingFang SC\',\'Hiragino Sans GB\',\'Microsoft YaHei\',sans-serif">'
        + html +
        "</section>"
    )
    with open(args.output, "w", encoding="utf-8") as f:
        f.write(full)
    print("已生成:", args.output, "长度:", len(full))


if __name__ == "__main__":
    main()
