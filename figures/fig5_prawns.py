import os
DATA = os.environ.get("FIGURE_DATA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")) + "/"
OUT = os.environ.get("FIGURE_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")) + "/"
import csv, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.transforms import blended_transform_factory as btf
from decimal import Decimal, ROUND_HALF_UP
def hu(x, nd, sign=False, pct=False):
    """Round half up, as the text does (2.15 -> 2.2), on the value's shortest decimal form."""
    d = Decimal(repr(float(x))) * (100 if pct else 1)
    q = d.quantize(Decimal(1).scaleb(-nd), rounding=ROUND_HALF_UP)
    return (f"{q:+f}" if sign else f"{q:f}") + ("%" if pct else "")
plt.rcParams["font.family"]="DejaVu Sans"
R=list(csv.DictReader([l for l in open(DATA+"chef_home.csv",encoding="utf-8-sig") if not l.startswith("#")]))
fl=lambda x: None if x in ("",None) else float(x)
SC={}
for q in csv.DictReader([l for l in open(DATA+"fig7_duty.csv",encoding="utf-8-sig") if not l.startswith("#")]):
    if q["pair_id"]=="prawns" and q["stated_condition_gap"] not in ("",None): SC[q["arm"]]=float(q["stated_condition_gap"])
nm={"claude":"Claude Sonnet 5","deepseek":"DeepSeek-V4.1 (log-prob)","deepseek_s":"DeepSeek-V4.1 (sampled)","deepseek_r":"DeepSeek-V4.1 (reasoning)",
    "gemini_r":"Gemini 3.8 Flash (reasoning)","gemini_pro":"Gemini 3.1 Pro (reasoning)","gemma27b":"Gemma-3-27B","gpt4o":"GPT-4o",
    "gpt6l_s":"gpt-6-luna","gpt6l_r":"gpt-6-luna (reasoning)","gpt6s_s":"gpt-6-sol","gpt6s_r":"gpt-6-sol (reasoning)",
    "grok43_s":"grok-4.3","grok43_r":"grok-4.3 (reasoning)","llama70b":"Llama-3.3-70B","mistral24b":"Mistral-Small-24B",
    "haiku_s":"Claude Haiku 4.5","haiku_r":"Claude Haiku 4.5 (reasoning)","kimi":"Kimi-K3","qwen235b":"Qwen3-235B","qwen30b":"Qwen3-30B","qwen80b":"Qwen3-Next-80B",
    "llama31":"Llama 3.1 8B","qwen3":"Qwen3 8B","mistral":"Mistral 7B","olmo2":"OLMo 2 7B","falcon3":"Falcon3 7B",
    "gemma9":"Gemma 2 9B","gemma27":"Gemma 2 27B","yi34b":"Yi 1.5 34B","yi6b":"Yi 1.5 6B (chat)","yi9b":"Yi 1.5 9B (chat)"}
api=[r for r in R if r["source"]=="api" and r["model"]!="deepseek_s"]; loc=[r for r in R if r["source"]=="local"]
off=[r for r in api if r["reasoning"]=="off"]; on=[r for r in api if r["reasoning"]!="off"]
k=lambda r:(fl(r["stated_gap_digits"]) or 0)
off.sort(key=k,reverse=True); on.sort(key=k,reverse=True)
loc.sort(key=lambda r: fl(r["careless_gap_digits"]) or 0, reverse=True)
groups=[("Deployed, without reasoning",off),("Deployed, with reasoning",on)]
c_st="#2C5D8F"; c_cl="#1A1A1A"; c_sc="#555555"
order=[]
for g,rs in groups: order.append(("H",g)); order+=[("R",r) for r in rs]
fig,(ax,tx)=plt.subplots(1,2,figsize=(12.2,9.2),sharey=True,gridspec_kw={"width_ratios":[1.15,0.6],"wspace":0.02})
tx.axis("off"); tx.set_xlim(-0.5,2.75)
ax.axvline(0,color="#333333",lw=1)
tr=tx.transData
cx=[0.3,1.2,2.2]
y=len(order)+0.6
for x,t in zip(cx,["Paired\nscores","Separate\ncases","Separate ÷\npaired"]):
    ax.text(x,y,t,transform=tr,ha="center",va="bottom",fontsize=9,fontweight="bold",clip_on=False)
