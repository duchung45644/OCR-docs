"""Dựng trang A4 từ danh sách block, vẽ con dấu/chữ ký giả, và tạo nhiễu kiểu scan/ảnh chụp. Chỉ dùng PIL."""
import math
import random
import re
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageChops, ImageOps
import io

FONT_DIR = "/usr/share/fonts/truetype/liberation/"
FONTS = {"r": "LiberationSerif-Regular.ttf", "b": "LiberationSerif-Bold.ttf",
         "i": "LiberationSerif-Italic.ttf", "bi": "LiberationSerif-BoldItalic.ttf"}
_cache = {}

DPI = 150
PAGE_W, PAGE_H = int(8.27 * DPI), int(11.69 * DPI)


def font(style, size):
    k = (style, size)
    if k not in _cache:
        _cache[k] = ImageFont.truetype(FONT_DIR + FONTS[style], size)
    return _cache[k]


def pt(p):
    return round(p * DPI / 72)


def wrap(text, f, width):
    words, lines, cur = text.split(" "), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if f.getlength(t) <= width or not cur:
            cur = t
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


class Page:
    """Block = các đoạn văn trong một khung (x0, x1). Ghi lại bbox + text để làm nhãn."""

    def __init__(self, size_pt=13):
        self.img = Image.new("RGB", (PAGE_W, PAGE_H), "white")
        self.d = ImageDraw.Draw(self.img)
        self.margin_l = pt(random.uniform(70, 85))
        self.margin_r = PAGE_W - pt(random.uniform(45, 60))
        self.y = pt(random.uniform(40, 60))
        self.size = pt(size_pt)
        self.lead = random.uniform(1.25, 1.45)
        self.blocks = []  # (bbox, text, kind)
        self.lines = []   # (bbox chặt của từng dòng đã vẽ, text dòng, kind)

    def para(self, text, style="r", align="left", x0=None, x1=None, size=None, indent=0,
             underline=False, kind="text", y=None, advance=True, gap=0.25):
        f = font(style, size or self.size)
        x0 = self.margin_l if x0 is None else x0
        x1 = self.margin_r if x1 is None else x1
        y0 = cur = self.y if y is None else y
        lh = int((size or self.size) * self.lead)
        lines = wrap(text, f, x1 - x0 - indent)
        bx0, bx1 = 10 ** 9, 0
        for k, ln in enumerate(lines):
            w = f.getlength(ln)
            if align == "center":
                lx = x0 + (x1 - x0 - w) / 2
            elif align == "right":
                lx = x1 - w
            else:
                lx = x0 + (indent if k == 0 else 0)
            self.d.text((lx, cur), ln, font=f, fill=(15, 15, 15))
            if ln.strip():
                self.lines.append((self.d.textbbox((lx, cur), ln, font=f), ln, kind))
            if underline:
                uy = cur + (size or self.size) * 1.12
                self.d.line([(lx + w * 0.15, uy), (lx + w * 0.85, uy)], fill=(15, 15, 15), width=2)
            bx0, bx1 = min(bx0, lx), max(bx1, lx + w)
            cur += lh
        bbox = (int(bx0) - 4, int(y0) - 4, int(bx1) + 4, int(cur - lh * 0.2) + 4)
        self.blocks.append((bbox, text, kind))
        if advance:
            self.y = cur + int(lh * gap)
        return cur

    def space(self, n=0.5):
        self.y += int(self.size * n)

    def two_col(self, left, right, split=0.42):
        """Quốc hiệu 2 cột. left/right: list (text, style, underline). Nhãn: cột trái rồi cột phải."""
        mid = self.margin_l + (self.margin_r - self.margin_l) * split
        y0 = self.y
        yl = yr = y0
        for t, s, u in left:
            yl = self.para(t, s, "center", self.margin_l - pt(20), mid, underline=u, y=yl, advance=False, kind="header")
        for t, s, u in right:
            yr = self.para(t, s, "center", mid, self.margin_r + pt(10), underline=u, y=yr, advance=False, kind="header")
        self.y = max(yl, yr) + int(self.size * 0.3)
        return mid


