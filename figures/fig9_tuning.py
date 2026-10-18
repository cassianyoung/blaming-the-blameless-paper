import os
DATA = os.environ.get("FIGURE_DATA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")) + "/"
OUT = os.environ.get("FIGURE_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")) + "/"
import csv, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
plt.rcParams["font.family"]="DejaVu Sans"
# RUN 216, the reading Table A.1 prints (review of v0.7, item 1: A.1, A.6, section 4.5 and
# Figure 9 report base-model worksheet positions from one run). Run 216 never read
# Yi-1.5-34B-Chat on the worksheet, so Yi has no release square; Llama 3.1's blameless case
# was read on one ordering, so its base interval is not drawn.
SRC="A1_run216_tuning_table.csv"
_rows=list(csv.DictReader([l for l in open(DATA+SRC,encoding="utf-8-sig") if not l.startswith("#")]))
assert {r["run"] for r in _rows}=={"216"}, {r["run"] for r in _rows}
T=[r for r in _rows if r["is_footnote_row"]=="0"]
foot=[r for r in _rows if r["is_footnote_row"]=="1"][0]
fv=lambda x: None if x in ("",None) else float(x)
names={"llama31":"Llama 3.1 8B","qwen3":"Qwen3 8B","mistral":"Mistral 7B","olmo2":"OLMo 2 7B","falcon3":"Falcon3 7B",
       "gemma9":"Gemma 2 9B","stablelm12b":"StableLM 2 12B","gemma27":"Gemma 2 27B","yi34b":"Yi 1.5 34B"}
T.sort(key=lambda r: float(r["base_P0_pos"]), reverse=True)
c_base="#C0392B"; c_ad="#E08E0B"; c_in="#2C5D8F"; grey="#555555"
fig,ax=plt.subplots(figsize=(8.2,6.4))
ax.axvspan(-0.15,0.10,color="#C6EFCE",alpha=0.55,lw=0); ax.axvspan(0.10,0.30,color="#FFEB9C",alpha=0.45,lw=0); ax.axvspan(0.30,1.02,color="#FFD6D6",alpha=0.40,lw=0)
ys=list(range(len(T)))[::-1]; off=0.09
for y,r in zip(ys,T):
    b,lo,hi=float(r["base_P0_pos"]),fv(r["base_P0_ci_low"]),fv(r["base_P0_ci_high"])
    ad,ins,by=float(r["adapter_P0_pos"]),fv(r["instruct_P0_pos"]),float(r["base_BYST_pos"])
    xs=[v for v in (b,ad,ins,by,lo,hi) if v is not None]
    ax.plot([min(xs)-0.02,max(xs)+0.02],[y,y],color="#bbbbbb",lw=0.8,zorder=1)
    ax.plot(by,y,"D",ms=7,mfc="white",mec=grey,mew=1.4,zorder=7)
    if lo is not None: ax.plot([lo,hi],[y+off,y+off],color=c_base,lw=2.2,zorder=4)
    ax.plot(b,y+off,"o",ms=8,color=c_base,mec="white",mew=1.1,zorder=5)
    ax.plot(ad,y,"^",ms=8,color=c_ad,mec="white",mew=1.0,zorder=5)
    if ins is not None: ax.plot(ins,y-off,"s",ms=7,color=c_in,mec="white",mew=1.0,zorder=5)
ax.plot(float(foot["adapter_P0_pos"]),ys[[r["family"] for r in T].index("yi34b")],"^",ms=8,mfc="white",mec=c_ad,mew=1.5,zorder=8)
ax.set_yticks(ys); ax.set_yticklabels([names[r["family"]] for r in T],fontsize=10.5)
ax.set_xlim(-0.15,1.02); ax.set_xticks([0,0.25,0.5,0.75,1]); ax.set_xticklabels(["0\nblameless","0.25","0.5","0.75","1\ncareless"])
ax.set_xlabel("Careful agent's position on the model's own scale (worksheet, bicycle)",fontsize=10)
for s in ("top","right"): ax.spines[s].set_visible(False)
h=[Line2D([],[],marker="o",ls="",color=c_base,ms=8,label="pretrained base (95% interval)"),
   Line2D([],[],marker="^",ls="",color=c_ad,ms=8,label="+ study adapter (English corpus)"),
   Line2D([],[],marker="^",ls="",mfc="white",mec=c_ad,ms=8,label="+ study adapter (Chinese corpus; Yi only)"),
   Line2D([],[],marker="s",ls="",color=c_in,ms=7,label="developer's instruction-tuned release"),
   Line2D([],[],marker="D",ls="",mfc="white",mec=grey,ms=7,label="uninvolved bystander (base)")]
ax.legend(handles=h,loc="upper center",bbox_to_anchor=(0.45,-0.13),ncol=2,fontsize=9,frameon=False)
fig.tight_layout()
for ext in ("png","pdf","svg"): fig.savefig(OUT+f"Figure_tuning.{ext}",dpi=300,bbox_inches="tight")
