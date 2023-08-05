import re

def js(html): return re.findall('<script>[^>]+>', html)

def search(text, html):
    to_find = lambda s: re.search(text.replace(f'<>{text.strip()[-1]}', f'([^{text.strip()[-1]}]+)'), s)
    for i in js(html):
        if to_find(i): return to_find(i).group(1)

def find(text, html):
    to_find = text.replace(f'<>{text.strip()[-1]}', f'([^{text.strip()[-1]}]+)')
    return re.findall(to_find, " ".join(js(html)).replace('\n', ' '))