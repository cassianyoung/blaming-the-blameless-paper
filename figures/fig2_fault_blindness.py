import os
DATA = os.environ.get("FIGURE_DATA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")) + "/"
OUT = os.environ.get("FIGURE_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")) + "/"
import csv, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from matplotlib.patches import Patch
from matplotlib.legend_handler import HandlerTuple
plt.rcParams["font.family"]="DejaVu Sans"
U=DATA
A=list(csv.DictReader([l for l in open(U+"fig2_panelA.csv",encoding="utf-8-sig") if not l.startswith("#")]))
B=list(csv.DictReader([l for l in open(U+"fig2_panelB.csv",encoding="utf-8-sig") if not l.startswith("#")]))
f=lambda x: None if x in ("",None) else float(x)

nameA={"llama31":"Llama 3.1 8B","qwen3":"Qwen3 8B","mistral":"Mistral 7B","olmo2":"OLMo 2 7B","falcon3":"Falcon3 7B",
       "gemma9":"Gemma 2 9B","stablelm12b":"StableLM 2 12B","gemma27":"Gemma 2 27B","yi34b":"Yi 1.5 34B"}
nameB={"claude":"Claude Sonnet 5","deepseek":"DeepSeek-V4.1 (log-prob)","deepseek_s":"DeepSeek-V4.1 (sampled)",
       "deepseek_r_bike8192_all":"DeepSeek-V4.1","gemini_r":"Gemini 3.8 Flash","gemini_pro":"Gemini 3.1 Pro","gemma27b":"Gemma-3-27B","gpt4o":"GPT-4o",
       "gpt6l_s_bike":"gpt-6-luna","gpt6l_r_bike":"gpt-6-luna","gpt6s_s_bike":"gpt-6-sol","gpt6s_r_bike":"gpt-6-sol",
       "gptoss_r":"GPT-OSS-120B","grok43_s_bike":"grok-4.3","grok43_r_bike":"grok-4.3","haiku":"Claude Haiku 4.5",
       "haiku_r":"Claude Haiku 4.5","haiku_s":"Claude Haiku 4.5","kimi":"Kimi-K3","llama70b":"Llama-3.3-70B","mistral24b":"Mistral-Small-24B",
       "qwen235b":"Qwen3-235B","qwen30b":"Qwen3-30B","qwen80b":"Qwen3-Next-80B"}

red="#C0392B"; grey="#555555"; blue="#2C5D8F"; green="#2E7D32"
fig,(a,b)=plt.subplots(1,2,figsize=(15.5,9.2),gridspec_kw={"width_ratios":[1,1.15]})
def bands(ax):
    ax.axvspan(-0.25,0.10,color="#C6EFCE",alpha=0.55,lw=0)
    ax.axvspan(0.10,0.30,color="#FFEB9C",alpha=0.45,lw=0)
    ax.axvspan(0.30,1.02,color="#FFD6D6",alpha=0.40,lw=0)
    ax.set_xlim(-0.25,1.02); ax.set_xticks([0,0.25,0.5,0.75,1])
    ax.set_xticklabels(["0\nblameless","0.25","0.5","0.75","1\ncareless"])
    for s in ("top","right"): ax.spines[s].set_visible(False)

# Panel A, sorted by P0
A.sort(key=lambda r: f(r["P0_pos"]), reverse=True)
bands(a); ys=list(range(len(A)))[::-1]
for y,r in zip(ys,A):
    p,lo,hi,by=f(r["P0_pos"]),f(r["P0_ci_low"]),f(r["P0_ci_high"]),f(r["BYST_pos"])
    # Every base model is drawn in one colour (review of v0.7, item 5). Yi-1.5-34B was
    # blue by name, with no legend entry and no reason recorded in the renderer.
    c=red
    a.plot([by,p],[y,y],color="#bbbbbb",lw=1,zorder=1)
    a.plot(by,y,"D",ms=7,mfc="white",mec=grey,mew=1.4,zorder=4)
    a.plot([lo,hi],[y,y],color=c,lw=2.2,zorder=3)
    a.plot(p,y,"o",ms=8,color=c,mec="white",mew=1.2,zorder=5)
    if r["gap_clears_2_bands"]=="yes":
        a.text(1.0,y,"✓",fontsize=11,color=green,va="center",ha="left")
