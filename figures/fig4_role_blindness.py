import os
DATA = os.environ.get("FIGURE_DATA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")) + "/"
OUT = os.environ.get("FIGURE_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")) + "/"
import csv, statistics as st, matplotlib
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
R=list(csv.DictReader([l for l in open(U+"fig7_duty.csv",encoding="utf-8-sig") if not l.startswith("#")]))
sha=[l for l in open(U+"fig7_duty.csv",encoding="utf-8-sig") if "sha256" in l][0].split("sha256:")[1].split()[0]
f=lambda x: None if x in ("",None) else float(x)
nm={"gpt4o":"GPT-4o","gpt6s_s":"gpt-6-sol","gpt6l_s":"gpt-6-luna","claude":"Claude Sonnet 5","haiku_s":"Claude Haiku 4.5",
    "qwen235b":"Qwen3-235B","qwen80b":"Qwen3-Next-80B","qwen30b":"Qwen3-30B","deepseek":"DeepSeek-V4.1 (log-prob)",
    "deepseek_s":"DeepSeek-V4.1 (sampled)","gemma27b":"Gemma-3-27B","llama70b":"Llama-3.3-70B","mistral24b":"Mistral-Small-24B",
    "grok43_s":"grok-4.3","kimi":"Kimi-K3","gpt6s_r":"gpt-6-sol","gpt6l_r":"gpt-6-luna","haiku_r":"Claude Haiku 4.5",
    "deepseek_r":"DeepSeek-V4.1","gemini_r":"Gemini 3.8 Flash","gemini_pro":"Gemini 3.1 Pro","grok43_r":"grok-4.3"}
by={}
for r in R:
    # the sampled DeepSeek readout is a check row (one readout per model; ruling 2026-10-18)
    if r["arm"] in nm and r["arm"]!="deepseek_s": by.setdefault(r["arm"],[]).append(r)
rows=[]
for a,rs in by.items():
    w,wc=[],[]
    for r in rs:
        if r["verdict"]=="NO CONVENTION STATED": continue
        if r["pair_id"]=="5": continue   # driving: the five conventions only (Cassian, 2026-10-18)
        s,sep,sc=f(r["stated_gap"]),f(r["separate_gap"]),f(r["stated_condition_gap"])
        if s is None or s<=0 or sep is None: continue
        w.append(1-sep/s)
        if sc is not None: wc.append(1-sc/s)
    if w: rows.append((a,rs[0]["reasoning"],st.median(w),st.median(wc) if wc else None,len(w)))
off=sorted([r for r in rows if r[1]=="off"],key=lambda r:-r[2]); on=sorted([r for r in rows if r[1]=="on"],key=lambda r:-r[2])
rows=off+on
red="#7B3FA0"; grey="#555555"; green="#2E7D32"
# XL reaches past the lowest point so nothing is clipped (review of v0.7, item 7: grok-4.3
# with reasoning, told the convention, was drawn at the edge with a label). A point outside
# the axis refuses rather than being clamped.
XL,XR=-1.45,1.05
fig,b=plt.subplots(figsize=(11.2,9.2))
b.axvspan(XL,-0.30,facecolor="#FFD6D6",alpha=0.40,lw=0)
b.axvspan(XL,-0.30,facecolor="none",edgecolor="#E8A8A8",hatch="///",lw=0)
b.axvspan(-0.30,-0.10,color="#FFEB9C",alpha=0.45,lw=0)
b.axvspan(-0.10,0.10,color="#C6EFCE",alpha=0.55,lw=0)
b.axvspan(0.10,0.30,color="#FFEB9C",alpha=0.45,lw=0)
b.axvspan(0.30,XR,color="#FFD6D6",alpha=0.40,lw=0)
ys=list(range(len(rows)))[::-1]
def clip(v):
    assert XL<v<XR, f"point {v} outside the axis {XL}..{XR}: widen it, do not clamp"
    return v
for y,(a,re,w0,w1,n) in zip(ys,rows):
    col=red if re=="off" else green
    if w1 is not None and abs(w1-w0)>0.02:
        b.annotate("",xy=(clip(w1),y),xytext=(clip(w0),y),arrowprops=dict(arrowstyle="-|>",color=grey,lw=1.3,shrinkA=5,shrinkB=4))
        b.plot(clip(w1),y,"o",ms=7,mfc="white",mec=grey,mew=1.5,zorder=6)
    b.plot(clip(w0),y,"o",ms=8,color=col,mec="white",mew=1.2,zorder=5)
lab=[nm[r[0]]+(" (reasoning)" if r[1]=="on" else "") for r in rows]
b.set_yticks(ys); b.set_yticklabels(lab,fontsize=9.5)
b.axhline(len(on)-0.5,color="#999999",lw=0.8,ls=(0,(3,3)))
b.set_xlim(XL,XR); b.set_xticks([-1,-0.5,0,0.25,0.5,0.75,1])
b.set_xticklabels(["−1\ndouble","−0.5","0\napplies all","0.25","0.5","0.75","1\nwithholds all"])
for s in ("top","right"): b.spines[s].set_visible(False)
b.set_title("Deployed models (chat): convention unstated → stated",loc="left",fontsize=12,fontweight="bold")
b.set_xlabel("Share of the model's own stated slack it withholds",fontsize=10)
keyB=[Patch(fc="#C6EFCE",ec="#BBBBBB",label="Applies its convention: within\na tenth of the slack it states"),
      Patch(fc="#FFEB9C",ec="#BBBBBB",label="A tenth to three tenths off,\ntoo little (right) or too much (left)"),
      Patch(fc="#FFD6D6",ec="#BBBBBB",label="Withholds more than\nthree tenths of it"),
      Patch(fc="#FFE5E5",ec="#E8A8A8",hatch="///",label="Overshoots: gives more than three\ntenths more than it states")]
keyM=[Line2D([],[],marker="o",ls="",color=red,ms=8,label="Private person judged alone,\nwithout reasoning"),
      Line2D([],[],marker="o",ls="",color=green,ms=8,label="Private person judged alone,\nwith reasoning"),
      Line2D([],[],marker="o",ls="",mfc="white",mec=grey,mew=1.5,ms=8,label="Convention stated\nin the prompt")]
l1=fig.legend(handles=keyM,title="Markers",loc="upper left",bbox_to_anchor=(0.70,0.90),fontsize=9.5,title_fontsize=10,frameon=False,labelspacing=1.1,alignment="left")
l2=fig.legend(handles=keyB,title="Background",loc="upper left",bbox_to_anchor=(0.70,0.58),fontsize=9.5,title_fontsize=10,frameon=False,labelspacing=1.1,handlelength=1.6,handleheight=1.3,alignment="left")
fig.tight_layout(rect=(0,0,0.69,1))
for e in ("png","pdf","svg"): fig.savefig(OUT+f"Figure_bias2_headline.{e}",dpi=300,bbox_inches="tight")
for r in rows: print(f"{r[0]:12} {r[1]:3} withheld {r[2]:+.2f}  stated-cond {r[3] if r[3] is None else round(r[3],2)}  n={r[4]}")
print(sha[:16])
