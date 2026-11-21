"""Các mẫu văn bản hành chính, điền hoàn toàn bằng dữ liệu giả."""
import random
from datetime import date
from fake_data import (person, rand_date, fmt, unit, address, cap, CHUC_DANH, DAN_TOC, NGHE, DOI_TUONG,
                       HO, DEM_NAM, TEN_NAM)
from render import Page, pt, stamp, signature, paste

LEADERS = ["TM. ỦY BAN NHÂN DÂN", "TUQ. CHỦ TỊCH", "KT. CHỦ TỊCH"]


def leader_name():
    return f"{random.choice(HO)} {random.choice(DEM_NAM)} {random.choice(TEN_NAM)}"


def quoc_hieu(p, left_lines):
    p.two_col(left_lines,
              [("CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM" if random.random() < .5 else "CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM", "b", False),
               ("Độc lập - Tự do - Hạnh phúc", "b", True)])


def sign_block(p, title_lines, name, kind_unit, uname, x0=None):
    x0 = x0 or p.margin_l + (p.margin_r - p.margin_l) * 0.45
    y = p.y
    for t, s in title_lines:
        y = p.para(t, s, "center", x0, p.margin_r, y=y, advance=False, kind="sign")
    sy = y + pt(random.uniform(40, 60))
    cx = (x0 + p.margin_r) / 2
    y_name = y + pt(70)
    if random.random() < 0.9:
        paste(p, stamp(f"ỦY BAN NHÂN DÂN {kind_unit.upper()} {uname.upper()} * TP HÀ NỘI *"), cx - pt(random.uniform(30, 60)), sy)
    if random.random() < 0.9:
        paste(p, signature(), cx + pt(random.uniform(-10, 25)), sy + pt(10))
    p.para(name, "b", "center", x0, p.margin_r, y=y_name, advance=False, kind="sign")
    p.y = y_name + pt(30)


def tthn():
    p = Page(size_pt=random.choice([12.5, 13, 13.5]))
    k, u = unit()
    U = u.upper()
    left = [("THÀNH PHỐ HÀ NỘI", "r", False), (f"UBND {k.upper()} {U}", "b", True)]
    quoc_hieu(p, left)
    issue = rand_date(2024, 2026)
    num = f"{random.randint(1, 600)}/{issue.year}/UBND-XNTTHN"
    mid = p.margin_l + (p.margin_r - p.margin_l) * 0.42
    y = p.y
    p.para(f"Số: {num}", "r", "center", p.margin_l - pt(20), mid, y=y, advance=False, kind="header")
    p.para(f"{u}, ngày {issue.day:02d} tháng {issue.month} năm {issue.year}", "i", "center", mid, p.margin_r, y=y, kind="header")
    p.space(1.2)
    p.para("GIẤY XÁC NHẬN TÌNH TRẠNG HÔN NHÂN", "b", "center", size=pt(15), kind="title", gap=0.05)
    p.para(random.choice([f"ỦY BAN NHÂN DÂN {k.upper()} {U}", f"UBND {k} {u}"]), "b", "center", kind="title")
    p.space(0.4)
    a = person()
    staff = person()
    p.para(f"Xét đề nghị của ông/bà: {staff['name']} {random.choice(CHUC_DANH)} về việc cấp Giấy xác nhận tình trạng hôn nhân cho {a['name'].upper()}", indent=pt(28))
    p.para("XÁC NHẬN", "b", "center", kind="title")
    p.para(f"Họ, chữ đệm, tên: {a['name'].upper()}")
    p.para(f"Ngày, tháng, năm sinh: {fmt(a['dob'])}")
    p.para(f"Giới tính: {a['gender']}     Dân tộc: {random.choice(DAN_TOC)}     Quốc tịch: Việt Nam")
    cdate = rand_date(2021, 2025)
    p.para(f"Giấy tờ tùy thân: Thẻ căn cước{random.choice(['', ' công dân'])} số {a['cccd']}, "
           f"{random.choice(['Cục Cảnh sát quản lý hành chính về trật tự xã hội', 'Bộ Công an', 'Cục CS QLHC về trật tự xã hội'])} cấp ngày {fmt(cdate)}")
    p.para(f"Nơi cư trú: {address(k, u)}")
    sp = random.random()
    if sp < 0.45:
        st = "Hiện tại chưa đăng ký kết hôn với ai"
    elif sp < 0.75:
        d = rand_date(2005, 2023)
        tc = random.choice(["Tòa án nhân dân huyện Sóc Sơn", "Tòa án nhân dân quận Đống Đa", "Tòa án nhân dân khu vực 3 - Hà Nội",
                            "Tòa án nhân dân huyện Thanh Oai", "Tòa án nhân dân quận Hà Đông"])
        st = (f"Đã đăng ký kết hôn nhưng đã ly hôn theo {random.choice(['Bản án/Quyết định ly hôn', 'Quyết định công nhận thuận tình ly hôn'])} "
              f"số {random.randint(1, 400)}/{d.year}/QĐST-HNGĐ ngày {fmt(d)} của {tc}; hiện tại chưa đăng ký kết hôn với ai")
    elif sp < 0.88:
        d0, d1 = rand_date(1990, 2010), rand_date(2011, 2025)
        st = f"Trong thời gian từ ngày {fmt(d0)} đến ngày {fmt(d1)} chưa đăng ký kết hôn với ai"
    else:
        d = rand_date(2000, 2024)
        st = f"Đã đăng ký kết hôn hoặc đã có vợ/chồng, nhưng vợ/chồng đã chết theo Trích lục khai tử số {random.randint(1, 900)}/TLKT-BS ngày {fmt(d)}; hiện tại chưa đăng ký kết hôn với ai"
    p.para(f"Tình trạng hôn nhân: {st}{random.choice(['', '.'])}")
    p.para("Giấy này được sử dụng để: " + random.choice([
        "Bổ sung hồ sơ thực hiện các thủ tục hành chính liên quan đến quyền sử dụng đất",
        "Vay vốn ngân hàng", "Mua nhà ở xã hội", "Làm thủ tục mua bán, chuyển nhượng quyền sử dụng đất",
        "Bổ sung hồ sơ mua nhà ở xã hội", "Thực hiện thủ tục thừa kế"]))
    p.para(f"Giấy xác nhận tình trạng hôn nhân có giá trị đến thời điểm thay đổi tình trạng hôn nhân hoặc 06 tháng kể từ ngày cấp, {random.choice(['tùy', 'tuỳ'])} theo thời điểm nào đến trước.")
    p.space(0.6)
    sign_block(p, [("NGƯỜI KÝ GIẤY XÁC NHẬN", "b"), ("(Ký, ghi rõ họ tên, chức vụ và đóng dấu)", "i"),
                   (random.choice(LEADERS), "b"), (random.choice(["CHỦ TỊCH", "PHÓ CHỦ TỊCH", "CHÁNH VĂN PHÒNG HĐND VÀ UBND"]), "b")],
               leader_name(), k, u)
    return p