def norm(t):
    return re.sub(r" {2,}", " ", t).strip()


def text_of(page):
    return "\n".join(norm(t) for _, t, _ in page.blocks)


# ---------- con dấu / chữ ký giả ----------

def stamp(text_ring, text_mid="", r=None):
    r = r or pt(random.uniform(55, 70))
    S = 2 * r + 20
    im = Image.new("RGBA", (S, S), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = (random.randint(190, 230), random.randint(20, 60), random.randint(30, 70), 255)
    c = S // 2
    d.ellipse([c - r, c - r, c + r, c + r], outline=col, width=5)
    d.ellipse([c - r + 10, c - r + 10, c + r - 10, c + r - 10], outline=col, width=2)
    ri = r * 0.45
    d.ellipse([c - ri, c - ri, c + ri, c + ri], outline=col, width=2)
    # ngôi sao
    pts = []
    for k in range(10):
        a = -math.pi / 2 + k * math.pi / 5
        rr = ri * (0.6 if k % 2 == 0 else 0.25)
        pts.append((c + rr * math.cos(a), c + rr * math.sin(a)))
    d.polygon(pts, fill=col)
    f = font("b", int(r * 0.17))
    n = len(text_ring)
    for k, ch in enumerate(text_ring):
        a = -math.pi * 0.95 + (k + 0.5) * (1.9 * math.pi) / n
        cim = Image.new("RGBA", (40, 40), (0, 0, 0, 0))
        ImageDraw.Draw(cim).text((20, 20), ch, font=f, fill=col, anchor="mm")
        cim = cim.rotate(-math.degrees(a) - 90, resample=Image.BICUBIC)
        rr = r * 0.74
        im.alpha_composite(cim, (int(c + rr * math.cos(a) - 20), int(c + rr * math.sin(a) - 20)))
    im = im.rotate(random.uniform(-25, 25), resample=Image.BICUBIC)
    # mực không đều
    a = im.split()[3].point(lambda v: int(v * random.uniform(0.55, 0.95)))
    a = ImageChops.multiply(a, Image.effect_noise(im.size, 60).convert("L").point(lambda v: min(255, v + 120)))
    im.putalpha(a)
    return im


def signature(w=None, h=None):
    w, h = w or pt(random.uniform(90, 140)), h or pt(random.uniform(35, 55))
    im = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    col = random.choice([(20, 40, 150, 230), (10, 10, 60, 230), (30, 30, 30, 220)])
    for _ in range(random.randint(1, 3)):
        pts, x, y = [], random.uniform(0, w * 0.2), random.uniform(h * 0.3, h * 0.7)
        for _ in range(random.randint(25, 50)):
            x = min(w - 2, x + random.uniform(0, w / 18))
            y = min(h - 2, max(2, y + random.uniform(-h / 3, h / 3)))
            pts.append((x, y))
        d.line(pts, fill=col, width=random.randint(2, 3), joint="curve")
    return im


def paste(page, im, cx, cy):
    page.img.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)


# ---------- nhiễu kiểu scan / chụp ----------

