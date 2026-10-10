# -*- coding: utf-8 -*-
"""Verificator automat pentru site-ul „Psihologia Umană” (WEB2).

Verifică:
  1. pe fiecare pagină: meta charset, title, h1, p, a, img, header/footer/nav/main/section;
  2. pe tot site-ul: fiecare tag cerut ≥ 1 dată + atributele-cheie;
  3. tipurile de <input>, toate cele 5 tipuri de <ol>, colspan/rowspan, method="get";
  4. toate fișierele locale referențiate există; ancorele încrucișate se rezolvă;
  5. meniul: <nav> pe fiecare pagină, cu legături către celelalte pagini;
  6. zero CSS/JS: fără <style>, <link>, <script>, style=, on*=;
  7. tag-urile sunt închise corect și imbricate corect (parser HTML strict).

Rulare din rădăcina proiectului:   python WEB2/unelte/verifica_site.py
Cod de ieșire: 0 = totul OK, 1 = probleme.
"""

import os
import re
import sys
from html.parser import HTMLParser

AICI = os.path.dirname(os.path.abspath(__file__))
WEB2 = os.path.abspath(os.path.join(AICI, ".."))

PAGINI = ["index.html", "ghid.html", "multimedia.html", "formular.html"]

VOID_TAGS = {"meta", "img", "br", "hr", "col", "source", "input", "area",
             "wbr", "embed", "track", "param", "link", "base"}

# tag -> atribute obligatorii (cel puțin o instanță a tag-ului cu acel atribut)
TAGURI_CERUTE = {
    "h1": [], "h2": [], "h3": [], "h4": [], "h5": [], "h6": [],
    "p": [], "br": [], "hr": [],
    "ul": [], "ol": [], "li": [],
    "dl": [], "dt": [], "dd": [],
    "b": [], "i": [], "u": [], "sub": [], "sup": [], "s": [],
    "strong": [], "code": [], "q": [],
    "img": ["src", "alt"],
    "picture": [], "source": ["srcset", "media"],
    "figure": [], "figcaption": [],
    "video": ["controls", "src", "poster", "width", "height", "loop", "muted"],
    "audio": ["controls"],
    "iframe": ["src", "width", "height", "title"],
    "table": [], "tr": [], "th": [], "td": [], "caption": [],
    "colgroup": [], "col": [],
    "form": ["action", "method"],
    "label": ["for"],
    "input": ["type"],
    "button": ["type"],
    "select": [], "option": [], "optgroup": [],
    "fieldset": [], "legend": [],
    "datalist": ["id"],
    "progress": ["value", "max"],
    "meter": ["value", "min", "max"],
    "textarea": [],
    "header": [], "footer": [], "nav": [], "main": [], "section": [],
    "article": [], "aside": [],
}

# cerințe per pagină („elemente HTML variate pe fiecare pagină”)
CERUTE_PE_PAGINA = ["h1", "p", "a", "img", "header", "footer", "nav", "main", "section"]

TIPURI_INPUT = {"text", "email", "number", "date", "time", "range", "radio", "checkbox"}
TIPURI_OL = {"1", "a", "A", "i", "I"}

REF_PATTERN = re.compile(r'(?:href|src|poster|srcset|action)="([^"]+)"')
ATTR_PATTERN = re.compile(r'([a-zA-Z][a-zA-Z0-9-]*)\s*=')


class VerificatorImbricare(HTMLParser):
    """Parser strict: semnalează tag-uri neînchise și închideri inversate."""

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stiva = []
        self.erori = []

    def handle_starttag(self, tag, attrs):
        if tag not in VOID_TAGS:
            self.stiva.append(tag)

    def handle_endtag(self, tag):
        if tag in VOID_TAGS:
            return
        if not self.stiva:
            self.erori.append(f"</{tag}> fără deschidere")
        elif self.stiva[-1] == tag:
            self.stiva.pop()
        elif tag in self.stiva:
            while self.stiva and self.stiva[-1] != tag:
                self.erori.append(f"</{self.stiva.pop()}> lipsește înainte de </{tag}>")
            if self.stiva:
                self.stiva.pop()
        else:
            self.erori.append(f"</{tag}> neașteptat (stiva: {self.stiva[-3:]})")


