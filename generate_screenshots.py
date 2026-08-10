#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
App Store スクリーンショット生成テンプレート
================================================
撮った実機スクショを「背景 + デバイス枠 + キャッチコピー + (任意)バッジ」に合成します。
架空UIは一切描きません。screens/ に置いた本物のスクショを読み込むだけです。

使い方:
  1. screens/iphone/ に実機スクショ(縦)を置く。例: 01_home.png, 02_meal.png ...
  2. screens/ipad/   にiPad用スクショを置く(iPad対応アプリのみ)
  3. 下の CONFIG を編集 (色・コピー・どのスクショを使うか)
  4. python3 generate_screenshots.py
  5. output/ に App Store 提出サイズのPNGが出る

依存: Pillow (pip install Pillow)
"""

from PIL import Image, ImageDraw, ImageFont
import os

# ============================================================
# CONFIG ── ここだけ編集すればOK
# ============================================================

# --- テーマ色 (カラダログ+ のブランドに合わせて。見本の青緑にしたいなら BG を '#79D2C8' などに) ---
THEME = {
    "bg":            "#EAF6F2",  # 背景色 (淡いグリーン系。ベタ塗り)
    "bg_gradient":   "#D6EFE7",  # 背景下部の色 (上の bg からのグラデ。同じ色にすればベタ塗り)
    "headline":      "#2E7D6B",  # キャッチコピーの文字色
    "frame":         "#FFFFFF",  # デバイス枠の色
    "frame_border":  "#DDE7E3",  # 枠の細い縁取り
    "badge_bg":      "#F4A0A0",  # 丸バッジの背景 (使う場合)
    "badge_text":    "#FFFFFF",  # 丸バッジの文字
}

# --- 提出サイズ (2026年現行) ---
# iPhone: 1242x2688 (6.5インチ)
# iPad  : 2048x2732 (13インチ)。新サイズ 2064x2752 も可
DEVICES = {
    "iphone": {"canvas": (1242, 2688), "screen_w_ratio": 0.74},
    "ipad":   {"canvas": (2048, 2732), "screen_w_ratio": 0.78},
}

# --- 各スクショの設定 ---
# src       : screens/<device>/ 内のファイル名
# headline  : キャッチコピー。改行は \n で手動指定 (日本語は手で改行した方がキレイ)
# badge     : 丸バッジ。不要なら None。 {"text": "見える", "pos": "tr"} pos= tr/tl/br/bl
#
# ※ 「No.1」「使いやすさ最高」等の検証できない主張はApp Store審査で弾かれやすいので避ける
SCREENS = {
    "iphone": [
        {"src": "01_home.png",  "headline": "食事も体重も\nこれひとつで",     "badge": None},
        {"src": "02_meal.png",  "headline": "写真でかんたん\n記録",          "badge": {"text": "OK", "pos": "tr"}},
        {"src": "03_ai.png",    "headline": "AIが栄養を\n推定でサポート",     "badge": None},
        {"src": "04_weight.png","headline": "体重の変化を\nグラフで見える化", "badge": {"text": "見える", "pos": "tr"}},
        {"src": "05_history.png","headline": "毎日の記録を\nふり返る",        "badge": None},
    ],
    "ipad": [
        {"src": "01_home.png",  "headline": "食事も体重も\nこれひとつで",     "badge": None},
        {"src": "02_weight.png","headline": "体重の変化を\nグラフで見える化", "badge": None},
        {"src": "03_meal.png",  "headline": "写真でかんたん記録",            "badge": None},
    ],
}

# --- レイアウト微調整 ---
HEADLINE_TOP_RATIO  = 0.07   # 上端からキャッチコピーまでの余白(キャンバス高さ比)
HEADLINE_MAX_RATIO  = 0.85   # キャッチコピーの最大横幅(キャンバス幅比)
DEVICE_TOP_RATIO    = 0.27   # デバイス上端の位置(キャンバス高さ比)

# ============================================================
# 以下、処理本体 (通常は触らない)
# ============================================================

BASE = os.path.dirname(os.path.abspath(__file__))
SCREENS_DIR = os.path.join(BASE, "screens")
OUT_DIR = os.path.join(BASE, "output")


def _find_font(candidates):
    """環境に存在する最初のフォントパスを返す (Mac / Linux 両対応)"""
    for p in candidates:
        if p and os.path.exists(p):
            return p
    return None


# 太字(見出し用)。上から順に探して最初に見つかったものを使う
FONT_BLACK = _find_font([
    os.path.join(BASE, "fonts", "NotoSansJP-Black.ttf"),     # プロジェクト同梱(最も確実・git管理推奨)
    "/System/Library/Fonts/ヒラギノ角ゴシック W8.ttc",         # macOS 標準
    "/System/Library/Fonts/ヒラギノ角ゴシック W7.ttc",
    "/System/Library/Fonts/Hiragino Sans W8.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc",   # Linux (Codexクラウド等)
    "/Library/Fonts/NotoSansCJKjp-Black.otf",
])
FONT_BOLD = _find_font([
    os.path.join(BASE, "fonts", "NotoSansJP-Bold.ttf"),
    "/System/Library/Fonts/ヒラギノ角ゴシック W6.ttc",
    "/System/Library/Fonts/Hiragino Sans W6.ttc",
    "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc",
    "/Library/Fonts/NotoSansCJKjp-Bold.otf",
]) or FONT_BLACK

if FONT_BLACK is None:
    raise SystemExit(
        "日本語フォントが見つかりません。\n"
        "対処: プロジェクトに fonts/ フォルダを作り NotoSansJP-Black.ttf を入れる "
        "(Google Fontsから無料DL) か、Macなら標準のヒラギノが自動で使われます。"
    )


def font(path, size):
    return ImageFont.truetype(path, size)


def rounded_mask(size, radius):
    """角丸のアルファマスクを作る"""
    mask = Image.new("L", size, 0)
    d = ImageDraw.Draw(mask)
    d.rounded_rectangle([0, 0, size[0] - 1, size[1] - 1], radius=radius, fill=255)
    return mask


def fit_cover(img, target_w, target_h):
    """アスペクト比を保ったまま target を埋めるようにリサイズ+中央クロップ"""
    src_w, src_h = img.size
    scale = max(target_w / src_w, target_h / src_h)
    new_w, new_h = int(src_w * scale + 0.5), int(src_h * scale + 0.5)
    img = img.resize((new_w, new_h), Image.LANCZOS)
    left = (new_w - target_w) // 2
    top = (new_h - target_h) // 2
    return img.crop((left, top, left + target_w, top + target_h))


def vertical_gradient(size, top_hex, bottom_hex):
    """上から下へのグラデ背景"""
    w, h = size
    top = tuple(int(top_hex[i:i+2], 16) for i in (1, 3, 5))
    bot = tuple(int(bottom_hex[i:i+2], 16) for i in (1, 3, 5))
    base = Image.new("RGB", size, top)
    if top == bot:
        return base
    grad = Image.new("L", (1, h))
    for y in range(h):
        grad.putpixel((0, y), int(255 * y / max(h - 1, 1)))
    grad = grad.resize(size)
    overlay = Image.new("RGB", size, bot)
    return Image.composite(overlay, base, grad)


def draw_device(canvas, screenshot, device_key):
    """デバイス枠を描いて中に実機スクショをはめ込む"""
    cw, ch = canvas.size
    spec = DEVICES[device_key]
    screen_w_ratio = spec["screen_w_ratio"]

    # 枠の外形サイズ
    frame_w = int(cw * screen_w_ratio)
    bezel = max(int(frame_w * 0.035), 14)          # 枠の太さ
    inner_w = frame_w - bezel * 2                   # 画面部分の幅
    # 画面のアスペクト比は元スクショのものを使う(本物に忠実)
    s_w, s_h = screenshot.size
    inner_h = int(inner_w * s_h / s_w)
    frame_h = inner_h + bezel * 2

    frame_radius = int(frame_w * 0.12)
    inner_radius = max(frame_radius - bezel, int(frame_radius * 0.7))

    # 枠(白い角丸＋細い縁取り)
    frame = Image.new("RGBA", (frame_w, frame_h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    fd.rounded_rectangle([0, 0, frame_w - 1, frame_h - 1], radius=frame_radius,
                         fill=THEME["frame"], outline=THEME["frame_border"],
                         width=max(int(bezel * 0.18), 2))

    # 画面(角丸クロップしたスクショ)
    screen = fit_cover(screenshot, inner_w, inner_h).convert("RGBA")
    screen.putalpha(rounded_mask((inner_w, inner_h), inner_radius))
    frame.paste(screen, (bezel, bezel), screen)

    # キャンバスに合成(横中央、上端は DEVICE_TOP_RATIO)
    fx = (cw - frame_w) // 2
    fy = int(ch * DEVICE_TOP_RATIO)
    canvas.paste(frame, (fx, fy), frame)
    return (fx, fy, frame_w, frame_h)


def draw_headline(canvas, text, device_key):
    """上部にキャッチコピーを描く(自動でフォントサイズ調整)"""
    cw, ch = canvas.size
    draw = ImageDraw.Draw(canvas)
    lines = text.split("\n")
    max_w = int(cw * HEADLINE_MAX_RATIO)

    # 最大サイズから縮めて収める
    size = int(cw * 0.13)
    while size > 24:
        f = font(FONT_BLACK, size)
        widest = max(draw.textlength(ln, font=f) for ln in lines)
        if widest <= max_w:
            break
        size -= 4
    f = font(FONT_BLACK, size)
    line_h = int(size * 1.18)

    y = int(ch * HEADLINE_TOP_RATIO)
    for ln in lines:
        w = draw.textlength(ln, font=f)
        x = (cw - w) // 2
        draw.text((x, y), ln, font=f, fill=THEME["headline"])
        y += line_h


def draw_badge(canvas, badge, device_key, device_box):
    """丸バッジ(吹き出し風)を描く"""
    if not badge:
        return
    cw, ch = canvas.size
    fx, fy, fw, fh = device_box
    d = ImageDraw.Draw(canvas)

    r = int(cw * 0.11)
    pos = badge.get("pos", "tr")
    cx = fx + fw - r if "r" in pos else fx + r
    cy = fy + r if "t" in pos else fy + fh - r
    # 枠から少しはみ出す感じに
    cx += int(r * 0.25) * (1 if "r" in pos else -1)
    cy -= int(r * 0.15)

    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=THEME["badge_bg"])
    txt = badge["text"]
    fsize = int(r * 0.7) if len(txt) <= 2 else int(r * 0.46)
    bf = font(FONT_BLACK, fsize)
    tw = d.textlength(txt, font=bf)
    bbox = bf.getbbox(txt)
    th = bbox[3] - bbox[1]
    d.text((cx - tw / 2, cy - th / 2 - bbox[1]), txt, font=bf, fill=THEME["badge_text"])


def render(device_key, screen_cfg):
    canvas = vertical_gradient(DEVICES[device_key]["canvas"],
                               THEME["bg"], THEME["bg_gradient"]).convert("RGBA")
    src_path = os.path.join(SCREENS_DIR, device_key, screen_cfg["src"])
    if not os.path.exists(src_path):
        print(f"  [スキップ] スクショが見つかりません: {src_path}")
        return None
    shot = Image.open(src_path).convert("RGB")
    box = draw_device(canvas, shot, device_key)
    draw_headline(canvas, screen_cfg["headline"], device_key)
    draw_badge(canvas, screen_cfg.get("badge"), device_key, box)
    return canvas.convert("RGB")  # 透過なし(App Store要件)


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for device_key, screens in SCREENS.items():
        print(f"== {device_key} ==")
        for i, cfg in enumerate(screens, 1):
            img = render(device_key, cfg)
            if img is None:
                continue
            out = os.path.join(OUT_DIR, f"{device_key}_{i:02d}.png")
            img.save(out, "PNG")
            print(f"  生成: {out}  ({img.size[0]}x{img.size[1]})")
    print("完了。output/ を確認してください。")


if __name__ == "__main__":
    main()
