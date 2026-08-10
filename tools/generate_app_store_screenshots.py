from pathlib import Path
from PIL import Image, ImageDraw, ImageFont, ImageFilter
import os


ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "appstore_screenshots"

INK = "#17211f"
MUTED = "#65716d"
LINE = "#dce4df"
SOFT = "#f4f7f3"
PAPER = "#ffffff"
MINT = "#1f9d7a"
MINT_DARK = "#127159"
BLUE = "#3c78d8"
SUN = "#f3b23c"
CORAL = "#e76555"
SCREEN_BG = "#fbfcf9"


def font_file(weight):
    candidates = [
        f"/System/Library/Fonts/ヒラギノ角ゴシック W{weight}.ttc",
        f"/System/Library/Fonts/ヒラギノ角ゴシック W{weight}.ttc",
        "/System/Library/Fonts/HelveticaNeue.ttc",
        "/System/Library/Fonts/Supplemental/Arial Unicode.ttf",
    ]
    return next((p for p in candidates if os.path.exists(p)), None)


FONT_REG = font_file(3)
FONT_BOLD = font_file(6) or FONT_REG
FONT_HEAVY = font_file(8) or FONT_BOLD


def font(size, bold=False, heavy=False):
    path = FONT_HEAVY if heavy else FONT_BOLD if bold else FONT_REG
    return ImageFont.truetype(path, size) if path else ImageFont.load_default()


def text_size(draw, text, fnt):
    box = draw.textbbox((0, 0), text, font=fnt)
    return box[2] - box[0], box[3] - box[1]


def rr(draw, box, radius, fill, outline=None, width=1):
    draw.rounded_rectangle(box, radius=radius, fill=fill, outline=outline, width=width)


def panel(canvas, box, radius=28, fill=PAPER, outline=LINE, shadow=True):
    if shadow:
        layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
        sd = ImageDraw.Draw(layer)
        x1, y1, x2, y2 = box
        sd.rounded_rectangle((x1, y1 + 16, x2, y2 + 16), radius=radius, fill=(23, 33, 31, 24))
        canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(18)))
    rr(ImageDraw.Draw(canvas), box, radius, fill, outline, 2)


def bg(width, height):
    im = Image.new("RGBA", (width, height), PAPER)
    pix = im.load()
    top = (251, 253, 250)
    bottom = (237, 246, 239)
    for y in range(height):
        t = y / max(1, height - 1)
        col = tuple(int(top[i] * (1 - t) + bottom[i] * t) for i in range(3))
        for x in range(width):
            pix[x, y] = col + (255,)
    d = ImageDraw.Draw(im)
    d.ellipse((-width * 0.18, height * 0.64, width * 0.27, height * 0.94), fill=(227, 245, 235, 130))
    d.ellipse((width * 0.74, height * 0.18, width * 1.15, height * 0.46), fill=(226, 244, 234, 150))
    d.ellipse((width * 0.42, height * 0.86, width * 0.72, height * 1.08), fill=(242, 249, 243, 140))
    return im


def center_text(draw, width, y, text, size, color=INK, bold=True, heavy=False):
    fnt = font(size, bold=bold, heavy=heavy)
    tw, th = text_size(draw, text, fnt)
    draw.text(((width - tw) / 2, y), text, font=fnt, fill=color)
    return y + th


def center_wrap(draw, width, y, text, size, max_width, color=MUTED, gap=12):
    fnt = font(size)
    lines = []
    current = ""
    for char in text:
        test = current + char
        if not current or text_size(draw, test, fnt)[0] <= max_width:
            current = test
        else:
            lines.append(current)
            current = char
    if current:
        lines.append(current)
    for line in lines:
        tw, th = text_size(draw, line, fnt)
        draw.text(((width - tw) / 2, y), line, font=fnt, fill=color)
        y += th + gap
    return y


