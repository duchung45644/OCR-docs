"""Chuyển synth_data/*.jsonl sang định dạng finetune.

  --fmt erniekit : định dạng SFT của ERNIEKit/PaddleFormers cho PaddleOCR-VL
                   {"image_info":[{"matched_text_index":0,"image_url":...}],
                    "text_info":[{"text":"OCR:","tag":"mask"},{"text":<nhãn>,"tag":"no_mask"}]}
  --fmt messages : định dạng chat cho Transformers/TRL/LLaMA-Factory
                   {"messages":[{"role":"user","content":"<image>OCR:"},{"role":"assistant","content":<nhãn>}],"images":[...]}

Kiểm tra lại schema với tài liệu phiên bản công cụ bạn dùng trước khi train.
Dùng: python3 ocr_synth/convert.py synth_data --fmt erniekit [--image-root /kaggle/input/vn-ocr-synth]
"""
import argparse
import json
import os

PROMPT = "OCR:"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("data_dir")
    ap.add_argument("--fmt", choices=["erniekit", "messages"], default="erniekit")
    ap.add_argument("--image-root", default=None, help="tiền tố đường dẫn ảnh trên máy train (vd. Kaggle)")
    ap.add_argument("--level", choices=["all", "page", "block"], default="all")
    a = ap.parse_args()
    root = a.image_root or os.path.abspath(a.data_dir)
    for split in ("train", "val"):
        src = os.path.join(a.data_dir, f"{split}.jsonl")
        dst = os.path.join(a.data_dir, f"{split}_{a.fmt}.jsonl")
        n = 0
        with open(src) as fi, open(dst, "w") as fo:
            for line in fi:
                r = json.loads(line)
                if a.level != "all" and r["level"] != a.level:
                    continue
                img = f"{root.rstrip('/')}/{r['image']}"
                if a.fmt == "erniekit":
                    o = {"image_info": [{"matched_text_index": 0, "image_url": img}],
                         "text_info": [{"text": PROMPT, "tag": "mask"}, {"text": r["text"], "tag": "no_mask"}]}
                else:
                    o = {"messages": [{"role": "user", "content": "<image>" + PROMPT},
                                      {"role": "assistant", "content": r["text"]}], "images": [img]}
                fo.write(json.dumps(o, ensure_ascii=False) + "\n")
                n += 1
        print(dst, n)


if __name__ == "__main__":
    main()
