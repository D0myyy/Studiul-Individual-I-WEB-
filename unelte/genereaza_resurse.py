# -*- coding: utf-8 -*-
"""Generează automat TOATE resursele site-ului „Psihologia Umană” (WEB2):

  imagini/  sigla.png, sigla.svg, banner-minte.png, harta-psihic.svg,
            curba-uitarii.png, curba-uitarii-mica.png, curba-uitarii.svg,
            roata-emotiilor.png, hipnograma-somn.png, creier-dezvoltare.svg,
            coperta-video.png, coperta-audio.png, galerie-atentie.png,
            galerie-memorie.png, galerie-emotii.png, galerie-somn.png
  video/    respiratie-478.mp4  (8 s, 320x240 — cerc care respiră 4-7-8)
  audio/    sunet-relaxare.wav (16 s, acord A3+E4+A4 cu anvelopă lentă)
            metronom.wav       (6 s, 120 bpm, bătăi 4/4)

Se rulează din rădăcina proiectului:   python WEB2/unelte/genereaza_resurse.py
Dependențe: Pillow (poze) + imageio-ffmpeg (video). Sunetele: doar Python pur.
"""

import math
import os
import struct
import subprocess
import tempfile
import wave

from PIL import Image, ImageDraw, ImageFont

AICI = os.path.dirname(os.path.abspath(__file__))
WEB2 = os.path.abspath(os.path.join(AICI, ".."))

DIR_IMAGINI = os.path.join(WEB2, "imagini")
DIR_VIDEO = os.path.join(WEB2, "video")
DIR_AUDIO = os.path.join(WEB2, "audio")

# ---------------------------------------------------------------- paleta ----
# Paleta „navy & rose” — modernă, elegantă, corelată între ea.
ALBASTRU = (34, 34, 59)      # 22223B — bleumarin adânc (text, benzi)
MOV = (74, 78, 105)          # 4A4E69 — mov-albăstrui (linkuri, corp grafic)
ROZ_VECHI = (154, 140, 152)  # 9A8C98 — roz vechi (elemente secundare)
ROZ_PRAF = (201, 173, 167)   # C9ADA7 — roz prăfos (accent cald)
ALBASTRU_C = (232, 224, 240) # E8E0F0 — lavandă deschisă (fonduri casete)
ALB_Cald = (242, 233, 228)   # F2E9E4 — alabastru (fond)
ALB = (255, 255, 255)
VERDE_S = (82, 121, 111)     # 52796F — verde salvie (meter/progress grafic)
AURIU = (188, 146, 76)       # BC924C — auriu discret (detalii)


def font(dimensiune, bold=False):
    """Font TrueType disponibil pe Windows, cu fallback serif."""
    nume = "georgiab.ttf" if bold else "georgia.ttf"
    try:
        return ImageFont.truetype(nume, dimensiune)
    except OSError:
        return ImageFont.load_default()


def fundal_latime(latime, inaltime, baza=ALB_Cald):
    """Fond degrade subtil vertical: alabastru spre lavandă foarte deschisă."""
    img = Image.new("RGB", (latime, inaltime), baza)
    d = ImageDraw.Draw(img)
    for y in range(inaltime):
        raport = y / max(1, inaltime - 1)
        r = int(baza[0] + (ALBASTRU_C[0] - baza[0]) * raport)
        g = int(baza[1] + (ALBASTRU_C[1] - baza[1]) * raport)
        b = int(baza[2] + (ALBASTRU_C[2] - baza[2]) * raport)
        d.line([(0, y), (latime, y)], fill=(r, g, b))
    return img


def salveaza(img, nume):
    cale = os.path.join(DIR_IMAGINI, nume)
    if nume.endswith(".svg"):
        with open(cale, "w", encoding="utf-8") as f:
            f.write(img)
    else:
        img.save(cale)
    print("scris:", os.path.relpath(cale, WEB2))