def app_icon(draw, x, y, s):
    rr(draw, (x, y, x + s, y + s), int(s * 0.24), "#0e5368")
    rr(draw, (x + s * 0.12, y + s * 0.12, x + s * 0.88, y + s * 0.88), int(s * 0.14), "#2b8f8c", "#74c2ad", max(2, int(s * 0.025)))
    draw.ellipse((x + s * 0.39, y + s * 0.21, x + s * 0.61, y + s * 0.43), fill="#f7fcf8", outline="#0d4057", width=max(3, int(s * 0.045)))
    rr(draw, (x + s * 0.36, y + s * 0.42, x + s * 0.64, y + s * 0.65), int(s * 0.04), "#f7fcf8", "#0d4057", max(3, int(s * 0.045)))
    draw.line((x + s * 0.42, y + s * 0.58, x + s * 0.49, y + s * 0.51, x + s * 0.55, y + s * 0.58, x + s * 0.62, y + s * 0.49), fill="#0d4057", width=max(4, int(s * 0.05)))
    draw.ellipse((x + s * 0.50, y + s * 0.61, x + s * 0.68, y + s * 0.78), fill="#bde29c", outline="#0d4057", width=max(2, int(s * 0.032)))
    draw.ellipse((x + s * 0.32, y + s * 0.61, x + s * 0.50, y + s * 0.78), fill="#bde29c", outline="#0d4057", width=max(2, int(s * 0.032)))


