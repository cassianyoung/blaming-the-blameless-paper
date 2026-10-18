import os
DATA = os.environ.get("FIGURE_DATA", os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")) + "/"
OUT = os.environ.get("FIGURE_OUT", os.path.join(os.path.dirname(os.path.abspath(__file__)), "out")) + "/"
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch
# Mistral-Small-24B, run 214, log-prob, bicycle, from results db sha 9b892c64...
N, P0, C, I = 0.2444682, 3.9020844, 6.6974938, 8.9945
pos=(P0-N)/(C-N)
plt.rcParams["font.family"]="DejaVu Sans"
fig,ax=plt.subplots(figsize=(10,6.2)); ax.set_xlim(-0.8,9.8); ax.set_ylim(-5.4,3.2); ax.axis("off")
ink="#222222"; grey="#888888"
col={"N":"#2E7D32","P0":"#C0392B","C":"#B26A00","I":"#5B2C83"}
y0=1.0
ax.add_patch(FancyBboxPatch((0,y0-0.18),9,0.36,boxstyle="round,pad=0,rounding_size=0.05",fc="#F2F2F2",ec=grey,lw=1))
for t in range(10):
    ax.plot([t,t],[y0-0.18,y0-0.30],color=grey,lw=1); ax.text(t,y0-0.52,str(t),ha="center",va="center",fontsize=10,color=grey)
ax.text(-0.75,y0,"Blame\n(0–9)",ha="left",va="center",fontsize=10,color=ink)
marks=[("N",N,"blameless case\n(careful, no harm)"),("P0",P0,"target case\n(careful, hidden flaw, harm)"),
       ("C",C,"careless case"),("I",I,"deliberate case")]
for k,x,d in marks:
    ax.plot([x,x],[y0-0.18,y0+0.55],color=col[k],lw=2)
    ax.plot(x,y0,"o",ms=9,color=col[k],mec="white",mew=1.5,zorder=5)
    ax.text(x,y0+0.85,f"{k} = {x:.2f}",ha="center",va="bottom",fontsize=11,fontweight="bold",color=col[k])
    ax.text(x,y0+1.25,d,ha="center",va="bottom",fontsize=8.5,color=ink)
def bracket(x1,x2,y,lab,c):
    ax.plot([x1,x1,x2,x2],[y+0.12,y,y,y+0.12],color=c,lw=1.5); ax.text((x1+x2)/2,y-0.28,lab,ha="center",va="top",fontsize=10.5,color=c)
bracket(N,P0,-0.35,f"P0 − N = {P0-N:.2f}",col["P0"]); bracket(N,C,-1.25,f"C − N = {C-N:.2f}",col["C"])
ax.text(4.5,-2.35,r"position of P0  $=\ \dfrac{P0 - N}{C - N}\ =\ \dfrac{%.2f}{%.2f}\ =\ %.2f$"%(P0-N,C-N,pos),ha="center",va="center",fontsize=14,color=ink)
y1=-4.0; L,R=N,C
for x,k in ((N,"N"),(C,"C")): ax.plot([x,x],[y0-0.62,-3.55],color=col[k],lw=0.8,ls=(0,(3,3)),alpha=0.6)
ax.plot([L,R],[y1,y1],color=ink,lw=2)
for v in (0,0.25,0.5,0.75,1.0):
    x=L+v*(R-L); ax.plot([x,x],[y1-0.10,y1+0.10],color=ink,lw=1.2); ax.text(x,y1-0.40,f"{v:g}",ha="center",va="center",fontsize=10,color=ink)
ax.text(L,y1+0.40,"0 = treated as blameless (N)",ha="left",va="bottom",fontsize=9,color=col["N"])
ax.text(R,y1+0.40,"1 = treated as careless (C)",ha="right",va="bottom",fontsize=9,color=col["C"])
xp=L+pos*(R-L); ax.plot(xp,y1,"o",ms=11,color=col["P0"],mec="white",mew=1.5,zorder=5)
ax.annotate(f"P0 at {pos:.2f}",(xp,y1),xytext=(xp,y1-1.0),ha="center",fontsize=11,fontweight="bold",color=col["P0"],arrowprops=dict(arrowstyle="-",color=col["P0"],lw=1))
ax.text(-0.75,y1,"Model's own\nscale",ha="left",va="center",fontsize=10,color=ink)
fig.tight_layout()
for e in ("png","pdf","svg"): fig.savefig(OUT+f"Figure_measuring_the_effect.{e}",dpi=300,bbox_inches="tight")
print(round(pos,4))
