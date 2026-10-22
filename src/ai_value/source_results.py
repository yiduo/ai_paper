r"""Locate labelled TeX results without losing nested citation titles.

This is a bounded source index, not a TeX interpreter or proof checker.
Labels may follow the title or occur at statement level within the result.
Nested equation or other environment labels do not identify the result.
Cleveref's optional label type is permitted, e.g. ``\label[lemma]{key}``.
"""

from __future__ import annotations

import re


def named_results(text: str) -> list[dict]:
    # Ignore comments, retaining offsets for source locators.
    visible = re.sub(r"(?<!\\)%[^\n]*", lambda m: " " * len(m[0]), text)
    results = []
    for match in re.finditer(r"\\begin\{(theorem|lemma|proposition|corollary|verification)\}", visible):
        pos = match.end()
        while pos < len(visible) and visible[pos].isspace():
            pos += 1
        title = None
        if pos < len(visible) and visible[pos] == "[":
            start, depth = pos + 1, 1
            pos += 1
            while pos < len(visible) and depth:
                if visible[pos] == "\\":
                    # Escaped brackets do not close an optional argument.
                    pos += 2
                    continue
                if visible[pos] == "[":
                    depth += 1
                elif visible[pos] == "]":
                    depth -= 1
                pos += 1
            if depth:
                raise ValueError("Unclosed result title at source offset " + str(match.start()))
            title = text[start:pos-1]
        end = visible.find(r"\end{" + match[1] + "}", pos)
        if end < 0:
            raise ValueError("Unclosed result at source offset " + str(match.start()))
        label_pattern = r"\\label(?:\[[^\]\n]*\])?\{([^}]+)\}"
        immediate = re.match(r"\s*" + label_pattern, visible[pos:end])
        labels = []
        environments = []
        braces = 0
        # Only outer statement labels count. In particular an unlabelled
        # result containing labelled equations must stay unlabelled.
        tokens = re.finditer(r"\\(begin|end)\{([^}]+)\}|" + label_pattern
                             + r"|\\[{}]|[{}]", visible[pos:end])
        for token in tokens:
            if token[1] == "begin":
                environments.append(token[2])
            elif token[1] == "end":
                if environments and environments[-1] == token[2]:
                    environments.pop()
            elif token[3] is not None:
                if not environments and braces == 0:
                    labels.append(token[3])
            elif token[0] == "{":
                braces += 1
            elif token[0] == "}":
                braces -= 1
        if not labels:
            continue
        body_start = pos + immediate.end() if immediate is not None else pos
        results.append({"kind": match[1], "label": labels[0], "title_tex": title,
                        "label_aliases": list(dict.fromkeys(labels[1:])),
                        "start": match.start(), "statement_start": body_start,
                        "statement_end": end})
    return results
