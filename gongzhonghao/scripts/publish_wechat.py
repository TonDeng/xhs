#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微信公众号自动发布脚本（发布推文到草稿箱）
用法:
  python publish_wechat.py --appid APPID --secret SECRET \
      --title "标题" --content article.html --cover cover.jpg

流程:
  1. 获取 access_token
  2. 上传封面图 -> thumb_media_id
  3. 新建草稿（draft/add）-> 返回 media_id（草稿）
发布后到公众号后台「草稿箱」确认并群发。
"""
import argparse
import json
import sys
import time
import urllib.request
import urllib.parse
import uuid
import os

# 强制 UTF-8 输出，避免 Windows GBK 编码错误
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

API = "https://api.weixin.qq.com"


def http_json(url, data=None, method="GET", files=None, timeout=30):
    if files:
        # multipart/form-data 上传（media 素材）
        boundary = "----WebKitFormBoundary" + uuid.uuid4().hex
        body = b""
        for name, (fname, content, ctype) in files.items():
            body += ("--%s\r\nContent-Disposition: form-data; name=\"%s\"; filename=\"%s\"\r\nContent-Type: %s\r\n\r\n" % (
                boundary, name, fname, ctype)).encode("utf-8")
            body += content + b"\r\n"
        body += ("--%s--\r\n" % boundary).encode("utf-8")
        req = urllib.request.Request(url, data=body, method="POST")
        req.add_header("Content-Type", "multipart/form-data; boundary=" + boundary)
    else:
        data_b = None
        if data is not None:
            data_b = json.dumps(data, ensure_ascii=False).encode("utf-8")
            if method == "GET":
                method = "POST"  # 传了 body 就必须 POST
        req = urllib.request.Request(url, data=data_b, method=method)
        if data is not None:
            req.add_header("Content-Type", "application/json; charset=utf-8")
    try:
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8")
    except Exception as e:
        print("HTTP ERROR:", e)
        sys.exit(1)
    return json.loads(raw)


def get_token(appid, secret):
    url = "%s/cgi-bin/token?grant_type=client_credential&appid=%s&secret=%s" % (API, appid, secret)
    r = http_json(url)
    if "access_token" not in r:
        print("获取 token 失败:", r)
        sys.exit(1)
    print("access_token 获取成功")
    return r["access_token"]


def upload_cover(token, cover_path):
    if not cover_path or not os.path.exists(cover_path):
        print("警告: 封面图不存在，跳过上传（草稿将无封面）")
        return None
    with open(cover_path, "rb") as f:
        content = f.read()
    fname = os.path.basename(cover_path)
    ctype = "image/jpeg" if fname.lower().endswith((".jpg", ".jpeg")) else "image/png"
    url = "%s/cgi-bin/material/add_material?access_token=%s&type=image" % (API, token)
    r = http_json(url, files={"media": (fname, content, ctype)})
    if "media_id" not in r:
        print("上传封面失败:", r)
        return None
    print("封面图上传成功 thumb_media_id:", r["media_id"])
    return r["media_id"]


def add_draft(token, title, content_html, thumb_media_id, author="", digest="", source_url=""):
    url = "%s/cgi-bin/draft/add?access_token=%s" % (API, token)
    article = {
        "title": title,
        "author": author,
        "digest": digest,
        "content": content_html,
        "content_source_url": source_url,   # 阅读原文链接（测试页 URL）
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    if thumb_media_id:
        article["thumb_media_id"] = thumb_media_id
    r = http_json(url, data={"articles": [article]}, method="POST")
    if "media_id" not in r:
        print("新建草稿失败:", r)
        sys.exit(1)
    print("草稿创建成功 media_id:", r["media_id"])
    return r["media_id"]


def update_draft(token, media_id, index, title, content_html, thumb_media_id, author="", digest="", source_url=""):
    url = "%s/cgi-bin/draft/update?access_token=%s" % (API, token)
    article = {
        "title": title,
        "author": author,
        "digest": digest,
        "content": content_html,
        "content_source_url": source_url,
        "need_open_comment": 1,
        "only_fans_can_comment": 0,
    }
    if thumb_media_id:
        article["thumb_media_id"] = thumb_media_id
    r = http_json(url, data={"media_id": media_id, "index": index, "articles": article}, method="POST")
    if r.get("errcode", 0) != 0:
        print("更新草稿失败:", r)
        sys.exit(1)
    print("草稿更新成功 media_id:", media_id)
    return media_id


def main():
    ap = argparse.ArgumentParser(description="发布/更新公众号草稿箱推文")
    ap.add_argument("--appid", required=True)
    ap.add_argument("--secret", required=True)
    ap.add_argument("--title", required=True)
    ap.add_argument("--content", required=True, help="HTML 内容文件路径")
    ap.add_argument("--cover", default="")
    ap.add_argument("--author", default="每天一个测试")
    ap.add_argument("--digest", default="")
    ap.add_argument("--update", default="", help="已有草稿 media_id，更新该草稿（index 0）")
    ap.add_argument("--source-url", default="", help="阅读原文链接（测试页 URL，公众号正文外链会被剥离，需用原文链接）")
    args = ap.parse_args()

    with open(args.content, "r", encoding="utf-8") as f:
        content_html = f.read()

    token = get_token(args.appid, args.secret)
    thumb = upload_cover(token, args.cover) if (args.cover and not args.update) else (upload_cover(token, args.cover) if args.cover else None)
    if args.update:
        update_draft(token, args.update, 0, args.title, content_html, thumb, args.author, args.digest, args.source_url)
        print("=== 草稿已更新，去公众号后台「草稿箱」查看 ===")
        print("media_id:", args.update)
    else:
        media_id = add_draft(token, args.title, content_html, thumb, args.author, args.digest, args.source_url)
        print("")
        print("=== 发布成功，去公众号后台「草稿箱」查看 ===")
        print("media_id:", media_id)


if __name__ == "__main__":
    main()