a.set_yticks(ys); a.set_yticklabels([nameA[r["model"]] for r in A],fontsize=10)
a.set_title("A. Pretrained models (worksheet)",loc="left",fontsize=12,fontweight="bold")
a.set_xlabel("Position on the model's own scale",fontsize=10)
a.legend(handles=[Line2D([],[],marker="o",ls="",color=red,ms=8,label="careful subject (95% interval)"),
                  Line2D([],[],marker="D",ls="",mfc="white",mec=grey,ms=7,label="uninvolved bystander"),
                  Line2D([],[],marker="$✓$",ls="",color=green,ms=9,label="careful subject > bystander by 2+ bands")],
         loc="upper center",bbox_to_anchor=(0.45,-0.09),fontsize=9,frameon=False)

# Panel B: non-reasoning sorted, then reasoning sorted
# The sampled DeepSeek-V4.1 readout is a check row, not a model: removed here as from
# Figures 5, 6 and 7 (review of v0.7, item 5). One readout per model.
B=[r for r in B if r["model"]!="deepseek_s"]
off=[r for r in B if r["reasoning"]=="off"]; on=[r for r in B if r["reasoning"]=="on"]
off.sort(key=lambda r: f(r["P0_pos"]), reverse=True); on.sort(key=lambda r: f(r["P0_pos"]), reverse=True)
rows=off+on
bands(b); ys=list(range(len(rows)))[::-1]
for y,r in zip(ys,rows):
    p0,p1=f(r["P0_pos"]),f(r["P1_pos"]); col=red if r["reasoning"]=="off" else green
    if p1 is not None and abs(p1-p0)>0.02:
        b.annotate("",xy=(p1,y),xytext=(p0,y),arrowprops=dict(arrowstyle="-|>",color=grey,lw=1.3,shrinkA=5,shrinkB=4))
        b.plot(p1,y,"o",ms=7,mfc="white",mec=grey,mew=1.5,zorder=6)
        b.plot(p0,y,"o",ms=8,color=col,mec="white",mew=1.2,zorder=5)
    else:
        b.plot(p0,y,"o",ms=8,color=col,mec="white",mew=1.2,zorder=5)
        if p1 is not None: b.plot(p0,y,"o",ms=13,mfc="none",mec=grey,mew=1.5,zorder=6)
lab=[nameB[r["model"]]+(" (reasoning)" if r["reasoning"]=="on" else "") for r in rows]
b.set_yticks(ys); b.set_yticklabels(lab,fontsize=9.5)
b.axhline(len(on)-0.5,color="#999999",lw=0.8,ls=(0,(3,3)))
b.set_title("B. Deployed models (chat): excuse unstated → stated",loc="left",fontsize=12,fontweight="bold")
b.set_xlabel("Position on the model's own scale",fontsize=10)
b.legend(handles=[Line2D([],[],marker="o",ls="",color=red,ms=8,label="careful subject, without reasoning"),
                  Line2D([],[],marker="o",ls="",color=green,ms=8,label="careful subject, with reasoning"),
                  Line2D([],[],marker="o",ls="",mfc="white",mec=grey,ms=7,label='excuse stated: "nothing anyone could have done"'),
                  # the overlapping circle-and-ring, drawn as the panel draws it (item 5)
                  (Line2D([],[],marker="o",ls="",color=red,ms=8,mec="white",mew=1.2),
                   Line2D([],[],marker="o",ls="",mfc="none",mec=grey,ms=13,mew=1.5))],
         labels=["careful subject, without reasoning","careful subject, with reasoning",
                 'excuse stated: "nothing anyone could have done"',
                 "excuse stated, no change (within 0.02): ring around the point"],
         handler_map={tuple: HandlerTuple(ndivide=1, pad=0)},
         loc="upper center",bbox_to_anchor=(0.45,-0.095),fontsize=9,frameon=False)
keyB=[Patch(fc="#C6EFCE",ec="#BBBBBB",label="Within one noise band\nof blameless"),
      Patch(fc="#FFEB9C",ec="#BBBBBB",label="One to three\nnoise bands"),
      Patch(fc="#FFD6D6",ec="#BBBBBB",label="Beyond three\nnoise bands")]
fig.legend(handles=keyB,title="Background",loc="center left",bbox_to_anchor=(0.845,0.55),fontsize=9.5,title_fontsize=10,
           frameon=False,labelspacing=1.2,handlelength=1.6,handleheight=1.3,alignment="left")
fig.tight_layout(rect=(0,0,0.84,1))
for ext in ("png","pdf","svg"):
    fig.savefig(OUT+f"Figure2_fault_blindness.{ext}",dpi=300,bbox_inches="tight")
print(len(A),len(rows),len(off),len(on))
