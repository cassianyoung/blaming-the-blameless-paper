import os
DATA = os.environ.get("FIGURE_DATA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")) + "/"
OUT = os.environ.get("FIGURE_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")) + "/"
import csv, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from collections import defaultdict
plt.rcParams["font.family"]="DejaVu Sans"
R=list(csv.DictReader([l for l in open(DATA+"B5_across_scenarios_long.csv",encoding="utf-8-sig") if not l.startswith("#")]))
D=defaultdict(dict)
for r in R:
    D[r["model"]][r["scenario"]]=r
nm={"gpt4o":"GPT-4o","gpt6s_s":"gpt-6-sol","gpt6l_s":"gpt-6-luna","claude":"Claude Sonnet 5","haiku_s":"Claude Haiku 4.5",
    "qwen235b":"Qwen3-235B","qwen80b":"Qwen3-Next-80B","qwen30b":"Qwen3-30B","deepseek":"DeepSeek-V4.1 (log-prob)",
    "deepseek_s":"DeepSeek-V4.1 (sampled)","gemma27b":"Gemma-3-27B","llama70b":"Llama-3.3-70B","mistral24b":"Mistral-Small-24B",
    "grok43_s":"grok-4.3","kimi":"Kimi-K3","gpt6s_r":"gpt-6-sol (R)","gpt6l_r":"gpt-6-luna (R)","haiku_r":"Claude Haiku 4.5 (R)",
    "deepseek_r_mt8192":"DeepSeek-V4.1 (R)","gemini_r":"Gemini 3.8 Flash (R)","gemini_pro":"Gemini 3.1 Pro (R)","grok43_r":"grok-4.3 (R)"}
arms=["gpt4o","gpt6s_s","gpt6l_s","claude","haiku_s","qwen235b","qwen80b","qwen30b","deepseek","gemma27b","llama70b",
      "mistral24b","grok43_s","kimi","gpt6s_r","gpt6l_r","haiku_r","deepseek_r_mt8192","gemini_r","gemini_pro","grok43_r"]
# the sampled DeepSeek readout is a check row, counted once by its log-prob readout
# (one readout per model; review of v0.7, ruling 2026-10-18), so it is not drawn
noff=14
scen=[("bicycle216","Bicycle"),("ladder","Ladder"),("prawns_home","Prawns, home"),("prawns_restaurant","Prawns, restaurant"),("scaffolding","Scaffolding"),("cheque","Cheque")]
c0="#C0392B"; c0r="#2E7D32"; c1="#555555"
def pos(r,k):
    v=r.get(k+"_pos","")
    return float(v) if v not in ("",None) else None
# One x range for all six panels, the smallest given in the review that shows every point
# (data -0.29 to 0.98 at bf90d122); a point outside it refuses instead of being clamped
# to the edge (review of v0.7, item 6).
XL,XR=-0.35,1.05
fig,axes=plt.subplots(2,3,figsize=(14,13),sharey=True,sharex=True)
for ax,(s,t) in zip(axes.flat,scen):
    ax.axvspan(XL,0.10,color="#C6EFCE",alpha=0.5,lw=0); ax.axvspan(0.10,0.30,color="#FFEB9C",alpha=0.4,lw=0); ax.axvspan(0.30,XR,color="#FFD6D6",alpha=0.35,lw=0)
    ax.axhline(len(arms)-noff-0.5,color="#999999",lw=0.8,ls=(0,(3,3)))
    for i,a in enumerate(arms):
        y=len(arms)-1-i; r=D.get(a,{}).get(s)
        if r is None: continue
        p0,p1=pos(r,"P0"),pos(r,"P1")
        if p0 is None: ax.text(XL+0.03,y,"no reading",fontsize=7,color="#999999",va="center"); continue
        ok=r["gate"]=="PASSED"; al=1 if ok else 0.25
        def cl(v):
            assert XL<v<XR, f"{a} {s}: point {v} outside {XL}..{XR}: widen, do not clamp"
            return v
        fc=(c0 if i<noff else c0r)
        # one threshold with Figure 2: the ring marks a change of 0.02 or less (Cassian,
        # 2026-10-18; it was 0.03 here, so the two figures ringed different readings)
        if p1 is not None and abs(p1-p0)>0.02:
            ax.plot([cl(p0),cl(p1)],[y,y],color=c1,lw=1.1,alpha=al,zorder=2)
            ax.plot(cl(p1),y,"o",ms=6.5,mfc="white",mec=c1,mew=1.4,alpha=al,zorder=5)
            ax.plot(cl(p0),y,"o",ms=6.5,color=fc,mec="white",mew=0.8,alpha=al,zorder=4)
        else:
            ax.plot(cl(p0),y,"o",ms=6,color=fc,mec="white",mew=0.6,alpha=al,zorder=6)
            if p1 is not None: ax.plot(cl(p0),y,"o",ms=11,mfc="none",mec=c1,mew=1.3,alpha=al,zorder=5)
    ax.set_title(t,loc="left",fontsize=10.5,fontweight="bold")
    ax.set_xlim(XL,XR); ax.set_xticks([0,0.5,1]); ax.set_xticklabels(["0","0.5","1"],fontsize=9)
    ax.tick_params(labelbottom=True)
    for sp in ("top","right"): ax.spines[sp].set_visible(False)
for ax in axes[:,0]:
    ax.set_yticks(range(len(arms))); ax.set_yticklabels([nm[a] for a in arms][::-1],fontsize=8.5)
fig.supxlabel("Careful subject's position on the model's own scale (0 blameless, 1 careless)",fontsize=10,y=0.045)
h=[Line2D([],[],marker="o",ls="",color=c0,ms=7,label="careful subject, without reasoning"),
   Line2D([],[],marker="o",ls="",color=c0r,ms=7,label="careful subject, with reasoning (R)"),
   Line2D([],[],marker="o",ls="",mfc="white",mec=c1,mew=1.4,ms=7,label='excuse stated: "nothing anyone could have done"'),
   Line2D([],[],marker="o",ls="",color=c0,alpha=0.25,ms=7,label="fails the gate on that scenario")]
fig.legend(handles=h,loc="lower center",ncol=4,fontsize=9,frameon=False,bbox_to_anchor=(0.5,-0.005))
fig.tight_layout(rect=(0,0.06,1,1))
for e in ("png","pdf","svg"): fig.savefig(OUT+f"Figure_deployed_by_scenario.{e}",dpi=300,bbox_inches="tight")