def mau02():
    p = Page(size_pt=random.choice([12, 12.5, 13]))
    p.para("Mẫu số 02. Giấy tờ chứng minh điều kiện về nhà ở để được mua, thuê mua nhà ở xã hội/nhà ở cho lực lượng vũ trang nhân dân "
           "(trường hợp chưa có nhà ở thuộc sở hữu của mình)", "b", size=pt(12), kind="text")
    p.space(0.8)
    p.para(random.choice(["CỘNG HÒA XÃ HỘI CHỦ NGHĨA VIỆT NAM", "CỘNG HOÀ XÃ HỘI CHỦ NGHĨA VIỆT NAM"]), "b", "center", gap=0.05, kind="header")
    p.para("Độc lập - Tự do - Hạnh phúc", "b", "center", underline=True, kind="header")
    p.space(0.8)
    p.para("GIẤY XÁC NHẬN VỀ ĐIỀU KIỆN NHÀ Ở", "b", "center", size=pt(14.5), kind="title")
    p.space(0.4)
    k, u = unit()
    a = person()
    p.para(f"1. Kính gửi¹: Văn phòng/Chi nhánh văn phòng đăng ký đất đai {random.choice(['quận/huyện', 'khu vực'])} {u}, thành phố Hà Nội "
           "(nơi có dự án đầu tư xây dựng nhà ở xã hội/nhà ở cho lực lượng vũ trang nhân dân).")
    p.para(f"2. Họ và tên: {a['name'].upper()}")
    p.para(f"3. Căn cước công dân số: {a['cccd']}  cấp ngày {fmt(rand_date(2021, 2025))}; tại Cục Cảnh sát Quản lý hành chính về trật tự xã hội")
    addr = address(k, u)
    p.para(f"4. Nơi ở hiện tại²: {addr}")
    p.para(f"5. Đăng ký thường trú (đăng ký tạm trú)³: {addr if random.random() < .6 else address()}")
    if random.random() < 0.6:
        sp = person("Nữ" if a["gender"] == "Nam" else "Nam")
        p.para(f"6. Họ và tên vợ/chồng (nếu có): {sp['name']}")
        p.para(f"Căn cước công dân số: {sp['cccd']}  cấp ngày {fmt(rand_date(2021, 2025))}")
        p.para("tại Cục Cảnh sát Quản lý hành chính về trật tự xã hội")
        p.para(f"7. Số sổ hộ khẩu/Số định danh hộ gia đình (nếu có): {random.randint(10, 9999)}")
    else:
        p.para("6. Họ và tên vợ/chồng (nếu có): Không")
    p.para(f"8. Là đối tượng⁴: {random.choice(DOI_TUONG)}")
    p.para(f"9. Nghề nghiệp: {random.choice(NGHE)}")
    p.para("Văn phòng/Chi nhánh văn phòng đăng ký đất đai xác nhận ông/bà có tên nêu trên chưa có tên trong Giấy chứng nhận "
           "quyền sử dụng đất, quyền sở hữu nhà ở và tài sản khác gắn liền với đất tại tỉnh, thành phố nơi có dự án đầu tư xây dựng nhà ở xã hội.")
    p.space(0.6)
    issue = rand_date(2025, 2026)
    p.para(f"{u}, ngày {issue.day:02d} tháng {issue.month:02d} năm {issue.year}", "i", "center",
           p.margin_l + (p.margin_r - p.margin_l) * 0.45, p.margin_r, kind="sign")
    sign_block(p, [("VĂN PHÒNG ĐĂNG KÝ ĐẤT ĐAI", "b"), ("(Ký, ghi rõ họ tên và đóng dấu)", "i")], leader_name(), k, u)
    return p


