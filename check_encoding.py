from pathlib import Path

for p in Path(".").rglob("*.html"):
    if ".venv" in p.parts:
        continue
    try:
        s = p.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        print(f"\n[НЕ UTF-8] {p}")
        continue

    if "РќР" in s or "Р”Р" in s or "РЎР" in s:
        print(f"\n[ПОВРЕЖДЁННЫЙ ТЕКСТ] {p}")
        for i, line in enumerate(s.splitlines(), 1):
            if any(x in line for x in ("РќР", "Р”Р", "РЎР", "РѕС‚Р", "РџСЂ")):
                print(f"{i}: {line[:240]}")
