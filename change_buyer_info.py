from pathlib import Path

p = Path("templates/marketplace/request_detail.html")
s = p.read_text(encoding="utf-8")

backup = Path(str(p) + ".before_buyer_info")
backup.write_text(s, encoding="utf-8")

old = """{% if user == item.buyer %}Р’Р°С€Р° Р·Р°СЏРІРєР°{% else %}Р•СЃС‚СЊ РїРѕРґС…РѕРґСЏС‰РµРµ РїСЂРµРґР»РѕР¶РµРЅРёРµ?{% endif %}"""

new = """{% if user == item.buyer %}{{ item.buyer.company_name|default:item.buyer.get_full_name|default:item.buyer.username }}{% else %}Р•СЃС‚СЊ РїРѕРґС…РѕРґСЏС‰РµРµ РїСЂРµРґР»РѕР¶РµРЅРёРµ?{% endif %}"""

if old not in s:
    print("Не найден точный заголовок. Файл не изменён.")
    print("Найди в шаблоне фразу: Р’Р°С€Р° Р·Р°СЏРІРєР°")
    raise SystemExit(1)

s = s.replace(old, new, 1)

old_desc = """{% if user == item.buyer %}РџРѕРґРµР»РёС‚РµСЃСЊ СЃСЃС‹Р»РєРѕР№ РЅР° Р·Р°РїСЂРѕСЃ СЃ РїРѕСЃС‚Р°РІС‰РёРєР°РјРё, С‡С‚РѕР±С‹ РїРѕР»СѓС‡РёС‚СЊ Р±РѕР»СЊС€Рµ РѕС‚РІРµС‚РѕРІ.{% else %}РћС‚РїСЂР°РІСЊС‚Рµ С†РµРЅСѓ Рё СЃСЂРѕРє РІС‹РїРѕР»РЅРµРЅРёСЏ. РџРѕРєСѓРїР°С‚РµР»СЊ СѓРІРёРґРёС‚ РІР°С€Рµ РїСЂРµРґР»РѕР¶РµРЅРёРµ РІ Р»РёС‡РЅРѕРј РєР°Р±РёРЅРµС‚Рµ.{% endif %}"""

new_desc = """{% if user == item.buyer %}{{ item.buyer.city|default:"Бишкек" }}{% else %}РћС‚РїСЂР°РІСЊС‚Рµ С†РµРЅСѓ Рё СЃСЂРѕРє РІС‹РїРѕР»РЅРµРЅРёСЏ. РџРѕРєСѓРїР°С‚РµР»СЊ СѓРІРёРґРёС‚ РІР°С€Рµ РїСЂРµРґР»РѕР¶РµРЅРёРµ РІ Р»РёС‡РЅРѕРј РєР°Р±РёРЅРµС‚Рµ.{% endif %}"""

if old_desc in s:
    s = s.replace(old_desc, new_desc, 1)
else:
    print("Предупреждение: описание не совпало, заголовок изменён.")

p.write_text(s, encoding="utf-8")
print("Изменения сохранены:", p)
