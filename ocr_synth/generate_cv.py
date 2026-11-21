"""Sinh dữ liệu train cho pipeline thuần CV PaddleOCR (PP-OCRv5 det + rec).

Dùng:  python3 ocr_synth/generate_cv.py --n 3000 --out synth_cv
Kết quả (định dạng label của PaddleOCR):
  synth_cv/det/images/*.jpg  + det/{train,val}.txt   "<path>\t[{"transcription": ..., "points": [[x,y]x4]}, ...]"
  synth_cv/rec/images/*.jpg  + rec/{train,val}.txt   "<path>\t<text>"
  synth_cv/dict.txt          bảng ký tự (mỗi dòng 1 ký tự, NFC) xuất hiện trong nhãn rec
Đường dẫn trong file label là tương đối so với synth_cv/det hoặc synth_cv/rec (đặt data_dir tương ứng trong config).
"""
import argparse
import json
import os
import random
import sys
import unicodedata
from multiprocessing import Pool

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from templates import TEMPLATES  # noqa: E402
from render import augment_tracked, augment_line, norm  # noqa: E402

MAX_SIDE = 1280


def make(job):
    i, out, seed, line_frac = job
    random.seed(seed * 1_000_003 + i)
    names, ws = zip(*[(k, w) for k, (_, w) in TEMPLATES.items()])
    tname = random.choices(names, ws)[0]
    page = TEMPLATES[tname][0]()
    lines = [(b, unicodedata.normalize("NFC", norm(t))) for b, t, _ in page.lines]
    lines = [(b, t) for b, t in lines if t]

    # ---- det: cả trang + 4 góc mỗi dòng sau biến đổi ----
    mode = random.choices(["clean", "scan", "photo"], [0.15, 0.55, 0.30])[0]
    img, f = augment_tracked(page.img, mode)
    s = min(1.0, MAX_SIDE / max(img.size))
    if s < 1:
        img = img.resize((round(img.width * s), round(img.height * s)))
    W, H = img.size
    ann = []
    for (x0, y0, x1, y1), t in lines:
        pad = 3
        pts = [f(x0 - pad, y0 - pad), f(x1 + pad, y0 - pad), f(x1 + pad, y1 + pad), f(x0 - pad, y1 + pad)]
        pts = [[min(W - 1, max(0, round(x * s))), min(H - 1, max(0, round(y * s)))] for x, y in pts]
        ann.append({"transcription": t, "points": pts})
    det_rel = f"images/{i:06d}.jpg"
    img.save(os.path.join(out, "det", det_rel), quality=90)
    det_line = f"{det_rel}\t{json.dumps(ann, ensure_ascii=False)}"

    # ---- rec: crop từng dòng từ trang sạch (có dấu/chữ ký đè), nhiễu riêng ----
    rec = []
    for k, ((x0, y0, x1, y1), t) in enumerate(lines):
        if random.random() > line_frac:
            continue
        h = y1 - y0
        px, pt_, pb = random.randint(2, 12), random.randint(1, max(2, h // 4)), random.randint(1, max(2, h // 4))
        dy = random.randint(-max(1, h // 10), max(1, h // 10))  # lệch khung như detector thật
        crop = page.img.crop((max(0, x0 - px), max(0, y0 - pt_ + dy), x1 + px, y1 + pb + dy))
        crop, _ = augment_line(crop)
        rel = f"images/{i:06d}_{k:03d}.jpg"
        crop.save(os.path.join(out, "rec", rel), quality=90)
        rec.append(f"{rel}\t{t}")
    return i, det_line, rec, {c for _, t in lines for c in t}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=3000)
    ap.add_argument("--out", default="synth_cv")
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--val", type=float, default=0.05)
    ap.add_argument("--line-frac", type=float, default=1.0, help="tỷ lệ dòng mỗi trang đưa vào rec")
    ap.add_argument("--workers", type=int, default=os.cpu_count())
    a = ap.parse_args()
    for d in ("det/images", "rec/images"):
        os.makedirs(os.path.join(a.out, d), exist_ok=True)
    nval = int(a.n * a.val)
    files = {k: open(os.path.join(a.out, k.replace("_", "/") + ".txt"), "w", encoding="utf-8")
             for k in ("det_train", "det_val", "rec_train", "rec_val")}
    chars = set()
    with Pool(a.workers) as pool:
        for c, (i, det, rec, ch) in enumerate(pool.imap(make, [(i, a.out, a.seed, a.line_frac) for i in range(a.n)], chunksize=8)):
            sp = "val" if i < nval else "train"  # chia theo trang
            files[f"det_{sp}"].write(det + "\n")
            for r in rec:
                files[f"rec_{sp}"].write(r + "\n")
            chars |= ch
            if (c + 1) % 200 == 0:
                print(f"{c + 1}/{a.n}", flush=True)
    for fh in files.values():
        fh.close()
    chars.discard(" ")
    with open(os.path.join(a.out, "dict.txt"), "w", encoding="utf-8") as fo:
        fo.write("\n".join(sorted(chars)) + "\n")
    print("xong:", a.out, "| số ký tự:", len(chars))


if __name__ == "__main__":
    main()
