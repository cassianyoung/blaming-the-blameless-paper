import os
DATA = os.environ.get("FIGURE_DATA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")) + "/"
OUT = os.environ.get("FIGURE_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")) + "/"
import csv, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from decimal import Decimal, ROUND_HALF_UP
def hu(x, nd, sign=False, pct=False):
    """Round half up, as the text does (2.15 -> 2.2), on the value's shortest decimal form."""
    d = Decimal(repr(float(x))) * (100 if pct else 1)
    q = d.quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)
    return (f"{q:+f}" if sign else f"{q:f}") + ("%" if pct else "")
plt.rcParams["font.family"]="DejaVu Sans"
U=DATA
rd=lambda f:list(csv.DictReader([l for l in open(U+f,encoding="utf-8-sig") if not l.startswith("#")]))
R=rd("fig7_duty.csv"); P={p["pair_id"]:p for p in rd("fig7_duty_panels.csv")}
sha=[l for l in open(U+"fig7_duty.csv",encoding="utf-8-sig") if "sha256" in l][0].split("sha256:")[1].split()[0]
f=lambda x: None if x in ("",None) else float(x)
nm={"gpt4o":"GPT-4o","gpt6s_s":"gpt-6-sol","gpt6l_s":"gpt-6-luna","claude":"Claude Sonnet 5","haiku_s":"Claude Haiku 4.5",
    "qwen235b":"Qwen3-235B","qwen80b":"Qwen3-Next-80B","qwen30b":"Qwen3-30B","deepseek":"DeepSeek-V4.1 (log-prob)",
    "deepseek_s":"DeepSeek-V4.1 (sampled)","gemma27b":"Gemma-3-27B","llama70b":"Llama-3.3-70B","mistral24b":"Mistral-Small-24B",
    "grok43_s":"grok-4.3","kimi":"Kimi-K3","gpt6s_r":"gpt-6-sol (R)","gpt6l_r":"gpt-6-luna (R)","haiku_r":"Claude Haiku 4.5 (R)",
    "deepseek_r":"DeepSeek-V4.1 (R)","gemini_r":"Gemini 3.8 Flash (R)","grok43_r":"grok-4.3 (R)","gemini_pro":"Gemini 3.1 Pro (R)"}
off=["gpt4o","gpt6s_s","gpt6l_s","claude","haiku_s","qwen235b","qwen80b","qwen30b","deepseek","gemma27b","llama70b","mistral24b","grok43_s","kimi"]
on=["gpt6s_r","gpt6l_r","haiku_r","deepseek_r","gemini_r","gemini_pro","grok43_r"]
D={(r["arm"],r["pair_id"]):r for r in R}
PIDS=["prawns","1","3","4","5","7"]
def shortfall(a):
    v=[f(D[(a,p)]["stated_gap"])-f(D[(a,p)]["separate_gap"]) for p in PIDS
       if (a,p) in D and f(D[(a,p)]["stated_gap"]) is not None and f(D[(a,p)]["separate_gap"]) is not None]
    return sum(v)/len(v) if v else None
key=lambda a: (shortfall(a) is None, -(shortfall(a) or 0))
off=sorted(off,key=key); on=sorted(on,key=key)
arms=off+on; noff=len(off)
for a in arms: print(f"{a:12} {shortfall(a)}")
assert all((a,"prawns") in D for a in arms)
panels=[("prawns","Prawns: chef / home cook"),("1","Electrical: electrician / homeowner"),("3","Gas: landlord / friend"),
        ("4","Childcare: childminder / grandfather"),("5","Driving: taxi driver / friend"),("7","Hair dye: hairdresser / friend")]
C_ST="#2C5D8F"; C_SC="#7B3FA0"
RED="#C0392B"; AMB="#E08E0B"; GRY="#9E9E9E"
def tri_col(r):
    v=r["verdict"]
    if v=="NO CONVENTION STATED": return GRY
    if v=="NOT APPLIED": return RED
    if v in ("PARTLY","APPLIED"): return AMB
    return GRY