y=len(order); labels=[]; ys=[]
for kind,obj in order:
    y-=1
    if kind=="H":
        ax.text(-0.95,y,obj,fontsize=10,fontweight="bold",va="center"); continue
    r=obj; ok=r["gate"] in ("PASSED","NOT ASKED"); a=1.0 if ok else 0.35
    st,cl=fl(r["stated_gap_digits"]),fl(r["careless_gap_digits"])
    pts=[v for v in (st,cl) if v is not None]
    if len(pts)==2: ax.annotate("",xy=(cl,y),xytext=(st,y),arrowprops=dict(arrowstyle="-|>",color="#999999",lw=1.1,shrinkA=5,shrinkB=5,alpha=a))
    if st is not None: ax.plot(st,y,"s",ms=7.5,color=c_st,alpha=a,zorder=4)
    if cl is not None: ax.plot(cl,y,"o",ms=7.5,color=c_cl,alpha=a,zorder=5)
    sc=SC.get(r["model"])
    if sc is not None: assert sc<4.5, (r["model"],sc); ax.plot(sc,y,"o",ms=8,mfc="white",mec=c_sc,mew=1.5,alpha=a,zorder=6)
    stxt=hu(st,2,sign=True) if st is not None else "—"
    ctxt=hu(cl,2,sign=True) if cl is not None else "—"
    # THE FLOOR RULE (review of v0.7, item 8). The share is printed only where the export
    # reports one, which is where the stated slack exceeds the model's wording floor, as
    # Table A.9 does; below the floor the cell is "—" and uncoloured (A.9's "–a"). The old
    # test (stated > 0.2) printed a share for four rows A.9 marks "–a" and hid gpt-6-luna's
    # only because its stated gap happens to be 0.2.
    sh=fl(r["share"]); fu=fl(r["floor_used"])
    if sh is not None:
        assert st is not None and cl is not None and fu is not None and st>fu, (r["model"],st,fu)
        assert abs(sh-cl/st)<1e-4, (r["model"],sh,cl,st)   # the export rounds to 4 places
    else:
        assert st is None or cl is None or fu is None or st<=fu, (r["model"],st,fu,"share withheld above the floor")
    rtxt=hu(sh,0,pct=True) if sh is not None else "—"
    ratio = sh
    fc = None
    if ratio is not None:
        fc = "#C6EFCE" if ratio>=2/3 else ("#FFEB9C" if ratio>=1/3 else "#F4B6B0")
    for i,(x,t) in enumerate(zip(cx,[stxt,ctxt,rtxt])):
        kw=dict(transform=tr,ha="center",va="center",fontsize=9,alpha=max(a,0.6),clip_on=False)
        if fc and i in (1,2): kw["bbox"]=dict(boxstyle="round,pad=0.3",fc=fc,ec="none")
        ax.text(x,y,t,**kw)
    labels.append(nm[r["model"]]); ys.append(y)
ax.set_yticks(ys); ax.set_yticklabels(labels,fontsize=9)
ax.set_ylim(-0.8,len(order)+0.4); ax.set_xlim(-1.0,4.5)
ax.set_xlabel("Slack for the home cook: the careless chef's blame minus the careless home cook's, on the 0–9 scale",fontsize=10)
for s in ("top","right"): ax.spines[s].set_visible(False)
h=[Line2D([],[],marker="s",ls="",color=c_st,ms=7.5,label="slack stated (both cases side by side)"),
   Line2D([],[],marker="o",ls="",color=c_cl,ms=7.5,label="slack given (each case judged alone)"),
   Line2D([],[],marker="o",ls="",mfc="white",mec=c_sc,mew=1.5,ms=8,label="slack given when told the convention"),
]
from matplotlib.patches import Patch
h+= [Patch(fc="#C6EFCE",label="separate ≥ ⅔ of stated"),Patch(fc="#FFEB9C",label="⅓–⅔ of stated"),Patch(fc="#F4B6B0",label="< ⅓ of stated")]
ax.legend(handles=h,loc="upper center",bbox_to_anchor=(0.62,-0.085),ncol=3,fontsize=9,frameon=False)
fig.tight_layout()
for e in ("png","pdf","svg"): fig.savefig(OUT+f"Figure5_prawns.{e}",dpi=300,bbox_inches="tight")
