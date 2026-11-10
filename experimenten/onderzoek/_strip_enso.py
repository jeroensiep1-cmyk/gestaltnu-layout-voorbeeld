from pathlib import Path

f = next(Path(__file__).parent.glob("bioscoop*.svg"))
t = f.read_text(encoding="utf-8")
marker = 'stroke="#0f6e6e" stroke-width="34"'
idx = t.find(marker)
if idx < 0:
    raise SystemExit("enso stroke not found")
start = t.rfind("<path", 0, idx)
c = t.rfind("<!--", 0, start)
if c >= 0 and start - c < 120:
    start = c
end = t.find("<!-- zachte zaal")
if end < 0:
    raise SystemExit("zaal marker not found")
t2 = t[:start] + "  <!-- geen ensō-cirkel -->\n\n  " + t[end:]
f.write_text(t2, encoding="utf-8")
print("ok", f.name, "removed", end - start, "chars")
