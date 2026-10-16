"""Separate upstream bilingual panel guides; apply reviewed locale files last.

The original source documents stay untouched. English is the unsuffixed source;
German is *.de.md. Hand-maintained translations in translations/de always win.
"""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / 'content'

def localize():
    for p in (CONTENT / 'webpanel').rglob('*.md'):
        if p.name.endswith('.de.md'): continue
        text = p.read_text(encoding='utf-8')
        markers = list(re.finditer(r'^## (English|Deutsch)\s*$', text, re.M))
        en, de = None, None
        title = text.splitlines()[0]
        if markers:
            chunks = {}
            for i, match in enumerate(markers):
                chunks[match[1]] = text[match.end():markers[i+1].start() if i+1<len(markers) else len(text)].strip()
            prefix = text[len(title):markers[0].start()].strip()
            en = chunks.get('English', prefix)
            de = chunks.get('Deutsch', '')
            # Supplementary upstream sections sometimes follow the German block.
            # Explicit EN:/DE: paragraph markers are split without language guessing.
            tail = re.search(r'^## (?:Direct terminal|Interactive terminals|Additional keys|Docker recovery|Bundle workflow permissions)', de, re.M)
            if tail:
                extra = de[tail.start():]
                de = de[:tail.start()].rstrip()
                for block in re.split(r'\n\s*\n', extra):
                    if block.startswith('## '):
                        parts=block.split(' / ',1)
                        en += '\n\n'+parts[0]
                        de += '\n\n'+('## '+parts[1] if len(parts)>1 else parts[0])
                    elif block.startswith(('EN: ', 'English: ')):
                        en += '\n\n'+block.split(': ',1)[1]
                    elif block.startswith(('DE: ', 'Deutsch: ')):
                        de += '\n\n'+block.split(': ',1)[1]
                    else:
                        en += '\n\n'+block
            titles=title.split(' / ',1)
            p.write_text(titles[0]+'\n\n'+en+'\n',encoding='utf-8')
            target=p.with_name(p.stem+'.de.md')
            # Preserve the dedicated German README already supplied by upstream.
            if p.name != 'README.md':
                target.write_text(('# '+titles[1] if len(titles)>1 else title)+'\n\n'+de+'\n',encoding='utf-8')
        elif '\n# Bundle-Tools (Experimentell)' in text:
            en,de=text.split('\n# Bundle-Tools (Experimentell)',1)
            p.write_text(en.rstrip()+'\n',encoding='utf-8')
            p.with_name(p.stem+'.de.md').write_text('# Bundle-Tools (Experimentell)'+de,encoding='utf-8')
    # The old dump has been replaced by the structured, compiled walkthrough.
    old=CONTENT/'lt-database/docs/RECIPES.md'
    if old.exists(): old.unlink()
    old=CONTENT/'lt-database/examples/consumer/Recipes.cs'
    if old.exists(): old.unlink()
    for p in (ROOT/'editorial/en').rglob('*.md'):
        dest=CONTENT/p.relative_to(ROOT/'editorial/en')
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(p.read_text(encoding='utf-8'),encoding='utf-8')
    for p in (ROOT/'translations/de').rglob('*.md'):
        rel=p.relative_to(ROOT/'translations/de')
        dest=CONTENT/rel.parent/(rel.stem+'.de.md')
        dest.parent.mkdir(parents=True,exist_ok=True)
        dest.write_text(p.read_text(encoding='utf-8'),encoding='utf-8')
    # Remove inline language links: the page-aware header switcher owns this.
    for p in (CONTENT/'webpanel').glob('README*.md'):
        s=p.read_text(encoding='utf-8')
        s=re.sub(r'\[(?:Deutsch|English)\]\(README(?:\.de)?\.md\)\s*[·|]?\s*','',s)
        p.write_text(s,encoding='utf-8')

if __name__=='__main__': localize()
