"""Figure 1: GovAllocXAI architecture as a clean sequential diagram (straight arrows only, no crossings).

Row 1 (pipeline):  Official sources -> Data layer -> Prediction layer -> Allocation engine
Row 2 (use):       Validation -> Explainability -> Human analyst, with vertical links from rows above.
"""
import pathlib
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = pathlib.Path(__file__).resolve().parents[1]
OUT = ROOT / "papers/figures"; OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({"font.family": "DejaVu Sans"})
fig, ax = plt.subplots(figsize=(8.4, 3.9))
ax.set_xlim(0, 100); ax.set_ylim(0, 50); ax.axis("off")
C = {"data": "#DCEBF7", "prep": "#E8F3E1", "model": "#FFF2CC", "alloc": "#FCE4D6", "xai": "#EADCF4", "val": "#E3EEF9", "human": "#F8D7DA", "edge": "#34495E"}
W, H = 21.5, 17
XS = [1.5, 26.5, 51.5, 76.5]           # column left edges, gap 3.5
Y1, Y2 = 29.5, 3.5


def box(x, y, title, lines, color, ls="-"):
    ax.add_patch(FancyBboxPatch((x, y), W, H, boxstyle="round,pad=0.2,rounding_size=1.0", fc=color, ec=C["edge"], lw=1.0, linestyle=ls))
    ax.text(x + W / 2, y + H - 1.6, title, ha="center", va="top", weight="bold", fontsize=7.8)
    ax.text(x + W / 2, y + H - 5.6, "\n".join(lines), ha="center", va="top", fontsize=6.6, linespacing=1.45)


def arrow(x1, y1, x2, y2, label=None, lx=0, ly=0, ls="-"):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle="-|>", mutation_scale=10, lw=1.2, color=C["edge"], shrinkA=0, shrinkB=0, linestyle=ls))
    if label:
        ax.text((x1 + x2) / 2 + lx, (y1 + y2) / 2 + ly, label, ha="center", va="center", fontsize=6.4, style="italic", color=C["edge"])


box(XS[0], Y1, "1  Official sources", ["World Bank WDI, WGI", "Eurostat COFOG", "OECD COFOG", "IMF GFS COFOG"], C["data"])
box(XS[1], Y1, "2  Data layer", ["217 economies, 2000-24", "Targets never imputed", "Flagged imputation", "Original dataset kept"], C["prep"])
box(XS[2], Y1, "3  Prediction layer", ["Persistence, peer mean", "Boosted trees, ridge", "Delta learner (history)", "Cold-start learner, stack"], C["model"])
box(XS[3], Y1, "4  Allocation engine", ["Sum-to-100 projection", "Optional policy bounds", "Exact solver + SLSQP", "Optional budget in US$"], C["alloc"])
box(XS[1], Y2, "5  Validation", ["Temporal split (COVID)", "Leave-country-out", "Cluster-bootstrap CIs", "Holm correction"], C["val"])
box(XS[2], Y2, "6  Explainability", ["TreeSHAP and LIME", "Agreement, stability", "Deletion faithfulness", "Synthetic ground truth"], C["xai"])
box(XS[3], Y2, "7  Human analyst", ["Reads reference split", "Inspects explanations", "Decides; override", "Never automatic"], C["human"])
box(XS[0], Y2, "Scope of claims", ["Descriptive reference", "Evidence only", "No causal claim", "No forecast claim"], "#F2F2F2", ls="--")
ym = Y1 + H / 2
for i in range(3):
    arrow(XS[i] + W + 0.3, ym, XS[i + 1] - 0.3, ym)
arrow(XS[2] + W / 2, Y1 - 0.3, XS[2] + W / 2, Y2 + H + 0.3, "inputs", lx=4.2)
arrow(XS[3] + W / 2, Y1 - 0.3, XS[3] + W / 2, Y2 + H + 0.3, "reference split", lx=6.2)
arrow(XS[2] + W + 0.3, Y2 + H / 2, XS[3] - 0.3, Y2 + H / 2)
arrow(XS[1] + W + 0.3, Y2 + H / 2, XS[2] - 0.3, Y2 + H / 2)
arrow(XS[0] + W + 0.3, Y2 + H / 2, XS[1] - 0.3, Y2 + H / 2, ls="--")
fig.savefig(OUT / "fig1_architecture.pdf", bbox_inches="tight"); fig.savefig(OUT / "fig1_architecture.png", dpi=300, bbox_inches="tight")
print("ok")
