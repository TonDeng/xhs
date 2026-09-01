#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""验证公众号草稿箱最新草稿内容，检查收费字眼"""
import json
import sys
import urllib.request

# 强制 UTF-8 输出，避免 Windows GBK 编码错误
sys.stdout.reconfigure(encoding="utf-8", errors="replace")
sys.stderr.reconfigure(encoding="utf-8", errors="replace")

API = "https://api.weixin.qq.com"

def http_json(url, data=None, method="GET", timeout=30):
    data_b = json.dumps(data, ensure_ascii=False).encode("utf-8") if data is not None else None
    req = urllib.request.Request(url, data=data_b, method=method)
    if data_b is not None:
        req.add_header("Content-Type", "application/json; charset=utf-8")
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode("utf-8"))

def main():
    appid, secret = sys.argv[1], sys.argv[2]
    r = http_json("%s/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (API, appid, secret))
    token = r["access_token"]

    # 获取草稿列表
    r = http_json("%s/cgi-bin/draft/batchget?access_token=%s" % (API, token),
                  data={"offset": 0, "count": 3, "no_content": 0}, method="POST")
    if "item_count" not in r or r["item_count"] == 0:
        print("草稿列表为空或接口异常:", json.dumps(r, ensure_ascii=False)[:500])
        return
    item = r["item"][0]
    art = item["content"]["news_item"][0]
    print("== 最新草稿 ==")
    print("media_id:", item.get("media_id"))
    print("标题:", art.get("title"))
    print("摘要:", art.get("digest"))
    c = art.get("content", "")
    for kw in ["8.88", "¥", "付款", "付费", "收费", "解锁", "购买", "支付"]:
        print("正文含 '%s': %s" % (kw, kw in c))
    print("正文含 '下载完整报告':", "下载完整报告" in c)
    print("测试链接存在:", "tondeng.github.io/xhs" in c)
    print("正文长度:", len(c))

if __name__ == "__main__":
    main()