# ------------------------------------------------------------- imagini ------
def genereaza_sigla():
    """Sigla 128x128: profil de cap cu undă cerebrală."""
    img = Image.new("RGBA", (128, 128), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    d.ellipse([4, 4, 124, 124], fill=ALBASTRU)
    d.ellipse([10, 10, 118, 118], outline=ROZ_PRAF, width=3)
    # profil de cap (simplificat)
    d.pieslice([34, 26, 98, 90], start=250, end=90, fill=ALB_Cald)
    d.rectangle([62, 58, 92, 92], fill=ALB_Cald)
    d.ellipse([66, 44, 76, 54], fill=ALBASTRU)          # ochi
    # undă cerebrală
    puncte = []
    for x in range(14, 114, 2):
        y = 40 + 10 * math.sin((x - 14) / 100 * 4 * math.pi)
        puncte.append((x, y))
    d.line(puncte, fill=ROZ_PRAF, width=4)
    salveaza(img, "sigla.png")


def genereaza_sigla_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="200" height="200" viewBox="0 0 200 200">
  <circle cx="100" cy="100" r="94" fill="#22223B"/>
  <circle cx="100" cy="100" r="84" fill="none" stroke="#C9ADA7" stroke-width="5"/>
  <path d="M62 132 C58 96 66 62 96 58 C126 54 140 78 136 100 C132 122 114 128 114 148 L70 148 Z" fill="#F2E9E4"/>
  <circle cx="104" cy="88" r="7" fill="#22223B"/>
  <path d="M40 44 q10 -14 20 0 t20 0 t20 0 t20 0 t20 0" stroke="#C9ADA7" stroke-width="6" fill="none" stroke-linecap="round"/>
  <path d="M40 164 q10 -14 20 0 t20 0 t20 0 t20 0 t20 0" stroke="#9A8C98" stroke-width="6" fill="none" stroke-linecap="round"/>
</svg>
"""
    salveaza(svg, "sigla.svg")


def genereaza_banner():
    """Banner 960x160: mintea — rețea de noduri și legături."""
    img = fundal_latime(960, 160)
    d = ImageDraw.Draw(img)
    # bandă superioară și inferioară
    d.rectangle([0, 0, 959, 14], fill=ALBASTRU)
    d.rectangle([0, 146, 959, 159], fill=ALBASTRU)
    noduri = [(90, 80), (200, 50), (200, 110), (320, 80), (440, 45),
              (440, 115), (560, 80), (680, 50), (680, 110), (800, 80), (900, 80)]
    for i in range(len(noduri) - 1):
        d.line([noduri[i], noduri[i + 1]], fill=MOV, width=2)
    d.line([noduri[1], noduri[2]], fill=MOV, width=2)
    d.line([noduri[5], noduri[6]], fill=MOV, width=2)
    for i, (x, y) in enumerate(noduri):
        raza = 9 if i % 3 == 0 else 6
        culoare = ROZ_PRAF if i % 3 == 0 else ROZ_VECHI
        d.ellipse([x - raza, y - raza, x + raza, y + raza], fill=culoare, outline=ALBASTRU)
    d.text((330, 66), "PSIHOLOGIA UMANĂ", font=font(34, True), fill=ALBASTRU)
    d.text((332, 104), "mintea, pas cu pas", font=font(18), fill=MOV)
    salveaza(img, "banner-minte.png")


def genereaza_harta_svg():
    """Harta psihicului (SVG, zone text clare) — folosită cu usemap."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="400" height="250" viewBox="0 0 400 250">
  <rect x="0" y="0" width="400" height="250" fill="#F2E9E4"/>
  <rect x="0" y="0" width="400" height="250" fill="none" stroke="#22223B" stroke-width="2"/>
  <rect x="12" y="12" width="376" height="52" rx="10" fill="#22223B"/>
  <text x="200" y="45" text-anchor="middle" font-family="Georgia, serif" font-size="22" fill="#F2E9E4">CONȘTIINȚA</text>
  <rect x="12" y="72" width="108" height="108" rx="10" fill="#C9ADA7"/>
  <text x="66" y="120" text-anchor="middle" font-family="Georgia, serif" font-size="16" fill="#22223B">ATENȚIA</text>
  <text x="66" y="142" text-anchor="middle" font-family="Georgia, serif" font-size="12" fill="#4A4E69">percepție</text>
  <rect x="128" y="72" width="124" height="108" rx="10" fill="#9A8C98"/>
  <text x="190" y="120" text-anchor="middle" font-family="Georgia, serif" font-size="16" fill="#F2E9E4">MEMORIA</text>
  <text x="190" y="142" text-anchor="middle" font-family="Georgia, serif" font-size="12" fill="#F2E9E4">învățare</text>
  <rect x="260" y="72" width="128" height="108" rx="10" fill="#4A4E69"/>
  <text x="324" y="120" text-anchor="middle" font-family="Georgia, serif" font-size="16" fill="#F2E9E4">EMOȚIILE</text>
  <text x="324" y="142" text-anchor="middle" font-family="Georgia, serif" font-size="12" fill="#C9ADA7">trăiri</text>
  <rect x="12" y="188" width="376" height="50" rx="10" fill="#E8E0F0"/>
  <text x="200" y="219" text-anchor="middle" font-family="Georgia, serif" font-size="16" fill="#4A4E69">SUBCONȘTIENTUL — somn și consolidare</text>
</svg>
"""
    salveaza(svg, "harta-psihic.svg")


def genereaza_curba_uitarii():
    """Curba uitării (Ebbinghaus) — 640x360 mare + 320x180 mică pentru <picture>."""
    def deseneaza(latime, inaltime, cu_etichete):
        img = fundal_latime(latime, inaltime)
        d = ImageDraw.Draw(img)
        mx, my, W, H = 50, 24, latime - 70, inaltime - 64
        d.line([(mx, my), (mx, my + H), (mx + W, my + H)], fill=ALBASTRU, width=2)
        puncte = []
        for zi in range(0, 31):
            retentie = math.exp(-zi / 6.0)          # model R = e^(-t/s)
            x = mx + W * zi / 30
            y = my + H * (1 - retentie)
            puncte.append((x, y))
        d.line(puncte, fill=MOV, width=4)
        # grafic comparativ: repetiția spațiată
        puncte2 = []
        for zi in range(0, 31):
            retentie = min(1.0, math.exp(-zi / 18.0) + 0.45 * math.exp(-abs(zi - 1) / 2.0)
                           + 0.25 * math.exp(-abs(zi - 7) / 3.0))
            x = mx + W * zi / 30
            y = my + H * (1 - retentie)
            puncte2.append((x, y))
        d.line(puncte2, fill=ROZ_PRAF, width=4)
        for x, y in puncte[::6]:
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=ALBASTRU)
        for x, y in puncte2[::6]:
            d.ellipse([x - 3, y - 3, x + 3, y + 3], fill=ROZ_VECHI)
        if cu_etichete:
            d.text((mx - 44, my + H - 8), "100%", font=font(13), fill=ALBASTRU)
            d.text((mx - 34, my + H // 2 - 8), "50%", font=font(13), fill=ALBASTRU)
            d.text((mx - 44, my + H - 28), "retenție", font=font(11), fill=MOV)
            d.text((mx + W - 60, my + H + 8), "zile", font=font(13), fill=ALBASTRU)
            d.text((mx + 8, my + 4), "fără repetiție", font=font(13), fill=ALBASTRU)
            d.text((mx + 150, my + 120), "cu repetiție", font=font(13), fill=ROZ_VECHI)
        return img
    salveaza(deseneaza(640, 360, True), "curba-uitarii.png")
    salveaza(deseneaza(320, 180, False), "curba-uitarii-mica.png")


def genereaza_curba_svg():
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="400" height="220" viewBox="0 0 400 220">
  <rect width="400" height="220" fill="#F2E9E4"/>
  <line x1="40" y1="20" x2="40" y2="180" stroke="#22223B" stroke-width="2"/>
  <line x1="40" y1="180" x2="380" y2="180" stroke="#22223B" stroke-width="2"/>
  <path d="M40 20 C 70 90, 100 130, 160 150 C 240 168, 320 174, 380 176" fill="none" stroke="#4A4E69" stroke-width="4"/>
  <path d="M40 20 C 80 40, 140 60, 200 72 C 260 84, 320 88, 380 90" fill="none" stroke="#C9ADA7" stroke-width="4" stroke-dasharray="8,6"/>
  <text x="46" y="34" font-family="Georgia, serif" font-size="13" fill="#22223B">fără repetiție</text>
  <text x="250" y="66" font-family="Georgia, serif" font-size="13" fill="#9A8C98">cu repetiție spațiată</text>
  <text x="200" y="206" text-anchor="middle" font-family="Georgia, serif" font-size="13" fill="#4A4E69">timp (zile)</text>
  <text x="18" y="105" font-family="Georgia, serif" font-size="13" fill="#4A4E69" transform="rotate(-90 18 105)">retenție</text>
</svg>
"""
    salveaza(svg, "curba-uitarii.svg")


def genereaza_roata_emotiilor():
    """Roata emoțiilor — 6 sectoare colorate, 420x420."""
    img = fundal_latime(420, 420)
    d = ImageDraw.Draw(img)
    cx, cy, R = 210, 210, 180
    emocki = ["BUCURIE", "ÎnTRISTARE", "FRICĂ", "MÂNIE", "MIRARE", "DEGUSTARE"]
    culori = [ROZ_PRAF, MOV, ALBASTRU, ROZ_VECHI, VERDE_S, AURIU]
    pas = 360 / 6
    for i in range(6):
        start = -90 + i * pas
        d.pieslice([cx - R, cy - R, cx + R, cy + R], start=start, end=start + pas,
                   fill=culori[i], outline=ALB)
        # eticheta la marginea exterioară
        unghi = math.radians(start + pas / 2)
        tx = cx + (R - 46) * math.cos(unghi)
        ty = cy + (R - 46) * math.sin(unghi)
        eticheta = emocki[i].upper()
        d.text((tx - 44, ty - 8), eticheta, font=font(12, True),
               fill=ALB if i in (2,) else ALBASTRU)
    d.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=ALB, outline=ALBASTRU, width=3)
    d.text((cx - 40, cy - 12), "EMOȚII DE", font=font(11, True), fill=ALBASTRU)
    d.text((cx - 26, cy + 4), "BAZĂ", font=font(11, True), fill=ALBASTRU)
    salveaza(img, "roata-emotiilor.png")