XL,XR=-2.0,5.6
fig,axes=plt.subplots(3,2,figsize=(13,17),sharey=True)
for ax,(pid,title) in zip(axes.flat,panels):
    p=P[pid]
    ax.axvline(0,color="#444444",lw=0.8)
    ax.axhline(len(arms)-noff-0.5,color="#999999",lw=0.8,ls=(0,(3,3)))
    for i,a in enumerate(arms):
        y=len(arms)-1-i; r=D[(a,pid)]
        fl=f(r["floor_used"])
        st,sep,sc=f(r["stated_gap"]),f(r["separate_gap"]),f(r["stated_condition_gap"])
        noconv = r["verdict"]=="NO CONVENTION STATED"
        al=1.0
        if noconv: sep=None; sc=None
        cl=lambda v: min(max(v,XL+0.05),XR-0.05)
        pts=[v for v in (st,sep) if v is not None]
        if len(pts)==2: ax.annotate("",xy=(cl(sep),y),xytext=(cl(st),y),arrowprops=dict(arrowstyle="-|>",color="#AAAAAA",lw=1.0,shrinkA=4,shrinkB=4,alpha=al),zorder=1)
        if st is not None: ax.plot(cl(st),y,"s",ms=6.5,color=("#A6A6A6" if noconv else C_ST),alpha=al,zorder=4)
        if sep is not None: ax.plot(cl(sep),y,"o",ms=7,color="#1A1A1A",zorder=5)
        if sc is not None: ax.plot(cl(sc),y,"o",ms=8,mfc="white",mec="#555555",mew=1.5,zorder=6)
    import statistics as stt
    ms=stt.median([f(D[(a,pid)]["stated_gap"]) for a in arms if f(D[(a,pid)]["stated_gap"]) is not None])
    sub=(f"slack stated: median {hu(ms,1)}   ·   slack given: median {hu(p['median_share'],0,pct=True)} of it"
         if p["median_share"] else f"slack stated: median {hu(ms,1)}")
    sub2=f"slack given when told the convention: median {hu(p['median_stated_condition_gap'],1)}"
    ax.set_title(title,loc="left",fontsize=11,fontweight="bold",pad=26)
    ax.text(0,1.035,sub,transform=ax.transAxes,fontsize=8.3,color="#333333")
    ax.text(0,1.005,sub2,transform=ax.transAxes,fontsize=8.3,color="#333333")
    ax.set_xlim(XL,XR); ax.set_xticks([-2,-1,0,1,2,3,4,5]); ax.tick_params(axis="x",labelsize=8.5)
    for s in ("top","right"): ax.spines[s].set_visible(False)
for ax in axes[:,0]:
    ax.set_yticks(range(len(arms))); ax.set_yticklabels([nm[a] for a in arms][::-1],fontsize=8.5)
for ax in axes[:,1]: ax.tick_params(axis="y",length=0)
fig.supxlabel("Slack for the private person: the professional's blame minus the private person's, on the 0–9 scale",fontsize=10,y=0.035)
h=[Line2D([],[],marker="s",ls="",color=C_ST,ms=7,label="slack the model says the private person deserves (both cases side by side)"),
   Line2D([],[],marker="o",ls="",color="#1A1A1A",ms=7,label="slack it gives him (each case judged alone)"),
   Line2D([],[],marker="o",ls="",mfc="white",mec="#555555",mew=1.5,ms=8,label="slack it gives him when told the convention"),
   Line2D([],[],marker="s",ls="",color="#A6A6A6",ms=7,label="grey square: no clear slack stated, so nothing to test")]
fig.legend(handles=h,loc="lower center",ncol=2,fontsize=9,frameon=False,bbox_to_anchor=(0.5,-0.01))
fig.tight_layout(rect=(0,0.055,1,1),h_pad=3.2)
for e in ("png","pdf","svg"): fig.savefig(OUT+f"Figure7_duty.{e}",dpi=300,bbox_inches="tight")
print(sha[:16])
