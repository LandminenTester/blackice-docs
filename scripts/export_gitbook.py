"""Export ordinary Markdown trees for separate English/German GitBook spaces."""
from pathlib import Path
import json, re, shutil
from navigation_model import summary_items

ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'content'
BASE=ROOT/'.gitbook-export'
navigation=json.loads((ROOT/'navigation.json').read_text(encoding='utf-8'))
labels=json.loads((ROOT/'locales/nav.de.json').read_text(encoding='utf-8'))
for locale in ('en','de'):
    dest=BASE/locale
    # Never remove any path except the named export child inside this repository.
    if dest.resolve().parent!=BASE.resolve() or BASE.resolve().parent!=ROOT.resolve():
        raise SystemExit('Unsafe export destination')
    if dest.exists():shutil.rmtree(dest)
    dest.mkdir(parents=True)
    for source in CONTENT.rglob('*'):
        if not source.is_file() or source.name in {'SUMMARY.md','SUMMARY.de.md','CNAME'}:continue
        if source.name.endswith('.de.md'):continue
        rel=source.relative_to(CONTENT)
        target=dest/rel;target.parent.mkdir(parents=True,exist_ok=True)
        selected=source
        if locale=='de' and source.suffix=='.md':
            translated=source.with_name(source.stem+'.de.md')
            if translated.exists():selected=translated
        if selected.suffix=='.md':
            text=selected.read_text(encoding='utf-8')
            text=re.sub(r'\.de\.md(?=[)#])','.md',text)
            target.write_text(text,encoding='utf-8')
        else:shutil.copyfile(selected,target)
    summary=['# Summary' if locale=='en' else '# Inhalt','']
    for group,pages in navigation.items():
        summary+=['## '+(labels.get(group,group) if locale=='de' else group),'']
        summary += summary_items(pages,labels if locale=='de' else {})
        summary+=['']
    (dest/'SUMMARY.md').write_text('\n'.join(summary),encoding='utf-8')
    (dest/'.gitbook.yaml').write_text('root: ./\nstructure:\n  readme: README.md\n  summary: SUMMARY.md\n',encoding='utf-8')
    print(f'Exported {locale} to {dest}')