def genereaza_hipnograma():
    """Hipnograma somnului — etapele N1, N2, N3, REM de-a lungul nopții."""
    img = fundal_latime(640, 300)
    d = ImageDraw.Draw(img)
    mx, W = 60, 540
    niveluri = {"vegă": 30, "REM": 90, "N1": 150, "N2": 210, "N3": 250}
    ymap = {k: v for k, v in niveluri.items()}
    for nume, y in niveluri.items():
        d.line([(mx, y), (mx + W, y)], fill=ALBASTRU_C, width=2)
        d.text((mx - 52, y - 8), nume, font=font(13, True), fill=MOV)
    # traseu: vegă → N1 → N2 → N3 → N2 → REM → N2 → N3 → REM → vegă
    secvente = [("vegă", 0, 40), ("N1", 40, 90), ("N2", 90, 170), ("N3", 170, 250),
                ("N2", 250, 300), ("REM", 300, 370), ("N2", 370, 420),
                ("N3", 420, 470), ("REM", 470, 540)]
    anterior = None
    for nume, a, b in secvente:
        y = ymap[nume]
        culoare = ROZ_PRAF if nume == "REM" else MOV
        if anterior is not None:
            d.line([(mx + anterior, ymap[anterior_nume]), (mx + a, y)], fill=culoare, width=3)
        d.line([(mx + a, y), (mx + b, y)], fill=culoare, width=6)
        anterior, anterior_nume = b, nume
    d.line([(mx, 30), (mx + W, 30)], fill=ROZ_VECHI, width=1)
    d.text((mx + W - 120, 8), "→ dimineața", font=font(12), fill=ROZ_VECHI)
    salveaza(img, "hipnograma-somn.png")


