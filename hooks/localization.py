"""Expose locale-aware UI strings and real page alternates to our custom theme."""
import json
from pathlib import Path
from mkdocs.plugins import event_priority

ROOT=Path(__file__).resolve().parents[1]

def on_env(env, config, files):
    # Static theme pages such as 404 do not receive on_page_context.
    env.globals.update(t=lambda text: text, lang='en', ui_strings={}, locale_links=[])
    return env

@event_priority(-100)
def on_page_context(context, page, config, nav):
    lang=context.get('i18n_page_locale','en')
    translations=json.loads((ROOT/'locales/ui.de.json').read_text(encoding='utf-8'))
    context['lang']=lang
    context['ui_strings']=translations if lang=='de' else {}
    context['t']=lambda value: translations.get(value,value) if lang=='de' else value
    context['locale_links']=[{'lang':locale,'name':name,'url':page.file.alternates[locale].url}
        for locale,name in [('en','English'),('de','Deutsch')] if locale in page.file.alternates]
    ancestors=[]
    parent=page.parent
    while parent:
        ancestors.append(parent)
        parent=parent.parent
    context['page_ancestors']=list(reversed(ancestors))
    # These are links between documents, not JavaScript tab panels.
    context['related_pages']=(page.parent.children if page.parent and page.parent.parent
        and all(not getattr(item,'children',None) for item in page.parent.children) else [])
    return context
