#!/usr/bin/env python3
"""Decode Mongbotics_Deck.pdf to text. Writes tools/deck-sources.md.

There is no pdftotext and no poppler on this machine, and the deck has no
plain text to pull: every glyph is a Tj with a font specific code, and the
ToUnicode CMaps that translate those codes live inside the compressed
streams. So: decompress everything, rebuild the glyph maps, then walk the
content streams decoding one glyph at a time.
"""
import os, re, sys, zlib

HERE = os.path.dirname(os.path.abspath(__file__))
PDF = sys.argv[1] if len(sys.argv) > 1 else os.path.join(
    os.path.dirname(os.path.dirname(HERE)), "Mongbotics_Deck.pdf")


def streams(data):
    for m in re.finditer(rb"stream\r?\n(.*?)endstream", data, re.S):
        try:
            yield zlib.decompress(m.group(1))
        except Exception:
            continue


def glyph_map(blob):
    """code -> character, from every bfchar and bfrange block in the file."""
    cmap = {}
    for m in re.finditer(rb"beginbfchar(.*?)endbfchar", blob, re.S):
        for src, dst in re.findall(rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", m.group(1)):
            cmap[int(src, 16)] = "".join(
                chr(int(dst[i:i + 4], 16)) for i in range(0, len(dst), 4))
    for m in re.finditer(rb"beginbfrange(.*?)endbfrange", blob, re.S):
        for lo, hi, dst in re.findall(
                rb"<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>\s*<([0-9A-Fa-f]+)>", m.group(1)):
            lo, hi, dst = int(lo, 16), int(hi, 16), int(dst, 16)
            for i in range(lo, hi + 1):
                cmap[i] = chr(dst + i - lo)
    return cmap


def slide_text(raw, cmap):
    # each glyph is its own Tj. A Td advance over 60 units is a word space,
    # which is what separates words since the PDF stores none.
    parts = []
    for m in re.finditer(
            rb"(-?[\d.]+) 0 Td <([0-9A-Fa-f]+)> Tj|<([0-9A-Fa-f]+)> Tj", raw):
        adv = m.group(1)
        code = (m.group(2) or m.group(3)).decode()
        if adv and float(adv) > 60:
            parts.append(" ")
        parts.append("".join(
            cmap.get(int(code[i:i + 4], 16), "") for i in range(0, len(code), 4)))
    return re.sub(r"\s+", " ", "".join(parts)).strip()


def main():
    data = open(PDF, "rb").read()
    all_streams = list(streams(data))
    cmap = glyph_map(b"\n".join(all_streams))
    if not cmap:
        sys.exit("no glyph maps found, the PDF structure must have changed")

    out = ["# Mongbotics_Deck.pdf, decoded", "",
           "All 15 slides, verbatim. Regenerate with `python3 tools/read-deck.py`.",
           "See that script for why this is not a one liner.", "",
           "Use this as the source of truth for any claim on the site.", ""]
    n = 0
    for raw in all_streams:
        if b"Tj" not in raw and b"TJ" not in raw:
            continue
        n += 1
        text = slide_text(raw, cmap)
        if text:
            out += ["## Slide %d" % n, "", text, ""]

    dest = os.path.join(HERE, "deck-sources.md")
    open(dest, "w").write("\n".join(out))
    print("wrote", dest, "with", n, "slides")


if __name__ == "__main__":
    main()