def genereaza_creier_svg():
    """Dezvoltarea creierului — sinapse la 3 vârste (SVG)."""
    svg = """<svg xmlns="http://www.w3.org/2000/svg" width="520" height="180" viewBox="0 0 520 180">
  <rect width="520" height="180" fill="#F2E9E4"/>
  <g>
    <circle cx="85" cy="80" r="34" fill="#C9ADA7"/>
    <text x="85" y="140" text-anchor="middle" font-family="Georgia, serif" font-size="14" fill="#22223B">nou-născut</text>
  </g>
  <g>
    <circle cx="260" cy="80" r="34" fill="#9A8C98"/>
    <line x1="240" y1="60" x2="280" y2="100" stroke="#F2E9E4" stroke-width="2"/>
    <line x1="280" y1="60" x2="240" y2="100" stroke="#F2E9E4" stroke-width="2"/>
    <text x="260" y="140" text-anchor="middle" font-family="Georgia, serif" font-size="14" fill="#22223B">copil</text>
  </g>
  <g>
    <circle cx="435" cy="80" r="34" fill="#4A4E69"/>
    <line x1="412" y1="55" x2="458" y2="105" stroke="#F2E9E4" stroke-width="2"/>
    <line x1="458" y1="55" x2="412" y2="105" stroke="#F2E9E4" stroke-width="2"/>
    <line x1="412" y1="80" x2="458" y2="80" stroke="#C9ADA7" stroke-width="2"/>
    <line x1="435" y1="52" x2="435" y2="108" stroke="#C9ADA7" stroke-width="2"/>
    <text x="435" y="140" text-anchor="middle" font-family="Georgia, serif" font-size="14" fill="#22223B">adult</text>
  </g>
  <text x="260" y="168" text-anchor="middle" font-family="Georgia, serif" font-size="13" fill="#9A8C98">prunarea: mai puține, dar mai puternice legături</text>
</svg>
"""
    salveaza(svg, "creier-dezvoltare.svg")


