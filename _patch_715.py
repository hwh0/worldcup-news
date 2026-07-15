#!/usr/bin/env python3
from pathlib import Path

path = Path("index.html")
text = path.read_text(encoding="utf-8")

text = text.replace("const APP_VERSION = 'v34';", "const APP_VERSION = 'v35';")
text = text.replace("const CACHE_KEY = 'wc_news_cache_v34';", "const CACHE_KEY = 'wc_news_cache_v35';")
text = text.replace("const NEWS_UPDATED = '2026-07-14';", "const NEWS_UPDATED = '2026-07-15';")
text = text.replace(
    "八強已全部完賽，以下為四強對戰表。完賽後自動填入晉級隊伍。",
    "四強首戰西班牙已晉級決賽，英格蘭阿根廷明日開踢。完賽後自動填入晉級隊伍。",
)

# 補上四強賽果（API 可能缺 Oyarzabal 十二碼）
needle = "        away_scorers: '{\"Dan Ndoye 67\\'\"}',\n    },\n};"
replacement = """        away_scorers: '{"Dan Ndoye 67\\'"}',
    },
    '101': {
        home_score: '0',
        away_score: '2',
        finished: 'TRUE',
        time_elapsed: 'finished',
        home_scorers: 'null',
        away_scorers: '{"Mikel Oyarzabal 22\\' (PEN)","Pedro Porro 58\\'"}',
    },
};"""
if needle not in text:
    raise SystemExit("KNOWN_RESULTS block not found")
text = text.replace(needle, replacement)

start = text.index("const TODAY_TOP10_NEWS = [")
end = text.index("/** 換版時清除舊 localStorage")
if end == -1:
    end = text.index("const REACTION_TONE = {")
NEW_DATA = open(Path(__file__).parent / "_news_715_data.js", encoding="utf-8").read()
text = text[:start] + NEW_DATA + "\n\n" + text[end:]

path.write_text(text, encoding="utf-8")
print("Patched 7/15 西班牙晉級決賽 v35 OK")