def device_frame(canvas, layout):
    d = ImageDraw.Draw(canvas)
    x, y, w, h = layout["device"]
    radius = layout["device_radius"]
    layer = Image.new("RGBA", canvas.size, (0, 0, 0, 0))
    sd = ImageDraw.Draw(layer)
    sd.rounded_rectangle((x + layout["shadow_dx"], y + layout["shadow_dy"], x + w + layout["shadow_dx"], y + h + layout["shadow_dy"]), radius=radius, fill=(23, 33, 31, 48))
    canvas.alpha_composite(layer.filter(ImageFilter.GaussianBlur(layout["shadow_blur"])))
    rr(d, (x, y, x + w, y + h), radius, "#17211f")
    inset = layout["bezel"]
    rr(d, (x + inset, y + inset, x + w - inset, y + h - inset), radius - inset, SCREEN_BG)
    sx = x + layout["screen_pad_x"]
    sy = y + layout["screen_pad_y"]
    sw = w - layout["screen_pad_x"] * 2
    sh = h - layout["screen_pad_y"] - layout["screen_pad_bottom"]
    rr(d, (sx, sy, sx + sw, sy + sh), layout["screen_radius"], SCREEN_BG)
    if layout["kind"] == "phone":
        rr(d, (x + w * 0.36, y + layout["notch_y"], x + w * 0.64, y + layout["notch_y"] + layout["notch_h"]), layout["notch_h"] // 2, "#17211f")
    else:
        r = layout["camera_r"]
        d.ellipse((x + w / 2 - r, y + layout["camera_y"], x + w / 2 + r, y + layout["camera_y"] + r * 2), fill="#26332f")
    return int(sx), int(sy), int(sw), int(sh)


def app_header(draw, sx, sy, sw, title, active, scale):
    draw.text((sx + 34 * scale, sy + 22 * scale), "9:41", font=font(int(20 * scale), True), fill=INK)
    rr(draw, (sx + sw - 92 * scale, sy + 28 * scale, sx + sw - 42 * scale, sy + 48 * scale), int(6 * scale), None, INK, max(1, int(2 * scale)))
    draw.rectangle((sx + sw - 39 * scale, sy + 34 * scale, sx + sw - 35 * scale, sy + 42 * scale), fill=INK)
    draw.text((sx + 36 * scale, sy + 82 * scale), "Nutrition Photo Log", font=font(int(16 * scale), True), fill=MINT_DARK)
    draw.text((sx + 36 * scale, sy + 106 * scale), "カラダログ＋", font=font(int(32 * scale), True), fill=INK)
    x = sx + 36 * scale
    tabs = ["概要", "食事追加", "履歴", "体重", "設定"]
    for tab in tabs:
        fnt = font(int(18 * scale), True)
        tw, _ = text_size(draw, tab, fnt)
        twidth = tw + 28 * scale
        fill = PAPER if tab == active else "#eef5f0"
        outline = LINE if tab == active else "#eef5f0"
        rr(draw, (x, sy + 164 * scale, x + twidth, sy + 211 * scale), int(10 * scale), fill, outline, max(1, int(1.5 * scale)))
        draw.text((x + 14 * scale, sy + 177 * scale), tab, font=fnt, fill=INK if tab == active else MUTED)
        x += twidth + 9 * scale
        if x > sx + sw - 60 * scale:
            break
    draw.line((sx, sy + 236 * scale, sx + sw, sy + 236 * scale), fill=LINE, width=max(1, int(1.5 * scale)))
    draw.text((sx + 36 * scale, sy + 278 * scale), title, font=font(int(30 * scale), True), fill=INK)


def meal_photo(draw, box, kind=0):
    colors = [("#f6d9a5", "#72ae70", "#db6b58"), ("#f0c36d", "#6daf77", "#fff7df"), ("#c97652", "#7fbb71", "#f8ead0")]
    bgc, leaf, main = colors[kind % len(colors)]
    rr(draw, box, 18, bgc)
    x1, y1, x2, y2 = box
    draw.ellipse((x1 + 18, y1 + 18, x2 - 16, y2 - 16), fill="#fffaf1", outline="#e8d9bf", width=3)
    draw.ellipse((x1 + 48, y1 + 46, x2 - 46, y2 - 42), fill=main)
    for i in range(5):
        draw.ellipse((x1 + 34 + i * 28, y1 + 30 + (i % 2) * 10, x1 + 62 + i * 28, y1 + 58 + (i % 2) * 10), fill=leaf)


def stat_card(draw, box, label, value, note, color, scale):
    rr(draw, box, int(14 * scale), PAPER, LINE, max(1, int(1.5 * scale)))
    x1, y1, x2, y2 = box
    draw.text((x1 + 18 * scale, y1 + 17 * scale), label, font=font(int(16 * scale), True), fill=MUTED)
    draw.text((x1 + 18 * scale, y1 + 50 * scale), value, font=font(int(31 * scale), True), fill=INK)
    dot = 10 * scale
    draw.ellipse((x1 + 20 * scale, y2 - 30 * scale, x1 + 20 * scale + dot, y2 - 30 * scale + dot), fill=color)
    draw.text((x1 + 40 * scale, y2 - 35 * scale), note, font=font(int(13 * scale)), fill=MUTED)


def screen_overview(canvas, sx, sy, sw, sh, scale, tablet=False):
    d = ImageDraw.Draw(canvas)
    app_header(d, sx, sy, sw, "今日の摂取と消費", "概要", scale)
    left_w = sw - 72 * scale if not tablet else sw * 0.62
    card = (sx + 36 * scale, sy + 340 * scale, sx + 36 * scale + left_w, sy + 600 * scale)
    panel(canvas, card, int(18 * scale), shadow=False)
    d = ImageDraw.Draw(canvas)
    rr(d, (card[0] + 24 * scale, card[1] + 24 * scale, card[0] + 140 * scale, card[1] + 58 * scale), int(17 * scale), "#e8f5ef")
    d.text((card[0] + 38 * scale, card[1] + 31 * scale), "維持モード", font=font(int(15 * scale), True), fill=MINT_DARK)
    d.text((card[0] + 24 * scale, card[1] + 82 * scale), "-120 kcal", font=font(int(60 * scale), True), fill=INK)
    d.text((card[0] + 25 * scale, card[1] + 156 * scale), "目標に近いペースです", font=font(int(20 * scale)), fill=MUTED)
    rr(d, (card[0] + 26 * scale, card[1] + 216 * scale, card[2] - 26 * scale, card[1] + 238 * scale), int(11 * scale), "#dde7e0")
    rr(d, (card[0] + 26 * scale, card[1] + 216 * scale, card[0] + (card[2] - card[0]) * 0.72, card[1] + 238 * scale), int(11 * scale), MINT)
    items = [("摂取", "1,860", "目標 2,000 kcal", MINT), ("タンパク質", "104g", "目標 110g", BLUE), ("脂質", "52g", "目標 55g", SUN), ("炭水化物", "218g", "目標 250g", MINT)]
    if tablet:
        x = sx + sw * 0.68
        y = sy + 340 * scale
        for i, item in enumerate(items):
            stat_card(d, (x, y + i * 132 * scale, sx + sw - 36 * scale, y + i * 132 * scale + 110 * scale), *item, scale)
        pfc = (sx + 36 * scale, sy + 640 * scale, sx + sw * 0.62 + 36 * scale, sy + 915 * scale)
        photos = (sx + 36 * scale, sy + 950 * scale, sx + sw - 36 * scale, sy + 1210 * scale)
    else:
        start_y = sy + 632 * scale
        gap = 18 * scale
        card_w = (sw - 90 * scale) / 2
        for i, item in enumerate(items):
            bx = sx + 36 * scale + (i % 2) * (card_w + gap)
            by = start_y + (i // 2) * 132 * scale
            stat_card(d, (bx, by, bx + card_w, by + 112 * scale), *item, scale)
        pfc = (sx + 36 * scale, sy + 930 * scale, sx + sw - 36 * scale, sy + 1160 * scale)
        photos = (sx + 36 * scale, sy + 1195 * scale, sx + sw - 36 * scale, sy + 1410 * scale)
    panel(canvas, pfc, int(18 * scale), shadow=False)
    d = ImageDraw.Draw(canvas)
    d.text((pfc[0] + 24 * scale, pfc[1] + 24 * scale), "PFCバランス", font=font(int(27 * scale), True), fill=INK)
    for i, (label, pct, color) in enumerate([("タンパク質", .78, BLUE), ("脂質", .62, SUN), ("炭水化物", .72, MINT)]):
        yy = pfc[1] + (78 + i * 48) * scale
        d.text((pfc[0] + 25 * scale, yy), label, font=font(int(17 * scale), True), fill=MUTED)
        rr(d, (pfc[0] + 165 * scale, yy + 8 * scale, pfc[2] - 26 * scale, yy + 24 * scale), int(8 * scale), "#e5ebe7")
        rr(d, (pfc[0] + 165 * scale, yy + 8 * scale, pfc[0] + 165 * scale + (pfc[2] - pfc[0] - 195 * scale) * pct, yy + 24 * scale), int(8 * scale), color)
    panel(canvas, photos, int(18 * scale), shadow=False)
    d = ImageDraw.Draw(canvas)
    d.text((photos[0] + 24 * scale, photos[1] + 22 * scale), "最近の写真", font=font(int(25 * scale), True), fill=INK)
    img_y = photos[1] + 72 * scale
    img_size = min((photos[2] - photos[0] - 60 * scale) / 4, 126 * scale if not tablet else 150 * scale)
    for i in range(4):
        meal_photo(d, (photos[0] + 24 * scale + i * (img_size + 16 * scale), img_y, photos[0] + 24 * scale + i * (img_size + 16 * scale) + img_size, img_y + img_size), i)


def screen_meal(canvas, sx, sy, sw, sh, scale, tablet=False):
    d = ImageDraw.Draw(canvas)
    app_header(d, sx, sy, sw, "食事を追加", "食事追加", scale)
    if tablet:
        left = (sx + 36 * scale, sy + 340 * scale, sx + sw * 0.43, sy + 1160 * scale)
        right = (sx + sw * 0.46, sy + 340 * scale, sx + sw - 36 * scale, sy + 1160 * scale)
    else:
        left = (sx + 36 * scale, sy + 340 * scale, sx + sw - 36 * scale, sy + 760 * scale)
        right = (sx + 36 * scale, sy + 790 * scale, sx + sw - 36 * scale, sy + 1435 * scale)
    panel(canvas, left, int(18 * scale), shadow=False)
    panel(canvas, right, int(18 * scale), shadow=False)
    d = ImageDraw.Draw(canvas)
    meal_photo(d, (left[0] + 26 * scale, left[1] + 26 * scale, left[2] - 26 * scale, left[1] + (300 if not tablet else 360) * scale), 1)
    rr(d, (left[2] - 150 * scale, left[1] + (265 if not tablet else 320) * scale, left[2] - 42 * scale, left[1] + (302 if not tablet else 360) * scale), int(12 * scale), (255, 255, 255, 235))
    d.text((left[2] - 132 * scale, left[1] + (274 if not tablet else 331) * scale), "写真を変更", font=font(int(15 * scale), True), fill=INK)
    action_y = left[1] + (328 if not tablet else 394) * scale
    labels = ["カメラで撮る", "写真を選ぶ", "栄養成分表示の写真を追加"]
    for i, label in enumerate(labels):
        yy = action_y + i * 55 * scale
        rr(d, (left[0] + 26 * scale, yy, left[2] - 26 * scale, yy + 40 * scale), int(10 * scale), PAPER, LINE, max(1, int(1.5 * scale)))
        d.text((left[0] + 45 * scale, yy + 10 * scale), label, font=font(int(16 * scale), True), fill=INK)
    if tablet:
        d.text((left[0] + 28 * scale, left[1] + 600 * scale), "食材・分量の補足", font=font(int(18 * scale), True), fill=MUTED)
        rr(d, (left[0] + 26 * scale, left[1] + 632 * scale, left[2] - 26 * scale, left[1] + 745 * scale), int(12 * scale), PAPER, LINE, 2)
        d.text((left[0] + 44 * scale, left[1] + 655 * scale), "ごはん200g、鶏むね肉150g", font=font(int(18 * scale)), fill=INK)
        rr(d, (left[0] + 26 * scale, left[1] + 770 * scale, left[2] - 26 * scale, left[1] + 825 * scale), int(12 * scale), PAPER, LINE, 2)
        d.text((left[0] + 54 * scale, left[1] + 786 * scale), "AIで計算・写真解析", font=font(int(19 * scale), True), fill=INK)
    fields = [("日付", "2026-06-27"), ("区分", "昼食"), ("食事名", "鶏むね肉とご飯"), ("カロリー", "620"), ("タンパク質 g", "42"), ("脂質 g", "14"), ("炭水化物 g", "78"), ("メモ", "量を確認して保存")]
    base_y = right[1] + 30 * scale
    for i, (label, value) in enumerate(fields):
        wide = i in (2, 7)
        if tablet:
            col_w = (right[2] - right[0] - 78 * scale) / 2
            x = right[0] + 26 * scale if wide or i % 2 == 0 else right[0] + 52 * scale + col_w
            row = 0 if i < 2 else 1 if i == 2 else 2 + ((i - 3) // 2)
            y = base_y + row * 91 * scale
            w = right[2] - right[0] - 52 * scale if wide else col_w
        else:
            x = right[0] + 24 * scale if wide or i % 2 == 0 else right[0] + (right[2] - right[0]) / 2 + 8 * scale
            row = 0 if i < 2 else 1 if i == 2 else 2 + ((i - 3) // 2)
            y = base_y + row * 82 * scale
            w = right[2] - right[0] - 48 * scale if wide else (right[2] - right[0] - 66 * scale) / 2
        d.text((x, y), label, font=font(int(15 * scale), True), fill=MUTED)
        rr(d, (x, y + 25 * scale, x + w, y + 74 * scale), int(10 * scale), PAPER, LINE, max(1, int(1.5 * scale)))
        d.text((x + 14 * scale, y + 38 * scale), value, font=font(int(18 * scale)), fill=INK)
    rr(d, (right[0] + 26 * scale, right[3] - 78 * scale, right[2] - 26 * scale, right[3] - 24 * scale), int(12 * scale), MINT)
    tw, _ = text_size(d, "保存", font(int(22 * scale), True))
    d.text(((right[0] + right[2] - tw) / 2, right[3] - 64 * scale), "保存", font=font(int(22 * scale), True), fill=PAPER)


def screen_history(canvas, sx, sy, sw, sh, scale, tablet=False):
    d = ImageDraw.Draw(canvas)
    app_header(d, sx, sy, sw, "食事履歴", "履歴", scale)
    y = sy + 340 * scale
    row_h = 166 * scale if not tablet else 178 * scale
    meals = [("昼食", "鮭定食", "650 kcal", "P 35g", "F 18g", "C 76g"), ("朝食", "ヨーグルトと果物", "380 kcal", "P 22g", "F 11g", "C 58g"), ("夕食", "鶏むねサラダ", "520 kcal", "P 48g", "F 16g", "C 42g")]
    for idx, meal in enumerate(meals):
        box = (sx + 36 * scale, y, sx + sw - 36 * scale, y + row_h)
        panel(canvas, box, int(17 * scale), shadow=False)
        d = ImageDraw.Draw(canvas)
        img = row_h - 42 * scale
        meal_photo(d, (box[0] + 22 * scale, box[1] + 21 * scale, box[0] + 22 * scale + img, box[1] + 21 * scale + img), idx)
        tx = box[0] + img + 52 * scale
        d.text((tx, box[1] + 28 * scale), meal[1], font=font(int(25 * scale), True), fill=INK)
        d.text((tx, box[1] + 68 * scale), f"2026-06-27 / {meal[0]}", font=font(int(16 * scale)), fill=MUTED)
        cx = tx
        for chip in meal[2:]:
            fnt = font(int(15 * scale), True)
            tw, _ = text_size(d, chip, fnt)
            rr(d, (cx, box[1] + 108 * scale, cx + tw + 24 * scale, box[1] + 140 * scale), int(16 * scale), SOFT)
            d.text((cx + 12 * scale, box[1] + 116 * scale), chip, font=fnt, fill=INK)
            cx += tw + 35 * scale
        y += row_h + 26 * scale
    info = (sx + 36 * scale, y + 8 * scale, sx + sw - 36 * scale, y + 205 * scale)
    panel(canvas, info, int(18 * scale), fill="#eef8f2", outline="#cfe4d9", shadow=False)
    d = ImageDraw.Draw(canvas)
    d.text((info[0] + 28 * scale, info[1] + 26 * scale), "AI推定で記録をサポート", font=font(int(25 * scale), True), fill=INK)
    d.text((info[0] + 28 * scale, info[1] + 74 * scale), "保存したカロリー・PFC・写真をあとから確認できます。", font=font(int(18 * scale)), fill=MUTED)
    rr(d, (info[0] + 28 * scale, info[1] + 124 * scale, info[0] + 220 * scale, info[1] + 168 * scale), int(12 * scale), MINT)
    d.text((info[0] + 53 * scale, info[1] + 135 * scale), "記録を見返す", font=font(int(17 * scale), True), fill=PAPER)


def screen_weight(canvas, sx, sy, sw, sh, scale, tablet=False):
    d = ImageDraw.Draw(canvas)
    app_header(d, sx, sy, sw, "体重記録", "体重", scale)
    chart = (sx + 36 * scale, sy + 340 * scale, sx + sw - 36 * scale, sy + (810 if not tablet else 860) * scale)
    panel(canvas, chart, int(18 * scale), shadow=False)
    d = ImageDraw.Draw(canvas)
    area = (chart[0] + 58 * scale, chart[1] + 82 * scale, chart[2] - 58 * scale, chart[3] - 130 * scale)
    for i in range(5):
        yy = area[1] + i * (area[3] - area[1]) / 4
        d.line((area[0], yy, area[2], yy), fill="#e8eee9", width=max(1, int(1.5 * scale)))
    pts = [(area[0], area[1] + (area[3] - area[1]) * .62), (area[0] + (area[2] - area[0]) * .20, area[1] + (area[3] - area[1]) * .54), (area[0] + (area[2] - area[0]) * .40, area[1] + (area[3] - area[1]) * .61), (area[0] + (area[2] - area[0]) * .60, area[1] + (area[3] - area[1]) * .42), (area[0] + (area[2] - area[0]) * .80, area[1] + (area[3] - area[1]) * .35), (area[2], area[1] + (area[3] - area[1]) * .25)]
    d.line(pts, fill=MINT, width=max(4, int(6 * scale)), joint="curve")
    for x, y in pts:
        d.ellipse((x - 9 * scale, y - 9 * scale, x + 9 * scale, y + 9 * scale), fill=PAPER, outline=MINT, width=max(2, int(4 * scale)))
    d.text((chart[0] + 60 * scale, chart[3] - 105 * scale), "直近の変化", font=font(int(18 * scale), True), fill=MUTED)
    d.text((chart[0] + 60 * scale, chart[3] - 72 * scale), "-1.4 kg", font=font(int(44 * scale), True), fill=INK)
    y = chart[3] + 34 * scale
    for date, value in [("6月27日", "68.4 kg"), ("6月24日", "68.8 kg"), ("6月21日", "69.1 kg")]:
        box = (sx + 36 * scale, y, sx + sw - 36 * scale, y + 92 * scale)
        panel(canvas, box, int(14 * scale), shadow=False)
        d = ImageDraw.Draw(canvas)
        d.text((box[0] + 28 * scale, box[1] + 28 * scale), date, font=font(int(22 * scale), True), fill=INK)
        d.text((box[2] - 170 * scale, box[1] + 25 * scale), value, font=font(int(27 * scale), True), fill=INK)
        y += 112 * scale
    rr(d, (sx + 36 * scale, y + 16 * scale, sx + sw - 36 * scale, y + 70 * scale), int(12 * scale), MINT)
    tw, _ = text_size(d, "記録", font(int(22 * scale), True))
    d.text((sx + sw / 2 - tw / 2, y + 30 * scale), "記録", font=font(int(22 * scale), True), fill=PAPER)


def screen_settings(canvas, sx, sy, sw, sh, scale, tablet=False):
    d = ImageDraw.Draw(canvas)
    app_header(d, sx, sy, sw, "消費カロリーと目標", "設定", scale)
    cloud = (sx + 36 * scale, sy + 340 * scale, sx + sw - 36 * scale, sy + 575 * scale)
    panel(canvas, cloud, int(18 * scale), fill="#eef8f2", outline="#cfe4d9", shadow=False)
    d = ImageDraw.Draw(canvas)
    d.text((cloud[0] + 28 * scale, cloud[1] + 26 * scale), "ログインとクラウド保存", font=font(int(26 * scale), True), fill=INK)
    d.text((cloud[0] + 28 * scale, cloud[1] + 72 * scale), "食事・写真・体重をクラウドに保存できます。", font=font(int(18 * scale)), fill=MUTED)
    fields_y = cloud[1] + 126 * scale
    if tablet:
        widths = [(cloud[0] + 28 * scale, 380 * scale), (cloud[0] + 426 * scale, 360 * scale)]
        for (x, w), label in zip(widths, ["メールアドレス", "パスワード（8文字以上）"]):
            rr(d, (x, fields_y, x + w, fields_y + 54 * scale), int(10 * scale), PAPER, LINE, 2)
            d.text((x + 14 * scale, fields_y + 15 * scale), label, font=font(int(16 * scale)), fill=MUTED)
        rr(d, (cloud[2] - 190 * scale, fields_y, cloud[2] - 28 * scale, fields_y + 54 * scale), int(10 * scale), MINT)
        d.text((cloud[2] - 139 * scale, fields_y + 15 * scale), "ログイン", font=font(int(17 * scale), True), fill=PAPER)
    else:
        rr(d, (cloud[0] + 28 * scale, fields_y, cloud[2] - 28 * scale, fields_y + 48 * scale), int(10 * scale), PAPER, LINE, 2)
        d.text((cloud[0] + 42 * scale, fields_y + 13 * scale), "メールアドレス", font=font(int(15 * scale)), fill=MUTED)
    grid = (sx + 36 * scale, sy + 610 * scale, sx + sw - 36 * scale, sy + (1040 if not tablet else 1020) * scale)
    panel(canvas, grid, int(18 * scale), shadow=False)
    d = ImageDraw.Draw(canvas)
    labels = [("体重 kg", "68.4"), ("身長 cm", "172"), ("年齢", "48"), ("活動量", "ふつう"), ("目標", "維持"), ("PFC目標", "バランス")]
    cols = 3 if tablet else 2
    gap = 18 * scale
    cell_w = (grid[2] - grid[0] - 56 * scale - gap * (cols - 1)) / cols
    for i, (label, value) in enumerate(labels):
        col = i % cols
        row = i // cols
        x = grid[0] + 28 * scale + col * (cell_w + gap)
        y = grid[1] + 32 * scale + row * 116 * scale
        d.text((x, y), label, font=font(int(16 * scale), True), fill=MUTED)
        rr(d, (x, y + 28 * scale, x + cell_w, y + 80 * scale), int(10 * scale), PAPER, LINE, 2)
        d.text((x + 14 * scale, y + 42 * scale), value, font=font(int(20 * scale)), fill=INK)
    account = (sx + 36 * scale, grid[3] + 34 * scale, sx + sw - 36 * scale, grid[3] + 215 * scale)
    panel(canvas, account, int(18 * scale), shadow=False)
    d = ImageDraw.Draw(canvas)
    d.text((account[0] + 28 * scale, account[1] + 26 * scale), "アカウント管理", font=font(int(25 * scale), True), fill=INK)
    d.text((account[0] + 28 * scale, account[1] + 70 * scale), "ログアウトやアカウント削除に対応しています。", font=font(int(18 * scale)), fill=MUTED)
    rr(d, (account[0] + 28 * scale, account[1] + 118 * scale, account[0] + 190 * scale, account[1] + 160 * scale), int(10 * scale), PAPER, LINE, 2)
    d.text((account[0] + 61 * scale, account[1] + 129 * scale), "ログアウト", font=font(int(16 * scale), True), fill=INK)


SCREENS = [
    ("overview", "食事・PFC・体重をまとめて記録", "毎日のカラダづくりをシンプルに見える化", screen_overview),
    ("meal_add", "食事をかんたん記録", "写真・食材・栄養情報をまとめて追加", screen_meal),
    ("history", "食事履歴をあとから確認", "カロリー・PFC・写真を見返せる", screen_history),
    ("weight", "体重の変化を記録", "日々の推移を見ながら続けられる", screen_weight),
    ("settings", "クラウド保存とアカウント管理", "ログイン・同期・削除にも対応", screen_settings),
]


LAYOUTS = {
    "iphone_65": {
        "size": (1242, 2688),
        "dir": OUT / "iphone_65",
        "prefix": "screenshot",
        "scale": 1.0,
        "headline": 72,
        "subtitle": 38,
        "logo": (88, 92, 96),
        "brand": (206, 111, 34, 22),
        "headline_y": 260,
        "subtitle_y": 370,
        "subtitle_w": 1020,
        "device": (142, 640, 958, 1880),
        "device_radius": 96,
        "bezel": 22,
        "screen_pad_x": 54,
        "screen_pad_y": 66,
        "screen_pad_bottom": 68,
        "screen_radius": 44,
        "shadow_dx": 24,
        "shadow_dy": 34,
        "shadow_blur": 28,
        "kind": "phone",
        "notch_y": 28,
        "notch_h": 36,
    },
    "ipad_13": {
        "size": (2048, 2732),
        "dir": OUT / "ipad_13",
        "prefix": "ipad_screenshot",
        "scale": 1.32,
        "headline": 84,
        "subtitle": 45,
        "logo": (130, 92, 112),
        "brand": (268, 118, 42, 26),
        "headline_y": 286,
        "subtitle_y": 408,
        "subtitle_w": 1500,
        "device": (160, 650, 1728, 1905),
        "device_radius": 78,
        "bezel": 24,
        "screen_pad_x": 62,
        "screen_pad_y": 72,
        "screen_pad_bottom": 70,
        "screen_radius": 36,
        "shadow_dx": 32,
        "shadow_dy": 42,
        "shadow_blur": 32,
        "kind": "tablet",
        "camera_y": 34,
        "camera_r": 13,
    },
}


def draw_shell(layout, headline, subtitle):
    width, height = layout["size"]
    im = bg(width, height)
    d = ImageDraw.Draw(im)
    ix, iy, isize = layout["logo"]
    app_icon(d, ix, iy, isize)
    bx, by, bsize, ssize = layout["brand"]
    d.text((bx, by), "カラダログ＋", font=font(bsize, True), fill=INK)
    d.text((bx, by + bsize + 8), "食事・PFC・体重の記録アプリ", font=font(ssize), fill=MUTED)
    center_text(d, width, layout["headline_y"], headline, layout["headline"], INK, True, True)
    center_wrap(d, width, layout["subtitle_y"], subtitle, layout["subtitle"], layout["subtitle_w"], MUTED)
    return im


def render_all():
    for layout_name, layout in LAYOUTS.items():
        layout["dir"].mkdir(parents=True, exist_ok=True)
        for index, (slug, headline, subtitle, renderer) in enumerate(SCREENS, 1):
            image = draw_shell(layout, headline, subtitle)
            sx, sy, sw, sh = device_frame(image, layout)
            renderer(image, sx, sy, sw, sh, layout["scale"], tablet=layout_name == "ipad_13")
            if layout_name == "iphone_65":
                filename = f"{layout['prefix']}_{index:02d}_{slug}.png"
            else:
                filename = f"{layout['prefix']}_{index:02d}_{slug}.png"
            image.convert("RGB").save(layout["dir"] / filename, "PNG", optimize=True)


if __name__ == "__main__":
    render_all()