def genereaza_coperta_video():
    """Poster 640x360 pentru <video poster>: cerc concentrat pe bandă lavandă."""
    img = fundal_latime(640, 360, ALBASTRU_C)
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, 639, 359], outline=ALBASTRU, width=4)
    cx, cy = 320, 180
    for raza, culoare in [(140, MOV), (110, ROZ_VECHI), (80, ROZ_PRAF),
                          (52, ALB), (26, ALBASTRU)]:
        d.ellipse([cx - raza, cy - raza, cx + raza, cy + raza], fill=culoare)
    for x, y in [(46, 46), (594, 46), (46, 314), (594, 314)]:
        d.ellipse([x - 9, y - 9, x + 9, y + 9], fill=AURIU)
    d.text((210, 320), "respirația 4 · 7 · 8", font=font(20, True), fill=ALBASTRU)
    salveaza(img, "coperta-video.png")


def genereaza_coperta_audio():
    """Copertă 300x300 pentru secțiunea audio."""
    img = fundal_latime(300, 300, ALBASTRU_C)
    d = ImageDraw.Draw(img)
    d.ellipse([40, 40, 260, 260], fill=ALBASTRU)
    for i, raza in enumerate([86, 66, 46]):
        culoare = [ROZ_PRAF, ROZ_VECHI, MOV][i]
        d.arc([150 - raza, 150 - raza, 150 + raza, 150 + raza], start=-60, end=140,
              fill=culoare, width=8)
    d.ellipse([136, 136, 164, 164], fill=ROZ_PRAF)
    salveaza(img, "coperta-audio.png")


def genereaza_galerie():
    """4 miniaturi pentru galeria multimedia (300x200 fiecare)."""
    teme = [
        ("galerie-atentie.png", "ATENȚIA", [(ALBASTRU, 110), (ROZ_PRAF, 60), (ALB, 26)], "observă un singur gând"),
        ("galerie-memorie.png", "MEMORIA", [(MOV, 110), (ALBASTRU_C, 60), (ALB, 26)], "amintește-ți cu repetiție"),
        ("galerie-emotii.png", "EMOȚIILE", [(ROZ_VECHI, 110), (ROZ_PRAF, 60), (ALB, 26)], "numește-ți trăirea"),
        ("galerie-somn.png", "SOMNUL", [(VERDE_S, 110), (ALBASTRU_C, 60), (ALB, 26)], "dormi pentru memorie"),
    ]
    for nume, titlu, cercuri, subtitlu in teme:
        img = fundal_latime(300, 200, ALBASTRU_C)
        d = ImageDraw.Draw(img)
        d.rectangle([0, 0, 299, 199], outline=ALBASTRU, width=3)
        cx, cy = 150, 92
        for culoare, raza in cercuri:
            d.ellipse([cx - raza, cy - raza, cx + raza, cy + raza], fill=culoare)
        d.text((150 - len(titlu) * 7, 158), titlu, font=font(17, True), fill=ALBASTRU)
        d.text((150 - len(subtitlu) * 4, 180), subtitlu, font=font(11), fill=MOV)
        salveaza(img, nume)


