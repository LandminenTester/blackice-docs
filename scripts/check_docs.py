"""Check locale coverage, rendered links and compiled example parity."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json, posixpath, re
from navigation_model import leaves, sibling_groups

ROOT=Path(__file__).resolve().parents[1]
CONTENT=ROOT/'content'
SITE=ROOT/'site'

class Page(HTMLParser):
    def __init__(self,text):
        super().__init__(convert_charrefs=True)
        self.links=[];self.ids=set();self.lang=None;self.locale_links={};self.in_switch=False
        self.in_tabs=False;self.tabs=[]
        self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.add(a['id'])
        if tag=='html':self.lang=a.get('lang')
        for attr in ('href','src'):
            if attr in a:self.links.append(a[attr])
        if tag=='nav' and a.get('class')=='language-switch':self.in_switch=True
        if self.in_switch and tag=='a':self.locale_links[a.get('lang')]=a.get('href')
        if tag=='nav' and a.get('class')=='page-tabs':self.in_tabs=True
        if self.in_tabs and tag=='a':self.tabs.append(a)
    def handle_endtag(self,tag):
        if tag=='nav':self.in_switch=False;self.in_tabs=False

def route(name):
    return re.sub(r'(?:README|index)\.md$','',name).replace('.md','/')

def check():
    errors=[]
    nav=json.loads((ROOT/'navigation.json').read_text(encoding='utf-8'))
    names=[path for label,path in leaves(nav)]
    tab_groups={path:group for group in sibling_groups(nav) for path in group}
    if len(names)!=len(set(names)):errors.append('A document appears more than once in navigation')
    pages={p.relative_to(SITE).as_posix():Page(p.read_text(encoding='utf-8')) for p in SITE.rglob('*.html')}
    for name in names:
        p=CONTENT/name;de=p.with_name(p.stem+'.de.md')
        if not de.is_file():errors.append('Missing German page: '+name)
        for file in (p,de):
            if file.exists() and re.search(r'^#{1,3} (English|Deutsch)\s*$',file.read_text(encoding='utf-8'),re.M):
                errors.append('Mixed-language section: '+str(file))
        for locale in ('en','de'):
            prefix='' if locale=='en' else 'de/'
            target=prefix+route(name)+'index.html'
            page=pages.get(target)
            if not page: errors.append('Missing output: '+target);continue
            if page.lang!=locale:errors.append('Wrong HTML language: '+target)
            if name in tab_groups:
                expected_tabs={'/'+prefix+route(path) for path in tab_groups[name]}
                actual_tabs={posixpath.normpath(posixpath.join('/'+posixpath.dirname(target),a['href']))+'/' for a in page.tabs}
                if actual_tabs!=expected_tabs:errors.append('Incorrect related-page tabs: '+target)
                if sum(a.get('aria-current')=='page' for a in page.tabs)!=1:errors.append('Expected one active page tab: '+target)
            for other in ('en','de'):
                href=page.locale_links.get(other)
                expected=('/de/' if other=='de' else '/')+route(name)
                actual=posixpath.normpath(posixpath.join('/'+posixpath.dirname(target),href or ''))+'/'
                if actual=='//':actual='/'
                if actual!=expected:errors.append(f'Wrong {other} switch: {target}: {actual}, expected {expected}')
            if locale=='de' and 'class="locale-notice"' in (SITE/target).read_text(encoding='utf-8'):
                errors.append('Unexpected English fallback: '+target)
    for name,page in pages.items():
        if name=='404.html':continue
        for href in page.links:
            parsed=urlsplit(href)
            if parsed.scheme or parsed.netloc or not parsed.path and not parsed.fragment:continue
            relative=unquote(parsed.path)
            target=posixpath.normpath(posixpath.join(posixpath.dirname(name),relative)) if not relative.startswith('/') else relative.lstrip('/')
            if not relative:target=name
            resolved=SITE/target
            if resolved.is_dir():target=target.rstrip('/')+'/index.html';resolved=SITE/target
            if not resolved.is_file():errors.append(f'Broken link: {name} → {href}');continue
            if parsed.fragment and target in pages and unquote(parsed.fragment) not in pages[target].ids:
                errors.append(f'Broken anchor: {name} → {href}')
    source=(CONTENT/'lt-database/examples/consumer/PlayerPreferences.cs').read_text(encoding='utf-8').strip()
    for name in ('lt-database/docs/EXAMPLES.md','lt-database/docs/EXAMPLES.de.md'):
        blocks=re.findall(r'```csharp\n(.*?)\n```',(CONTENT/name).read_text(encoding='utf-8'),re.S)
        if source not in [b.strip() for b in blocks]:errors.append('Compiled source differs: '+name)
    index=json.loads((SITE/'search/search_index.json').read_text(encoding='utf-8'))['docs']
    for locale,prefix in [('en',''),('de','de/')]:
        url=prefix+'webpanel/docs/users/'
        if not any(d['location']==url for d in index):errors.append('Search page missing: '+url)
    if errors:raise SystemExit('\n'.join(errors))
    print(f'Checked {len(names)*2} localized guides, {len(pages)} HTML files, local links, locale switches and example parity.')

if __name__=='__main__':check()