def augment(img, strength=None):
    """strength: 'clean' | 'scan' | 'photo'. Trả về ảnh RGB."""
    mode = strength or random.choices(["clean", "scan", "photo"], [0.15, 0.55, 0.30])[0]
    img = img.convert("RGB")
    if mode == "clean":
        return jpeg(img, random.randint(80, 95))
    W, H = img.size
    # giấy ngả màu
    tint = Image.new("RGB", img.size, tuple(random.randint(225, 255) for _ in range(3)))
    img = ImageChops.multiply(img, tint)
    if mode == "scan":
        img = img.rotate(random.uniform(-2.5, 2.5), resample=Image.BICUBIC, expand=False, fillcolor=(250, 250, 250))
        if random.random() < 0.3:
            img = ImageOps.grayscale(img).convert("RGB")
        if random.random() < 0.15:  # scan đen trắng
            img = ImageOps.grayscale(img).point(lambda v: 255 if v > random.randint(140, 190) else 0).convert("RGB")
    else:
        # phối cảnh nhẹ + nền tối + bóng
        bg = Image.new("RGB", (int(W * 1.1), int(H * 1.1)), tuple(random.randint(40, 120) for _ in range(3)))
        bg.paste(img, (int(W * 0.05), int(H * 0.05)))
        img = bg
        W2, H2 = img.size
        j = lambda: random.uniform(-0.04, 0.04)
        quad = [W2 * (0.04 + j()), H2 * (0.04 + j()), W2 * (0.04 + j()), H2 * (0.96 + j()),
                W2 * (0.96 + j()), H2 * (0.96 + j()), W2 * (0.96 + j()), H2 * (0.04 + j())]
        img = img.transform((W, H), Image.QUAD, quad, resample=Image.BICUBIC)
        # ánh sáng không đều: nội suy mượt từ lưới 3x3 độ sáng ngẫu nhiên
        lo = random.randint(150, 215)
        grid = Image.new("L", (3, 3))
        grid.putdata([random.randint(lo, 255) for _ in range(9)])
        grad = grid.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
        img = ImageChops.multiply(img, Image.merge("RGB", [grad] * 3))
    if random.random() < 0.6:
        img = img.filter(ImageFilter.GaussianBlur(random.uniform(0.3, 1.3)))
    if random.random() < 0.5:
        n = Image.effect_noise(img.size, random.uniform(8, 25)).convert("RGB")
        img = Image.blend(img, ImageChops.multiply(img, n.point(lambda v: min(255, v + 128))), 0.25)
    if random.random() < 0.4:
        s = random.uniform(0.55, 0.85)
        img = img.resize((int(W * s), int(H * s)), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    return jpeg(img, random.randint(35, 85))


def jpeg(img, q):
    b = io.BytesIO()
    img.save(b, "JPEG", quality=q)
    b.seek(0)
    return Image.open(b).convert("RGB")


# ---------- nhiễu có theo dõi toạ độ (cho det) ----------

def _solve(A, b):
    """Giải Ax=b (Gauss, pivot từng phần), Python thuần."""
    n = len(b)
    M = [row[:] + [b[i]] for i, row in enumerate(A)]
    for c in range(n):
        p = max(range(c, n), key=lambda r: abs(M[r][c]))
        M[c], M[p] = M[p], M[c]
        for r in range(n):
            if r != c:
                k = M[r][c] / M[c][c]
                M[r] = [a - k * bb for a, bb in zip(M[r], M[c])]
    return [M[i][n] / M[i][i] for i in range(n)]


def homography(src, dst):
    """8 hệ số H sao cho dst = H(src); src, dst: 4 điểm (x, y)."""
    A, b = [], []
    for (x, y), (u, v) in zip(src, dst):
        A.append([x, y, 1, 0, 0, 0, -u * x, -u * y]); b.append(u)
        A.append([0, 0, 0, x, y, 1, -v * x, -v * y]); b.append(v)
    return _solve(A, b)


def apply_h(h, x, y):
    w = h[6] * x + h[7] * y + 1
    return (h[0] * x + h[1] * y + h[2]) / w, (h[3] * x + h[4] * y + h[5]) / w


def photometric(img, mode):
    W, H = img.size
    if mode == "clean":
        return jpeg(img, random.randint(80, 95))
    if random.random() < 0.6:
        img = img.filter(ImageFilter.GaussianBlur(random.uniform(0.3, 1.2)))
    if random.random() < 0.5:
        n = Image.effect_noise(img.size, random.uniform(8, 25)).convert("RGB")
        img = Image.blend(img, ImageChops.multiply(img, n.point(lambda v: min(255, v + 128))), 0.25)
    if random.random() < 0.4:
        s = random.uniform(0.55, 0.85)
        img = img.resize((max(1, int(W * s)), max(1, int(H * s))), Image.BILINEAR).resize((W, H), Image.BILINEAR)
    return jpeg(img, random.randint(35, 85))


def augment_tracked(img, mode):
    """Như augment() nhưng trả thêm hàm f(x, y) -> (x', y') ánh xạ toạ độ trang gốc sang ảnh đầu ra."""
    img = img.convert("RGB")
    W, H = img.size
    if mode == "clean":
        return photometric(img, mode), (lambda x, y: (x, y))
    img = ImageChops.multiply(img, Image.new("RGB", img.size, tuple(random.randint(225, 255) for _ in range(3))))
    if mode == "scan":
        ang = random.uniform(-2.5, 2.5)
        img = img.rotate(ang, resample=Image.BICUBIC, fillcolor=(250, 250, 250))
        a, cx, cy = math.radians(ang), W / 2, H / 2
        ca, sa = math.cos(a), math.sin(a)
        f = lambda x, y: (cx + (x - cx) * ca + (y - cy) * sa, cy - (x - cx) * sa + (y - cy) * ca)
        if random.random() < 0.3:
            img = ImageOps.grayscale(img).convert("RGB")
        if random.random() < 0.12:
            th = random.randint(140, 190)
            img = ImageOps.grayscale(img).point(lambda v: 255 if v > th else 0).convert("RGB")
    else:  # photo: nền tối + phối cảnh + ánh sáng không đều
        ox, oy = int(W * 0.05), int(H * 0.05)
        bg = Image.new("RGB", (W + 2 * ox, H + 2 * oy), tuple(random.randint(40, 120) for _ in range(3)))
        bg.paste(img, (ox, oy))
        W2, H2 = bg.size
        j = lambda: random.uniform(-0.04, 0.04)
        out = [(0, 0), (0, H), (W, H), (W, 0)]
        quad = [(W2 * (0.04 + j()), H2 * (0.04 + j())), (W2 * (0.04 + j()), H2 * (0.96 + j())),
                (W2 * (0.96 + j()), H2 * (0.96 + j())), (W2 * (0.96 + j()), H2 * (0.04 + j()))]
        img = bg.transform((W, H), Image.PERSPECTIVE, homography(out, quad), resample=Image.BICUBIC)
        hf = homography(quad, out)
        f = lambda x, y: apply_h(hf, x + ox, y + oy)
        lo = random.randint(150, 215)
        grid = Image.new("L", (3, 3))
        grid.putdata([random.randint(lo, 255) for _ in range(9)])
        g = grid.resize((W, H), Image.BICUBIC).filter(ImageFilter.GaussianBlur(40))
        img = ImageChops.multiply(img, Image.merge("RGB", [g] * 3))
    return photometric(img, mode), f


def augment_line(crop):
    """Nhiễu cho ảnh dòng (rec): xoay rất nhẹ có expand, giấy ngả màu, xám/đen trắng, mờ, nhiễu, JPEG."""
    crop = crop.convert("RGB")
    mode = random.choices(["clean", "scan"], [0.25, 0.75])[0]
    if mode == "scan":
        crop = ImageChops.multiply(crop, Image.new("RGB", crop.size, tuple(random.randint(215, 255) for _ in range(3))))
        if random.random() < 0.5:
            bg = tuple(random.randint(225, 250) for _ in range(3))
            crop = crop.rotate(random.uniform(-1.2, 1.2), resample=Image.BICUBIC, expand=True, fillcolor=bg)
        if random.random() < 0.3:
            crop = ImageOps.grayscale(crop).convert("RGB")
        elif random.random() < 0.08:
            th = random.randint(140, 190)
            crop = ImageOps.grayscale(crop).point(lambda v: 255 if v > th else 0).convert("RGB")
    return photometric(crop, mode), mode
