import os
DATA = os.environ.get("FIGURE_DATA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")) + "/"
OUT = os.environ.get("FIGURE_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")) + "/"
import csv, statistics as st, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
plt.rcParams["font.family"]="DejaVu Sans"
U=DATA
R=list(csv.DictReader([l for l in open(U+"fig4to7_duty.csv",encoding="utf-8-sig") if not l.startswith("#")]))
f=lambda x: None if x in ("",None) else float(x)
nm={"gpt4o":"GPT-4o","gpt6s_s":"gpt-6-sol","gpt6l_s":"gpt-6-luna","claude":"Claude Sonnet 5","haiku_s":"Claude Haiku 4.5",
    "qwen235b":"Qwen3-235B","qwen80b":"Qwen3-Next-80B","qwen30b":"Qwen3-30B","deepseek":"DeepSeek-V4.1 (log-prob)",
    "gemma27b":"Gemma-3-27B","llama70b":"Llama-3.3-70B","mistral24b":"Mistral-Small-24B",
    "grok43_s":"grok-4.3","kimi":"Kimi-K3","gpt6s_r":"gpt-6-sol (R)","gpt6l_r":"gpt-6-luna (R)","haiku_r":"Claude Haiku 4.5 (R)",
    "deepseek_r":"DeepSeek-V4.1 (R)","gemini_r":"Gemini 3.8 Flash (R)","gemini_pro":"Gemini 3.1 Pro (R)","grok43_r":"grok-4.3 (R)"}
by={}
for r in R:
    if r["arm"] not in nm: continue
    by.setdefault(r["arm"],[]).append(r)
rows=[]
for a,rs in by.items():
    fd=f(rs[0]["floor_draw"]); fs=f(rs[0]["floor_sentence"])
    stated=[f(r["stated_gap"]) for r in rs if r["pair_id"]!="5" and f(r["stated_gap"]) is not None]
    rows.append((a,fd,fs,st.median(stated)))
rows=[r for r in rows if r[2] is not None]
rows.sort(key=lambda r:-r[2])
fig,ax=plt.subplots(figsize=(7.5,7.2))
for i,(a,fd,fs,ms) in enumerate(rows):
    y=len(rows)-1-i
    ax.plot([0,max(fd,fs)],[y,y],color="#EEEEEE",lw=1,zorder=0)
    # hollow and a little larger, drawn above the diamond, so a draw floor that coincides
    # with the wording floor stays visible (review of v0.7, item 10)
    ax.plot(fd,y,"o",ms=9,mfc="none",mec="#6E6E6E",mew=1.6,zorder=5)
    ax.plot(fs,y,"D",ms=7,color="#C0392B",zorder=4)
ax.set_yticks(range(len(rows))); ax.set_yticklabels([nm[r[0]] for r in rows][::-1],fontsize=9)
ax.set_xlim(0,2.5)
ax.set_xlabel("Points on the 0–9 blame scale",fontsize=10)
for s in ("top","right"): ax.spines[s].set_visible(False)
h=[Line2D([],[],marker="o",ls="",mfc="none",mec="#6E6E6E",mew=1.6,ms=9,label="draw noise: the same prompt, asked again"),
   Line2D([],[],marker="D",ls="",color="#C0392B",ms=7,label="wording noise: an irrelevant sentence added")]
ax.legend(handles=h,loc="upper center",bbox_to_anchor=(0.42,-0.08),ncol=1,fontsize=9,frameon=False)
fig.tight_layout()
for e in ("png","pdf","svg"): fig.savefig(OUT+f"Figure7_noise.{e}",dpi=300,bbox_inches="tight")
n_over=sum(1 for r in rows if r[2]>=r[3]); n_half=sum(1 for r in rows if r[2]>=0.5*r[3])
print(len(rows),"models; wording noise >= convention on",n_over,"; >= half on",n_half)
print("median draw",round(st.median(r[1] for r in rows),2),"median wording",round(st.median(r[2] for r in rows),2),"median stated",round(st.median(r[3] for r in rows),2))
for r in rows: print(f"{r[0]:12} draw {r[1]:.2f} wording {r[2]:.2f} stated {r[3]:.2f}")