# --------------------------------------------------------------- video ------
def genereaza_video():
    """MP4 8 s, 320x240: cerc care se dilată (4 s) și contractă (4 s) — modelul
    „vizualizează-ți respirația”. Codificare cu ffmpeg din imageio-ffmpeg."""
    import imageio_ffmpeg

    latime, inaltime = 320, 240
    fps = 12
    durata = 8.0
    total = int(fps * durata)

    cale_video = os.path.join(DIR_VIDEO, "respiratie-478.mp4")
    cale_ffmpeg = imageio_ffmpeg.get_ffmpeg_exe()
    cmd = [
        cale_ffmpeg, "-y",
        "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{latime}x{inaltime}", "-r", str(fps), "-i", "-",
        "-an",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "26",
        "-pix_fmt", "yuv420p", "-movflags", "+faststart",
        cale_video,
    ]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE,
                            stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    for cadru in range(total):
        t = cadru / fps
        ciclu = 8.0                       # 4 s inspir + 4 s expir
        faza = (t % ciclu) / ciclu        # 0..1
        raza = 44 + 58 * (1 - math.cos(math.pi * faza)) / 2   # 44 → 102 → 44
        img = fundal_latime(latime, inaltime, ALBASTRU_C)
        d = ImageDraw.Draw(img)
        for factor, culoare in [(1.35, MOV), (1.12, ROZ_VECHI), (0.9, ROZ_PRAF)]:
            r = int(raza * factor)
            d.ellipse([160 - r, 120 - r, 160 + r, 120 + r], fill=culoare)
        r = int(raza * 0.68)
        d.ellipse([160 - r, 120 - r, 160 + r, 120 + r], fill=ALB)
        eticheta = "inspiră…… 4 s" if faza < 0.5 else "expiră…… 4 s"
        d.text((104, 210), eticheta, font=font(14, True), fill=ALBASTRU)
        proc.stdin.write(img.tobytes())
    proc.stdin.close()
    proc.wait()
    print("scris:", os.path.relpath(cale_video, WEB2))


# --------------------------------------------------------------- audio ------
def scrie_wav(cale, esantioane, frecventa=22050):
    with wave.open(cale, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(frecventa)
        cadre = bytearray()
        for val in esantioane:
            v = max(-1.0, min(1.0, val))
            cadre += struct.pack("<h", int(v * 32767))
        w.writeframes(bytes(cadre))
    print("scris:", os.path.relpath(cale, WEB2))


def genereaza_sunet_relaxare():
    """16 s: acord A3 + E4 + A4 cu val lent de intensitate și margini line."""
    fs = 22050
    durata = 16.0
    n = int(fs * durata)
    doi_pi = 2 * math.pi
    esantioane = []
    for i in range(n):
        t = i / fs
        val = 0.72 + 0.28 * math.sin(doi_pi * 0.125 * t)   # val de 8 s
        ton = (0.50 * math.sin(doi_pi * 220 * t)            # A3
               + 0.32 * math.sin(doi_pi * 330 * t)          # E4
               + 0.18 * math.sin(doi_pi * 440 * t))         # A4
        val *= ton * 0.36
        if t < 2:
            val *= t / 2
        if t > durata - 3:
            val *= max(0.0, (durata - t) / 3)
        esantioane.append(val)
    scrie_wav(os.path.join(DIR_AUDIO, "sunet-relaxare.wav"), esantioane, fs)


def genereaza_metronom():
    """6 s metronom 120 bpm (bătai la fiecare 0,5 s) — pentru exercițiul de atenție."""
    fs = 22050
    durata = 6.0
    n = int(fs * durata)
    esantioane = [0.0] * n
    pas_bataie = int(fs * 0.5)          # 120 bpm
    for start in range(0, n - 800, pas_bataie):
        for j in range(800):            # bătaie de 36 ms, decay rapid
            t = j / fs
            esantioane[start + j] += 0.6 * math.exp(-t * 90) * math.sin(2 * math.pi * 1000 * t)
    scrie_wav(os.path.join(DIR_AUDIO, "metronom.wav"), esantioane, fs)


if __name__ == "__main__":
    for d in (DIR_IMAGINI, DIR_VIDEO, DIR_AUDIO):
        os.makedirs(d, exist_ok=True)
    genereaza_sigla()
    genereaza_sigla_svg()
    genereaza_banner()
    genereaza_harta_svg()
    genereaza_curba_uitarii()
    genereaza_curba_svg()
    genereaza_roata_emotiilor()
    genereaza_hipnograma()
    genereaza_creier_svg()
    genereaza_coperta_video()
    genereaza_coperta_audio()
    genereaza_galerie()
    genereaza_video()
    genereaza_sunet_relaxare()
    genereaza_metronom()
    print("GATA — toate resursele au fost generate.")
