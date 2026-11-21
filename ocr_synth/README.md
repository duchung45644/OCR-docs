# ocr_synth: dữ liệu OCR tổng hợp cho văn bản hành chính

Sinh ảnh văn bản hành chính Hà Nội từ **dữ liệu giả hoàn toàn** (họ tên, CCCD, địa chỉ, số hiệu…).
Không đọc hay sao chép thông tin cá nhân từ hồ sơ thật. Chỉ cần Python 3 + Pillow + font Liberation Serif.

## Mẫu hỗ trợ
| template | tỷ lệ | mô tả |
|---|---|---|
| `tthn` | 50% | Giấy xác nhận tình trạng hôn nhân (5 kiểu tình trạng) |
| `mau02` | 30% | Mẫu số 02 – Giấy xác nhận về điều kiện nhà ở (NOXH) |
| `phieu_dat_dai` | 20% | Phiếu cung cấp thông tin, dữ liệu đất đai (danh sách nhân khẩu) |

Mỗi trang có con dấu đỏ và chữ ký giả đè lên chữ, rồi thêm nhiễu theo 3 chế độ:
`clean` 15% / `scan` 55% (nghiêng, xám, đen trắng, mờ, JPEG) / `photo` 30% (phối cảnh, nền tối, ánh sáng không đều).

## Chạy
```bash
# Pipeline thuần CV (PP-OCRv5 det + rec): đang dùng
python3 ocr_synth/generate_cv.py --n 3000 --out synth_cv
#   synth_cv/det/{train,val}.txt  "<ảnh>\t[{"transcription","points"}]"
#   synth_cv/rec/{train,val}.txt  "<ảnh dòng>\t<chữ>"
#   synth_cv/dict.txt             bảng ký tự (NFC)

# Phiên bản cho VLM (PaddleOCR-VL): ảnh trang/vùng + nhãn

python3 ocr_synth/generate.py --n 3000 --out synth_data        # khoảng 0.3 giây/trang trên 2 CPU
python3 ocr_synth/convert.py synth_data --fmt erniekit --image-root /kaggle/input/<dataset>
```

## Đầu ra
- `images/pages/*.jpg`: cả trang, cạnh dài ≤ 1280 px
- `images/blocks/*.jpg`: từng vùng chữ (tối đa 4 vùng/trang), giống crop mà layout model đưa vào VLM
- `train.jsonl` / `val.jsonl`: `{"image","text","level","template","aug","doc"}`. Chia theo trang (5% val).

Quy ước nhãn: các dòng xuống hàng do tự ngắt trong cùng đoạn được nối bằng dấu cách, mỗi đoạn hay khối là một dòng `\n`.
Thứ tự đọc: quốc hiệu cột trái → cột phải → thân văn bản → khối ký. Chữ trên con dấu và chữ ký **không** đưa vào nhãn.

## Hạn chế
- Chỉ có 3 bố cục và 1 font (Times-like), nên model có thể học thuộc bố cục. Vì vậy **phải** đánh giá trên ảnh scan thật.
- Chưa có bảng, chữ viết tay hay CCCD. Muốn có thì thêm template trong `templates.py`.
- Schema ở `convert.py` cần đối chiếu với tài liệu ERNIEKit/PaddleFormers đúng phiên bản bạn dùng.
