"""Sinh bộ dữ liệu OCR tổng hợp.

Dùng:  python3 ocr_synth/generate.py --n 3000 --out synth_data
Kết quả:
  synth_data/images/pages/*.jpg     ảnh cả trang (đã thêm nhiễu)
  synth_data/images/blocks/*.jpg    ảnh từng vùng chữ (khớp với input crop của pipeline PaddleOCR-VL)
  synth_data/{train,val}.jsonl      {"image", "text", "level", "template", "aug"}
"""
import argparse
import json
import os
import random
import sys
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from templates import TEMPLATES  # noqa: E402
from render import augment, text_of, norm  # noqa: E402

MAX_SIDE = 1280


def resize(img, m=MAX_SIDE):
    s = m / max(img.size)
    return img.resize((round(img.width * s), round(img.height * s))) if s < 1 else img


def make(args):
    i, out, seed, blocks_per_page = args
    random.seed(seed * 1_000_003 + i)
    names, ws = zip(*[(k, w) for k, (_, w) in TEMPLATES.items()])
    tname = random.choices(names, ws)[0]
    page = TEMPLATES[tname][0]()
    recs = []
    mode = random.choices(["clean", "scan", "photo"], [0.15, 0.55, 0.30])[0]
    img = resize(augment(page.img, mode))
    rel = f"images/pages/{i:06d}.jpg"
    img.save(os.path.join(out, rel), quality=92)
    recs.append({"image": rel, "text": text_of(page), "level": "page", "template": tname, "aug": mode, "doc": i})
    cand = [b for b in page.blocks if b[2] != "sign" or random.random() < .3]
    for j, (bbox, text, kind) in enumerate(random.sample(cand, min(blocks_per_page, len(cand)))):
        x0, y0, x1, y1 = bbox
        pad = random.randint(2, 14)
        crop = page.img.crop((max(0, x0 - pad), max(0, y0 - pad), x1 + pad, y1 + pad))
        cm = random.choices(["clean", "scan"], [0.3, 0.7])[0]
        crop = resize(augment(crop, cm))
        rel = f"images/blocks/{i:06d}_{j:02d}.jpg"
        crop.save(os.path.join(out, rel), quality=92)
        recs.append({"image": rel, "text": norm(text), "level": "block", "template": tname, "aug": cm, "doc": i})
    return recs


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3000, help="số trang")
    ap.add_argument("--out", default="synth_data")
    ap.add_argument("--seed", type=int, default=0)
    ap.add_argument("--blocks", type=int, default=4, help="số crop vùng chữ mỗi trang")
    ap.add_argument("--val", type=float, default=0.05)
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    a = ap.parse_args()
    for d in ("images/pages", "images/blocks"):
        os.makedirs(os.path.join(a.out, d), exist_ok=True)
    jobs = [(i, a.out, a.seed, a.blocks) for i in range(a.n)]
    nval = int(a.n * a.val)
    with Pool(a.workers) as pool, open(os.path.join(a.out, "train.jsonl"), "w") as tr, \
            open(os.path.join(a.out, "val.jsonl"), "w") as va:
        for k, recs in enumerate(pool.imap(make, jobs, chunksize=8)):
            f = va if recs[0]["doc"] < nval else tr  # chia theo trang: block cùng trang đi cùng split
            for r in recs:
                f.write(json.dumps(r, ensure_ascii=False) + "\n")
            if (k + 1) % 200 == 0:
                print(f"{k + 1}/{a.n}", flush=True)
    print("xong:", a.out)


if __name__ == "__main__":
    main()
