# -*- coding: utf-8 -*-
"""Extract historical news from git and build NEWS_ARCHIVE block."""
import re
import subprocess
from pathlib import Path

ROOT = Path(r'D:\grok')
INDEX = ROOT / 'index.html'


def git_show(commit: str) -> str:
    return subprocess.check_output(
        ['git', 'show', f'{commit}:index.html'],
        cwd=ROOT,
        text=True,
        errors='replace',
    )


def extract_block(content: str, name: str) -> str | None:
    marker = f'const {name} = ['
    start = content.find(marker)
    if start < 0:
        return None
    i = start + len(marker) - 1
    depth = 0
    while i < len(content):
        ch = content[i]
        if ch == '[':
            depth += 1
        elif ch == ']':
            depth -= 1
            if depth == 0:
                end = content.find(';', i)
                if end < 0:
                    return None
                return content[start:end + 1]
        i += 1
    return None


def parse_title(block: str) -> str:
    m = re.search(r"title:\s*'([^']+)'", block)
    return m.group(1) if m else ''


def main():
    commits = subprocess.check_output(
        ['git', 'log', '--format=%H', '-50'],
        cwd=ROOT,
        text=True,
    ).strip().split('\n')

    archives: dict[str, dict] = {}
    for h in commits:
        try:
            content = git_show(h)
        except subprocess.CalledProcessError:
            continue
        m = re.search(r"const NEWS_UPDATED = '([^']+)'", content)
        if not m:
            continue
        date = m.group(1)
        if date in archives:
            continue
        today = extract_block(content, 'TODAY_TOP10_NEWS')
        idle = extract_block(content, 'IDLE_TEAM_NEWS')
        trending = extract_block(content, 'X_TRENDING_TOP20')
        if not (today and idle and trending):
            continue
        headline = parse_title(today)
        def strip_array(block: str, prefix: str) -> str:
            return block.replace(f'const {prefix} = ', '').rstrip().rstrip(';')

        archives[date] = {
            'commit': h[:8],
            'headline': headline,
            'today': strip_array(today, 'TODAY_TOP10_NEWS'),
            'idle': strip_array(idle, 'IDLE_TEAM_NEWS'),
            'trending': strip_array(trending, 'X_TRENDING_TOP20'),
        }
        print(f'{date} <- {h[:8]} | {headline[:40]}')

    dates = sorted(archives.keys(), reverse=True)
    lines = ['/** 歷史新聞索引（依日期回溯瀏覽）— 掛載至 window 供主程式讀取 */', 'window.NEWS_ARCHIVE = {']
    for d in dates:
        a = archives[d]
        lines.append(f"    '{d}': {{")
        lines.append(f"        headline: {json_str(a['headline'])},")
        lines.append(f"        today: {a['today']},")
        lines.append(f"        idle: {a['idle']},")
        lines.append(f"        trending: {a['trending']},")
        lines.append('    },')
    lines.append('};')
    lines.append('')
    lines.append('const NEWS_ARCHIVE_DATES = Object.keys(NEWS_ARCHIVE).sort().reverse();')

    archive_text = '\n'.join(lines)
    Path(ROOT / '_news_archive.js.txt').write_text(archive_text, encoding='utf-8')
    print(f'\nBuilt {len(dates)} dates -> _news_archive.js.txt ({len(archive_text)} chars)')


def json_str(s: str) -> str:
    return "'" + s.replace("\\", "\\\\").replace("'", "\\'") + "'"


if __name__ == '__main__':
    main()