def phieu_dat_dai():
    p = Page(size_pt=random.choice([13, 13.5, 14]))
    k, u = unit()
    quoc_hieu(p, [("ỦY BAN NHÂN DÂN", "b", False), (f"{k.upper()} {u.upper()}", "b", True)])
    issue = rand_date(2025, 2026)
    mid = p.margin_l + (p.margin_r - p.margin_l) * 0.42
    y = p.y
    p.para(f"Số: {random.choice(['    ', str(random.randint(1, 300))])}/PCC-UBND", "r", "center", p.margin_l - pt(20), mid, y=y, advance=False, kind="header")
    p.para(f"{u}, ngày {issue.day:02d} tháng {issue.month:02d} năm {issue.year}", "i", "center", mid, p.margin_r, y=y, kind="header")
    p.space(1)
    p.para("PHIẾU CUNG CẤP THÔNG TIN, DỮ LIỆU ĐẤT ĐAI", "b", "center", kind="title")
    a, head = person(), person("Nam")
    xung = "ông" if a["gender"] == "Nam" else "bà"
    addr = address(k, u)
    p.para(f"Kính gửi: {xung} {a['name']}, địa chỉ: {addr}", "r", "center")
    gcn = f"{random.choice(['CH', 'CS', 'BX', 'AP'])} {random.randint(100000, 999999)}"
    svs = f"CH{random.randint(1000, 99999):05d}"
    gd = rand_date(2000, 2020)
    rd = issue.toordinal() - random.randint(1, 5)
    rd = date.fromordinal(rd)
    p.para(f"Ngày {fmt(rd)}, UBND {k} {u} nhận được hồ sơ mã số H26.{random.randint(100, 999)}-{rd.strftime('%y%m%d')}-{random.randint(1, 99):04d} "
           f"của {xung} {a['name']}, địa chỉ: {addr}. Nội dung theo phiếu yêu cầu cung cấp thông tin, dữ liệu đất đai về xác nhận nhân khẩu "
           f"trên giấy chứng nhận quyền sử dụng đất số {gcn}; số vào sổ {svs}, cấp ngày {fmt(gd)}. Sau khi kiểm tra hồ sơ, UBND {k} {u} có ý kiến như sau:",
           indent=pt(36), gap=0.1)
    n = random.randint(2, 7)
    p.para(f"Hộ ông {head['name']}, địa chỉ: {addr} đã được cấp “Giấy chứng nhận quyền sử dụng đất quyền sở hữu nhà ở và tài sản khác gắn liền với đất” "
           f"có số phát hành: {gcn}; số vào sổ {svs}, cấp ngày {fmt(gd)}. Hộ ông {head['name']} gồm {n:02d} nhân khẩu:", indent=pt(36), gap=0.1)
    ho = head["name"].split()[0]
    for i in range(1, n + 1):
        m = head if i == 1 else person()
        nm = m["name"] if i == 1 or random.random() < .4 else f"{ho} {' '.join(m['name'].split()[1:])}"
        tail = f"sinh năm {m['dob'].year}" if random.random() < .85 else "đã chết"
        p.para(f"{i}. {'Ông' if m['gender'] == 'Nam' else 'Bà'} {nm}, {tail}", x0=p.margin_l + pt(36), gap=0.05)
    p.para(f"Vậy, UBND {k} {u} cung cấp thông tin, dữ liệu đất đai để {xung} {a['name']}, địa chỉ: {addr} được biết./.", indent=pt(36))
    p.space(0.4)
    y = p.y
    p.para("Nơi nhận:", "bi", x1=p.margin_l + pt(150), y=y, advance=False, kind="sign")
    p.para("- Như trên;", "r", size=pt(11), x1=p.margin_l + pt(150), y=y + pt(18), advance=False, kind="sign")
    p.para("- Lưu VT.", "r", size=pt(11), x1=p.margin_l + pt(150), y=y + pt(32), advance=False, kind="sign")
    p.y = y
    sign_block(p, [("TM. ỦY BAN NHÂN DÂN", "b"), (random.choice(["KT. CHỦ TỊCH", "CHỦ TỊCH"]), "b"), ("PHÓ CHỦ TỊCH", "b")], leader_name(), k, u)
    return p


TEMPLATES = {"tthn": (tthn, 0.5), "mau02": (mau02, 0.3), "phieu_dat_dai": (phieu_dat_dai, 0.2)}
