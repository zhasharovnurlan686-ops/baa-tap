from pathlib import Path
from datetime import datetime
import re
import shutil

p = Path("templates/marketplace/home.html")
text = p.read_text(encoding="utf-8")

backup = p.with_name(
    p.name + "." + datetime.now().strftime("%Y%m%d_%H%M%S") + ".bak"
)
shutil.copy2(p, backup)

pattern = re.compile(
    r"Р[А-Яа-яЁё]|С[А-Яа-яЁё]|в[†њ]|ТЇ|У©"
)

def fix_word(word):
    for _ in range(3):
        if not pattern.search(word):
            break
        try:
            fixed = word.encode("cp1251").decode("utf-8")
        except (UnicodeEncodeError, UnicodeDecodeError):
            break
        if fixed == word:
            break
        word = fixed
    return word

parts = re.split(r"(<[^>]*>|{%.*?%}|{{.*?}}|{#.*?#})", text, flags=re.S)

for i in range(0, len(parts), 2):
    parts[i] = re.sub(r"\S+", lambda m: fix_word(m.group()), parts[i])

result = "".join(parts)
p.write_text(result, encoding="utf-8")

print("Готово. Исправлен файл:", p)
print("Резервная копия:", backup)
print("Проверьте главную страницу в браузере.")
