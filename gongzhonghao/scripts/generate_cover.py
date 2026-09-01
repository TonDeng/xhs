#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
动态生成公众号推文封面（900×383）
根据题库 JSON 的 cover_title / cover_sub 生成对应主题封面，
每套题库可配置主题色（cover_color，缺省金色）。

用法:
  python generate_cover.py <题库json> <输出png>
  python generate_cover.py questions/qizongzui-v2.json output/covers/qizongzui-v2.png
"""
import json
import os
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

# 尝试 PIL（Anaconda 有）；无则降级说明
try:
    from PIL import Image, ImageDraw, ImageFont
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

W, H = 900, 383

# 字体路径候选
FONT_CANDIDATES = [
    r"C:\Windows\Fonts\msyh.ttc",       # 微软雅黑
    r"C:\Windows\Fonts\msyhbd.ttc",     # 微软雅黑 Bold
    r"C:\Windows\Fonts\simhei.ttf",     # 黑体
    r"C:\Windows\Fonts\Deng.ttf",       # 等线
]


def find_font(size, bold=False):
    names = [r"C:\Windows\Fonts\msyhbd.ttc", r"C:\Windows\Fonts\msyh.ttc",
             r"C:\Windows\Fonts\simhei.ttf", r"C:\Windows\Fonts\Deng.ttf"]
    if bold:
        names = [r"C:\Windows\Fonts\msyhbd.ttc"] + names
    for n in names:
        if os.path.exists(n):
            try:
                return ImageFont.truetype(n, size)
            except Exception:
                continue
    return ImageFont.load_default()


def lerp(a, b, t):
    return int(a + (b - a) * t)


def generate(qset_path, out_path):
    with open(qset_path, "r", encoding="utf-8") as f:
        qset = json.load(f)

    title = qset.get("cover_title", qset.get("topic", "每天一个测试"))
    sub = qset.get("cover_sub", qset.get("desc", "免费开测"))
    # 主题色（可选）：gold 金 / purple 紫 / blue 蓝 / green 绿 / pink 粉
    theme = qset.get("cover_color", "gold")
    palettes = {
        "gold":   ((240, 220, 170), (180, 140, 70), (40, 30, 58), (14, 11, 18)),
        "purple": ((220, 190, 255), (150, 100, 220), (48, 30, 66), (16, 11, 22)),
        "blue":   ((180, 220, 255), (90, 150, 230), (28, 40, 64), (10, 14, 22)),
        "green":  ((190, 240, 210), (90, 180, 130), (26, 46, 38), (9, 16, 13)),
        "pink":   ((255, 210, 225), (220, 120, 160), (58, 30, 44), (20, 11, 16)),
    }
    c1, c2, bg_c, bg_d = palettes.get(theme, palettes["gold"])

    img = Image.new("RGB", (W, H))
    draw = ImageDraw.Draw(img)

    # 背景渐变（深色）
    for y in range(H):
        t = y / H
        r = lerp(bg_c[0], bg_d[0], t)
        g = lerp(bg_c[1], bg_d[1], t)
        b = lerp(bg_c[2], bg_d[2], t)
        draw.line([(0, y), (W, y)], fill=(r, g, b))

    # 底部金色/主题色光带
    for y in range(240, H):
        t = (y - 240) / (H - 240)
        alpha = int(70 * (1 - t))
        r = lerp(255, c1[0], 0.5)
        gg = lerp(255, c1[1], 0.5)
        bb = lerp(255, c1[2], 0.5)
        base_r, base_g, base_b = img.getpixel((450, y))
        nr = lerp(base_r, r, alpha / 255)
        ng = lerp(base_g, gg, alpha / 255)
        nb = lerp(base_b, bb, alpha / 255)
        draw.line([(0, y), (W, y)], fill=(int(nr), int(ng), int(nb)))

    # 右侧装饰：双圆环 + 问号
    ring_color = c1
    import math

    def ring(cx, cy, r_outer, r_inner, color):
        """画圆环：先填充大圆，再用背景色覆盖内圆"""
        draw.ellipse([cx - r_outer, cy - r_outer, cx + r_outer, cy + r_outer], fill=color)
        # 内圆用背景色填充
        inner = Image.new("RGB", (W, H), (0, 0, 0))
        di = ImageDraw.Draw(inner)
        di.ellipse([cx - r_inner, cy - r_inner, cx + r_inner, cy + r_inner], fill=(255, 0, 0))
        px = img.load()
        for yy in range(cy - r_inner, cy + r_inner + 1):
            tt = yy / H
            rr = lerp(bg_c[0], bg_d[0], tt)
            gg = lerp(bg_c[1], bg_d[1], tt)
            bb = lerp(bg_c[2], bg_d[2], tt)
            for xx in range(cx - r_inner, cx + r_inner + 1):
                if inner.getpixel((xx, yy)) == (255, 0, 0):
                    px[xx, yy] = (int(rr), int(gg), int(bb))

    ring(760, 140, 100, 95, ring_color)   # 外环
    # 内虚线环（近似：画多段弧线）
    for a in range(0, 360, 12):
        r1, r2 = 62, 68
        x1 = 760 + r1 * math.cos(math.radians(a))
        y1 = 140 + r1 * math.sin(math.radians(a))
        x2 = 760 + r2 * math.cos(math.radians(a))
        y2 = 140 + r2 * math.sin(math.radians(a))
        draw.line([(x1, y1), (x2, y2)], fill=ring_color, width=2)
    # 中央问号
    fq = find_font(110, bold=True)
    draw.text((760, 140), "?", font=fq, fill=ring_color, anchor="mm")

    # 顶部小字：每天一个测试
    f_kicker = find_font(16)
    draw.text((44, 52), "每 天 一 个 测 试", font=f_kicker, fill=ring_color)

    # 主标题
    f_title = find_font(44, bold=True)
    t_color = (min(255, c1[0] + 20), min(255, c1[1] + 20), min(255, c1[2] + 20))
    draw.text((44, 100), title, font=f_title, fill=t_color)

    # 副标题
    f_sub = find_font(20)
    draw.text((46, 205), sub, font=f_sub, fill=(210, 200, 185))

    # 底部标签
    f_tag = find_font(15)
    draw.text((46, 265), "每日一测 · 免费报告 · 认识自己", font=f_tag, fill=(170, 160, 140))

    os.makedirs(os.path.dirname(out_path), exist_ok=True)
    img.save(out_path, "PNG")
    print("封面已生成:", out_path, "主题:", theme, "标题:", title)


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    if not HAS_PIL:
        print("需要 PIL：请用 Anaconda python 运行 或 pip install pillow")
        sys.exit(1)
    qset_path = sys.argv[1]
    out_path = sys.argv[2]
    generate(qset_path, out_path)


if __name__ == "__main__":
    main()
