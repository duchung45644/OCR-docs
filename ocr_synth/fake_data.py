"""Sinh dữ liệu giả (họ tên, địa chỉ, giấy tờ) cho mẫu hành chính Hà Nội. Không dùng dữ liệu thật."""
import random
from datetime import date, timedelta

HO = ["Nguyễn", "Trần", "Lê", "Phạm", "Hoàng", "Huỳnh", "Phan", "Vũ", "Võ", "Đặng", "Bùi", "Đỗ",
      "Hồ", "Ngô", "Dương", "Lý", "Đinh", "Trịnh", "Đoàn", "Lương", "Mai", "Tạ", "Chu", "Kiều", "Khuất", "Quách"]
DEM_NAM = ["Văn", "Đức", "Minh", "Quang", "Hữu", "Thành", "Tuấn", "Xuân", "Công", "Mạnh", "Trọng", "Ngọc", "Hoàng", "Thế", "Duy"]
DEM_NU = ["Thị", "Ngọc", "Thu", "Thanh", "Minh", "Phương", "Kim", "Hồng", "Thùy", "Lan", "Bích", "Diệu", "Mỹ", "Hải"]
TEN_NAM = ["An", "Bình", "Cường", "Dũng", "Đạt", "Hải", "Hiếu", "Hùng", "Huy", "Khánh", "Long", "Nam", "Phong",
           "Quân", "Sơn", "Thắng", "Tiến", "Trung", "Tùng", "Vinh", "Việt", "Hoàng", "Đông", "Lực", "Thịnh"]
TEN_NU = ["Anh", "Chi", "Dung", "Giang", "Hà", "Hạnh", "Hằng", "Hiền", "Hoa", "Hương", "Huyền", "Lan", "Linh",
          "Loan", "Mai", "Ngân", "Nhung", "Oanh", "Phương", "Quyên", "Thảo", "Trang", "Tuyết", "Yến", "Nga", "Thủy"]
XA = ["Nội Bài", "Đan Phượng", "Quảng Bị", "Phượng Dực", "Ứng Hòa", "Dân Hòa", "Sóc Sơn", "Mê Linh", "Thanh Oai",
      "Phúc Thọ", "Ba Vì", "Thạch Thất", "Quốc Oai", "Chương Mỹ", "Thường Tín", "Phú Xuyên", "Gia Lâm", "Đông Anh",
      "Bát Tràng", "Thuận An", "Hòa Lạc", "Yên Xuân", "Kim Anh", "Đa Phúc", "Tiến Thắng", "Quang Minh"]
PHUONG = ["Hồng Hà", "Hoàn Kiếm", "Ba Đình", "Thanh Xuân", "Khương Đình", "Cầu Giấy", "Đống Đa", "Hai Bà Trưng",
          "Hoàng Mai", "Long Biên", "Tây Hồ", "Hà Đông", "Yên Nghĩa", "Định Công", "Láng", "Ô Chợ Dừa", "Kim Liên",
          "Văn Miếu - Quốc Tử Giám", "Bạch Mai", "Vĩnh Tuy", "Lĩnh Nam", "Phú Diễn", "Xuân Đỉnh", "Nghĩa Đô"]
DUONG = ["Nguyễn Trãi", "Lê Lợi", "Trần Phú", "Quang Trung", "Láng Hạ", "Giải Phóng", "Kim Mã", "Hoàng Quốc Việt",
         "Phạm Văn Đồng", "Nguyễn Văn Cừ", "Minh Khai", "Tam Trinh", "Khương Trung", "Trường Chinh", "Lạc Long Quân"]
THON = ["Thôn Đoài", "Thôn Đông", "Thôn Thượng", "Thôn Hạ", "Thôn Trung", "Xóm Mới", "Thôn Bắc", "Thôn Nam", "Cụm 3", "Tổ 5"]
DAN_TOC = ["Kinh"] * 18 + ["Tày", "Mường", "Thái", "Dao"]
CHUC_DANH = ["chuyên viên Văn phòng HĐND và UBND", "công chức Tư pháp - Hộ tịch", "công chức Văn phòng - Thống kê",
             "chuyên viên Phòng Văn hóa - Xã hội"]
NGHE = ["Công nhân", "Viên chức", "Lao động tự do", "Nhân viên văn phòng", "Kinh doanh", "Giáo viên", "Kỹ sư"]
DOI_TUONG = ["Người thu nhập thấp tại khu vực đô thị", "Công nhân, người lao động đang làm việc tại doanh nghiệp",
             "Cán bộ, công chức, viên chức", "Hộ gia đình nghèo, cận nghèo tại khu vực đô thị",
             "Người lao động tự do tại khu vực đô thị"]


def person(gender=None):
    g = gender or random.choice(["Nam", "Nữ"])
    if g == "Nam":
        name = f"{random.choice(HO)} {random.choice(DEM_NAM)} {random.choice(TEN_NAM)}"
    else:
        dem = random.choice(DEM_NU)
        if random.random() < 0.3:
            dem += " " + random.choice(DEM_NU)
        name = f"{random.choice(HO)} {dem} {random.choice(TEN_NU)}"
    dob = rand_date(1960, 2004)
    return {"name": name, "gender": g, "dob": dob, "cccd": cccd(g, dob.year)}


def cccd(gender, year):
    # 001 = mã Hà Nội; chữ số giới tính/thế kỷ theo quy ước; phần còn lại ngẫu nhiên
    c = (0 if year < 2000 else 2) + (0 if gender == "Nam" else 1)
    return f"001{c}{year % 100:02d}{random.randint(0, 999999):06d}"


def rand_date(y0, y1):
    d0 = date(y0, 1, 1)
    return d0 + timedelta(days=random.randint(0, (date(y1, 12, 31) - d0).days))


def fmt(d, sep="/"):
    return f"{d.day:02d}{sep}{d.month:02d}{sep}{d.year}"


def unit():
    if random.random() < 0.55:
        return "xã", random.choice(XA)
    return "phường", random.choice(PHUONG)


def address(kind=None, name=None):
    kind, name = (kind, name) if kind else unit()
    if kind == "xã":
        pre = random.choice(THON)
    else:
        pre = f"Số {random.randint(1, 199)}{random.choice(['', '/' + str(random.randint(2, 60))])} {random.choice(['đường', 'phố', 'ngõ ' + str(random.randint(2, 300))])} {random.choice(DUONG)}"
    return f"{pre}, {kind} {name}, thành phố Hà Nội"


def cap(s):
    return s[:1].upper() + s[1:]