def citeste(cale):
    with open(cale, encoding="utf-8") as f:
        return f.read()


def parseaza(text):
    """Returnează lista (tag, șir_atribute) pentru toate tag-urile de deschidere."""
    rezultat = []
    for m in re.finditer(r"<([a-zA-Z][a-zA-Z0-9]*)((?:\s+[^<>]*?)?)>", text):
        rezultat.append((m.group(1).lower(), m.group(2) or ""))
    return rezultat

# ============================ MAIN ============================

def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    erori = []
    textele = {p: citeste(os.path.join(WEB2, p)) for p in PAGINI}

    # ---------- 1. Verificări pe fiecare pagină ----------
    print("== 1. Verificări pe fiecare pagină ==")
    for pagina in PAGINI:
        text = textele[pagina]
        taguri = parseaza(text)
        numar = {}
        for (n, _) in taguri:
            numar[n] = numar.get(n, 0) + 1
        e_pag = []

        if '<meta charset="UTF-8">' not in text:
            e_pag.append('lipsește <meta charset="UTF-8">')
        for t in CERUTE_PE_PAGINA:
            if numar.get(t, 0) < 1:
                e_pag.append(f"lipsește tag-ul <{t}>")

        # zero CSS/JS
        for interzis in ("<style", "<script", "<link", "style="):
            if interzis in text.lower():
                e_pag.append(f"CSS/JS interzis găsit: {interzis}")
        if re.search(r"\bon[a-z]+\s*=", text, re.I):
            e_pag.append("CSS/JS interzis găsit: handler on*=")

        # fișiere locale existente (href/src/poster/srcset/action)
        for val in REF_PATTERN.findall(text):
            cale = val.split()[0].split("#")[0]
            if not cale:
                continue
            if cale.startswith(("http://", "https://", "mailto:", "data:")):
                continue
            if not os.path.isfile(os.path.join(WEB2, cale)):
                e_pag.append(f"fișier local lipsă: {cale}")

        # meniul: nav cu legături către celelalte pagini
        m = re.search(r"<nav.*?</nav>", text, re.S)
        if not m:
            e_pag.append("lipsește blocul <nav>")
        else:
            nav_text = m.group(0)
            for alta in PAGINI:
                if alta != pagina and f'href="{alta}"' not in nav_text:
                    e_pag.append(f"meniul nu conține legătura către {alta}")

        # imbricarea corectă (parser strict)
        p = VerificatorImbricare()
        p.feed(text)
        p.close()
        for err in p.erori[:5]:
            e_pag.append(f"imbricare: {err}")
        if p.stiva:
            e_pag.append(f"imbricare: tag-uri neînchise la final: {p.stiva}")

        if e_pag:
            erori.extend(f"[{pagina}] {x}" for x in e_pag)
            print(f"  {pagina}: {len(e_pag)} probleme")
            for x in e_pag:
                print(f"    - {x}")
        else:
            print(f"  {pagina}: OK")

    # ---------- 2. Tag-uri + atribute pe tot site-ul ----------
    print("== 2. Tag-uri și atribute pe tot site-ul ==")
    toate_tagurile = []
    for pagina in PAGINI:
        toate_tagurile.extend(parseaza(textele[pagina]))
    numar_taguri = {}
    attrs_dupa_tag = {}
    for (n, at) in toate_tagurile:
        numar_taguri[n] = numar_taguri.get(n, 0) + 1
        attrs_dupa_tag.setdefault(n, []).append(at)
    for n in attrs_dupa_tag:
        attrs_dupa_tag[n] = " ".join(attrs_dupa_tag[n])

    for tag, atribute in TAGURI_CERUTE.items():
        if numar_taguri.get(tag, 0) < 1:
            erori.append(f"lipsește tag-ul <{tag}> pe tot site-ul")
            print(f"  <{tag}>: LIPSEȘTE")
            continue
        detalii = []
        for a in atribute:
            if not re.search(rf"\b{re.escape(a)}\b", attrs_dupa_tag.get(tag, ""), re.I):
                detalii.append(a)
        if detalii:
            erori.append(f"<{tag}> există, dar fără atributele: {', '.join(detalii)}")
            print(f"  <{tag}>: fără {', '.join(detalii)}")
        else:
            print(f"  <{tag}>: OK ({numar_taguri[tag]}×)")

    # colspan și rowspan
    text_combinat = "".join(textele.values())
    for atribut in ("colspan", "rowspan"):
        if not re.search(rf'\b{atribut}="\d+"', text_combinat):
            erori.append(f"lipsește atributul {atribut}")
            print(f"  {atribut}: LIPSEȘTE")
        else:
            print(f"  {atribut}: OK")

    # ---------- 3. Tipuri de input, tipuri de ol, method=get ----------
    print("== 3. Tipuri de input / ol / method =")
    tipuri_input = set(re.findall(r'<input\b[^>]*\btype="([a-z]+)"', text_combinat))
    lipsa_input = TIPURI_INPUT - tipuri_input
    if lipsa_input:
        erori.append(f"tipuri de <input> lipsă: {', '.join(sorted(lipsa_input))}")
    print(f"  tipuri input: {', '.join(sorted(tipuri_input))}")

    tipuri_ol = set(re.findall(r'<ol\b[^>]*\btype="([1aAiI])"', text_combinat))
    if TIPURI_OL - tipuri_ol:
        erori.append(f"tipuri de <ol> lipsă: {', '.join(sorted(TIPURI_OL - tipuri_ol))}")
    print(f"  tipuri ol: {', '.join(sorted(tipuri_ol))}")

    if not re.search(r'<form\b[^>]*\bmethod="get"', text_combinat):
        erori.append('nicio formular cu method="get"')
    print("  form method=get: " + ("OK" if re.search(r'<form\b[^>]*\bmethod="get"', text_combinat) else "LIPSEȘTE"))

    # list= pe un input + <datalist id=...> corespondent
    if 'list="' in text_combinat:
        m_lista = re.findall(r'list="([^"]+)"', text_combinat)
        for id_lista in m_lista:
            if f'id="{id_lista}"' not in text_combinat:
                erori.append(f"input list=\"{id_lista}\" fără <datalist id> corespondent")
        print("  input list= ↔ datalist id: OK")

    # ---------- 4. Ancore încrucișate + usemap ----------
    print("== 4. Ancore și hărți de imagini ==")
    ids_pe_pagina = {p: set(re.findall(r'id="([^"]+)"', textele[p])) for p in PAGINI}
    for pagina in PAGINI:
        for val in re.findall(r'href="([^"]+)"', textele[pagina]):
            if "#" in val and not val.startswith(("http", "mailto")):
                tinta, ancora = val.split("#", 1)
                if tinta:
                    if tinta not in textele:
                        erori.append(f"[{pagina}] ancoră spre pagină inexistentă: {val}")
                    elif ancora not in ids_pe_pagina.get(tinta, set()):
                        erori.append(f"[{pagina}] ancora #{ancora} nu există în {tinta}")
    print("  ancore încrucișate verificate")

    # usemap pe index: img usemap="#nume" ↔ map name="nume" + ≥1 area
    text_index = textele["index.html"]
    m_usemap = re.search(r'usemap="#([^"]+)"', text_index)
    if not m_usemap:
        erori.append("index.html: lipsește imaginea cu usemap")
        print("  usemap: LIPSEȘTE")
    else:
        nume_harta = m_usemap.group(1)
        if f'name="{nume_harta}"' not in text_index:
            erori.append(f'index.html: usemap="#nume_harta" fără <map name="{nume_harta}">')
            print("  usemap ↔ map: NEPOTRIVIT")
        else:
            nr_area = len(re.findall(r"<area\b", text_index))
            if nr_area < 1:
                erori.append("index.html: harta nu are <area>")
            print(f'  usemap ↔ map "{nume_harta}": OK, {nr_area} zone clicabile')

    # ---------- Rezumat ----------
    print()
    print("=" * 62)
    if not erori:
        print("TOATE VERIFICĂRILE AU TRECUT ✔")
        print("Site-ul respectă cerințele: tag-uri, atribute, link-uri, meniu,")
        print("fără CSS/JS, tag-uri închise și imbricate corect.")
    else:
        print(f"PROBLEME GĂSITE: {len(erori)}")
        for e in erori:
            print("  -", e)
        print("Site-ul NU respectă (încă) toate cerințele.")
    print("=" * 62)
    sys.exit(1 if erori else 0)


if __name__ == "__main__":
    main()
