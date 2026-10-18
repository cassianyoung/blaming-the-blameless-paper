import os
DATA = os.environ.get("FIGURE_DATA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")) + "/"
OUT = os.environ.get("FIGURE_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")) + "/"
import csv, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from decimal import Decimal, ROUND_HALF_UP
def hu(x, nd, sign=False, pct=False):
    """Round half up, as the text does (2.15 -> 2.2), on the value's shortest decimal form."""
    d = Decimal(repr(float(x))) * (100 if pct else 1)
    q = d.quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)
    return (f"{q:+f}" if sign else f"{q:f}") + ("%" if pct else "")
plt.rcParams["font.family"]="DejaVu Sans"
R=list(csv.DictReader([l for l in open(DATA+"frame_by_scenario.csv",encoding="utf-8-sig") if not l.startswith("#")]))
fam=["mistral","gemma27","llama31","falcon3","olmo2","qwen3","gemma9","yi34b"]
nm={"llama31":"Llama 3.1 8B","qwen3":"Qwen3 8B","mistral":"Mistral 7B","olmo2":"OLMo 2 7B","falcon3":"Falcon3 7B",
    "gemma9":"Gemma 2 9B","gemma27":"Gemma 2 27B","yi34b":"Yi 1.5 34B"}
scen=[("bicycle216","Bicycle"),("ladder","Ladder"),("prawns_home","Prawns, home"),
      ("prawns_restaurant","Prawns, restaurant"),("scaffolding","Scaffolding"),("cheque","Cheque")]
D={(r["family"],r["scenario"]):r for r in R}
# THE CHAT GATE IS READ FROM THE EXPORT, never recomputed here. If a C - N condition is
# adopted (records/RULE_CHAT_GATE_CN_20261018.md), set FIG8_CN_MIN to its value and the
# figure refuses unless every chat reading it draws as passing clears it, so a stale export
# cannot be drawn under the new rule (review of v0.7, item 11).
_cn=os.environ.get("FIG8_CN_MIN")
if _cn:
    bad=[(r["family"],r["scenario"],round(float(r["chat_C"])-float(r["chat_N"]),2)) for r in R
         if r["chat_gate"]=="PASSED" and float(r["chat_C"])-float(r["chat_N"])<float(_cn)]
    assert not bad, f"export passes chat readings below C - N {_cn}: {bad}"
ws_c="#2C5D8F"; ch_c="#C0392B"; grey="#555555"
XL,XR=-0.15,1.15
fig,axes=plt.subplots(2,3,figsize=(13,8.6),sharey=True)
for ax,(s,title) in zip(axes.flat,scen):
    ax.axvspan(XL,0.10,color="#C6EFCE",alpha=0.5,lw=0); ax.axvspan(0.10,0.30,color="#FFEB9C",alpha=0.4,lw=0); ax.axvspan(0.30,XR,color="#FFD6D6",alpha=0.35,lw=0)
    inv=0
    for i,f in enumerate(fam):
        y=len(fam)-1-i; r=D[(f,s)]
        w=float(r["ws_P0_pos"]); c=float(r["chat_P0_pos"]); ok=r["chat_gate"]=="PASSED"
        alpha=1.0 if ok else 0.25
        cc=min(max(c,XL+0.02),XR-0.02); clipped = cc!=c
        ax.plot([w,cc],[y,y],color=grey,lw=1.2,alpha=alpha,zorder=2)
        ax.plot(w,y,"o",ms=7,color=ws_c,mec="white",mew=1,zorder=4)
        ax.plot(cc,y,"o",ms=7,mfc="white",mec=ch_c,mew=1.6,alpha=alpha,zorder=5)
        if clipped:
            ax.text(cc+(0.03 if c<0 else -0.03),y+0.28,hu(c,2),fontsize=7.5,color=ch_c,alpha=0.6,ha="left" if c<0 else "right")
        if r["chat_C_below_P0"].lower()=="true":
            inv+=1; ax.text(XR+0.02,y,"†",fontsize=11,color=ch_c,va="center",ha="left",alpha=max(alpha,0.6),clip_on=False)
    t=title+("  († chat careless ≤ target)" if inv else "")
    ax.set_title(t,loc="left",fontsize=10.5,fontweight="bold")
    ax.set_xlim(XL,XR); ax.set_xticks([0,0.5,1]); ax.set_xticklabels(["0","0.5","1"],fontsize=9)
    for sp in ("top","right"): ax.spines[sp].set_visible(False)
for ax in axes[:,0]:
    ax.set_yticks(range(len(fam))); ax.set_yticklabels([nm[f] for f in fam][::-1],fontsize=9.5)
fig.supxlabel("Careful agent's position on the model's own scale (0 blameless, 1 careless)",fontsize=10,y=0.045)
h=[Line2D([],[],marker="o",ls="",color=ws_c,ms=7,label="worksheet"),
   Line2D([],[],marker="o",ls="",mfc="white",mec=ch_c,mew=1.6,ms=7,label="chat (same weights, same load)"),
   Line2D([],[],marker="o",ls="",mfc="white",mec=ch_c,mew=1.6,ms=7,alpha=0.25,label="chat reading that fails the gate")]
fig.legend(handles=h,loc="lower center",ncol=3,fontsize=9.5,frameon=False,bbox_to_anchor=(0.5,-0.015))
fig.tight_layout(rect=(0,0.06,0.985,1))
for e in ("png","pdf","svg"): fig.savefig(OUT+f"Figure_frame_by_scenario.{e}",dpi=300,bbox_inches="tight")
