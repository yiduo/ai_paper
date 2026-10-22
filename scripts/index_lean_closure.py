#!/usr/bin/env python3
"""Static local import/declaration index. Never claims a Lean or Comparator build."""

import argparse
import gzip
import hashlib
import json
from pathlib import Path
import re


def code_only(text):
    result, i, depth, quoted = [], 0, 0, False
    while i < len(text):
        if depth:
            if text.startswith('/-',i):
                depth += 1
                i += 2
            elif text.startswith('-/',i):
                depth -= 1
                i += 2
            else:
                result.append('\n' if text[i]=='\n' else ' ')
                i += 1
        elif quoted:
            if text[i]=='\\':
                result.extend('  ')
                i += 2
            elif text[i]=='"':
                quoted = False
                result.append(' ')
                i += 1
            else:
                result.append('\n' if text[i]=='\n' else ' ')
                i += 1
        elif text.startswith('/-',i):
            depth = 1
            result.extend('  ')
            i += 2
        elif text.startswith('--',i):
            end = text.find('\n',i)
            if end < 0:
                end = len(text)
            result.extend(' '*(end-i))
            i = end
        elif text[i]=='"':
            quoted = True
            result.append(' ')
            i += 1
        else:
            result.append(text[i])
            i += 1
    return ''.join(result)


def module_imports(code):
    """Read module names, preserving Lean visibility/access modifiers separately.

    This remains a lexical index, not Lean syntax elaboration. In particular,
    `all` in `import all M` is an access modifier, not a module to resolve.
    """
    records = []
    pattern = r"^[ \t]*((?:(?:public|meta)[ \t]+)*)import[ \t]+(?:(all)[ \t]+)?([^\n]+)"
    for match in re.finditer(pattern, code, re.M):
        modifiers = match[1].split() + (["all"] if match[2] else [])
        for name in match[3].split():
            records.append({"module": name, "modifiers": modifiers,
                            "line": code[:match.start()].count("\n")+1})
    return records


def index(root, module):
    todo, seen, records, external = [module], set(), [], set()
    while todo:
        name = todo.pop()
        if name in seen:
            continue
        seen.add(name)
        path = root/'math/lean'/Path(*name.split('.')).with_suffix('.lean')
        if not path.exists():
            external.add(name)
            continue
        text = path.read_text()
        code = code_only(text)
        import_statements = module_imports(code)
        imports = [item['module'] for item in import_statements]
        todo.extend(imports)
        declarations = []
        for match in re.finditer(r'^[ \t]*(?:(?:private|protected|noncomputable)[ \t]+)*(theorem|lemma|def|abbrev|structure|axiom)[ \t]+([^\s:(]+)',code,re.M):
            declarations.append({'kind':match[1],'local_name':match[2],
                                 'line':code[:match.start()].count('\n')+1})
        records.append({'module':name,'path':str(path.relative_to(root)),
                        'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),
                        'imports':imports,'import_statements':import_statements,'declarations':declarations,
                        'placeholder_tokens':[{'token':m[0],'line':code[:m.start()].count('\n')+1}
                                              for m in re.finditer(r'\b(?:sorry|admit)\b',code)]})
    return {'root_module':module,'method':'static import closure and lexical declaration/placeholder index; comments and strings ignored',
            'local_files':sorted(records,key=lambda r:r['module']),
            'external_modules_not_present':sorted(external),'local_build':'not_run','comparator':'not_run',
            'human_specification_review':'missing',
            'limitations':'Indexing does not read every proof mathematically, resolve Lean elaboration, prove imported axioms admissible, or establish natural-language specification agreement.'}


if __name__=='__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--module',required=True)
    parser.add_argument('--output',type=Path,required=True)
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = index(root,args.module)
    packed = gzip.compress((json.dumps(result,ensure_ascii=False,indent=2)+'\n').encode(),mtime=0)
    args.output.parent.mkdir(parents=True,exist_ok=True)
    args.output.write_bytes(packed)
    print(json.dumps({'local_files':len(result['local_files']),
                      'declarations':sum(len(r['declarations']) for r in result['local_files']),
                      'placeholder_tokens':sum(len(r['placeholder_tokens']) for r in result['local_files']),
                      'local_axiom_declarations':sum(d['kind']=='axiom' for r in result['local_files'] for d in r['declarations']),
                      'external_modules_not_present':result['external_modules_not_present'],
                      'compressed_bytes':len(packed),'local_build':'not_run'},indent=2))
