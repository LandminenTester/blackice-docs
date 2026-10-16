"""Shared recursive navigation model for the site, GitBook and verification."""
from pathlib import PurePosixPath

def leaves(tree):
    for label,value in tree.items():
        if isinstance(value,str):yield label,value
        else:yield from leaves(value)

def mkdocs_items(tree):
    return [{label:value if isinstance(value,str) else mkdocs_items(value)} for label,value in tree.items()]

def summary_items(tree,labels=None,german_files=False,depth=0):
    labels=labels or {}
    result=[]
    for label,value in tree.items():
        title=labels.get(label,label)
        if isinstance(value,str):
            path=PurePosixPath(value)
            if german_files:path=path.with_name(path.stem+'.de.md')
            result.append('  '*depth+f'* [{title}]({path.as_posix()})')
        else:
            result.append('  '*depth+f'* **{title}**')
            result.extend(summary_items(value,labels,german_files,depth+1))
    return result

def sibling_groups(tree,depth=0):
    """Nested sections containing only pages become horizontal page-link groups."""
    for value in tree.values():
        if isinstance(value,dict):
            if depth and all(isinstance(path,str) for path in value.values()):yield list(value.values())
            yield from sibling_groups(value,depth+1)
