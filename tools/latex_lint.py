r"""Static LaTeX sanity checks (no TeX engine is installed on the build machine): brace/environment balance, \input targets,
\ref vs \label, \cite vs references.bib, undefined result macros, figure files.
Usage: python tools/latex_lint.py [main_journal.tex main_conference.tex]"""
import pathlib
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1] / "papers"
bib = (ROOT / "references.bib").read_text(encoding="utf-8")
bibkeys = set(re.findall(r"@\w+\{([^,\s]+),", bib))
macros_def = set(re.findall(r"\\newcommand\{\\(\w+)\}", (ROOT / "results_macros.tex").read_text(encoding="utf-8")))
BEGIN, END = "\\begin{", "\\end{"
ok_all = True


def load(f, acc):
    p = ROOT / f
    if not p.exists():
        acc["errs"].append(f"missing input {f}")
        return
    t = re.sub(r"(?<!\\)%.*", "", p.read_text(encoding="utf-8"))
    acc["text"] += "\n" + t
    for m in re.finditer(r"\\input\{([^}]+)\}", t):
        g = m.group(1)
        load(g if g.endswith(".tex") else g + ".tex", acc)


for main in sys.argv[1:] or ["main_journal.tex", "main_conference.tex"]:
    acc = {"text": "", "errs": []}
    load(main, acc)
    text, errs = acc["text"], acc["errs"]
    a, b = len(re.findall(r"(?<!\\)\{", text)), len(re.findall(r"(?<!\\)\}", text))
    if a != b:
        errs.append(f"brace imbalance {a} vs {b}")
    for env in set(re.findall(r"\\begin\{(\w+\*?)\}", text)):
        if text.count(BEGIN + env + "}") != text.count(END + env + "}"):
            errs.append(f"env mismatch {env}")
    labels = set(re.findall(r"\\label\{([^}]+)\}", text))
    for r in set(re.findall(r"\\(?:ref|eqref)\{([^}]+)\}", text)):
        if r not in labels:
            errs.append(f"undefined ref {r}")
    cites = set(k.strip() for c in re.findall(r"\\cite\{([^}]+)\}", text) for k in c.split(","))
    for c in cites:
        if c not in bibkeys:
            errs.append(f"missing bib key {c}")
    for m in set(re.findall(r"\\((?:N[A-Z]|Res|Leg|Agr|ATest|ATrain|AYear|Eng|Cold|Hist|Err|Nov|FS|Ann|Cov|Residual)[A-Za-z]*)", text)):
        if m not in macros_def:
            errs.append(f"undefined macro \\{m}")
    for g in re.findall(r"\\includegraphics(?:\[[^\]]*\])?\{([^}]+)\}", text):
        if not (ROOT / g).exists():
            errs.append(f"missing figure {g}")
    print(main, "| labels", len(labels), "| cites", len(cites), "|", "OK" if not errs else "PROBLEMS")
    for e in errs:
        print("   ", e)
    print("    bib entries not cited in this version:", len([k for k in bibkeys if k not in cites]))
    ok_all &= not errs
sys.exit(0 if ok_all else 1)
