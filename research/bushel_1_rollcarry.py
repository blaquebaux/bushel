#!/usr/bin/python3
# =============================================================================
# bushel_1_rollcarry.py — can a regime gate turn the VIX roll-carry into a keeper, or is it still a landmine?
#
# Harvest = SHORT the front-month VIX ETF (−VIXY): you earn the contango roll-down. Raw, it's the brace
# landmine (huge negative skew, catastrophic Feb-2018/Mar-2020). Two causal gates try to tame it:
#   VOL-REGIME: harvest only when SPY 21d realized vol is BELOW its 1y median (calm = contango-prone).
#   TERM-STRUCTURE: harvest only when the mid-term (VIXM) is OUTPERFORMING the front (VIXY) over 20d —
#                   i.e. the front is decaying faster (steep contango); step aside when it inverts (stress).
# Both lagged one day. The real test is the TAIL: skew / exKurt / maxDD — a daily gate can't dodge an
# overnight vol gap, so does the premium survive the crashes it's structurally short?  SVXY = real-vehicle check.
# =============================================================================
import os, sys; sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _bushel_common import panel, rets, lag, riskadj, stats
import numpy as np

P, dates = panel(["VIXY", "VIXM", "SVXY", "SPY"])
R = {s: rets(P[s]) for s in P}
spy = R["SPY"]; n = len(spy)
harvest = -R["VIXY"]                         # short the front-month VIX ETF = the roll-carry harvest (gross, 1x)

# ---- gates (causal) ---------------------------------------------------------------------------------
rv21 = np.array([spy[max(0,t-21):t].std()*np.sqrt(252) if t>21 else np.nan for t in range(n)])
med  = np.array([np.nanmedian(rv21[max(0,t-252):t]) if t>60 else np.nan for t in range(n)])
vol_on = lag((rv21 <= med).astype(float))                                   # calm regime, lagged
# term structure: 20d return of VIXM vs VIXY (mid outperforming front = steep contango)
def roc(a,k): o=np.full(len(a),np.nan); o[k:]=a[k:]/a[:-k]-1; return o
ts_sig = roc(P["VIXM"],20)[1:] - roc(P["VIXY"],20)[1:]                       # aligned to returns (len n)
ts_on  = lag((ts_sig > 0).astype(float))

gated_vol = harvest * vol_on
gated_ts  = harvest * ts_on
gated_both= harvest * vol_on * ts_on

print("="*96); print(f"BUSHEL #1 — VIX roll-carry, raw vs gated  ({dates[0]} → {dates[-1]}, {n} days)"); print("="*96)
print(f"\n  {'book':24}{'Sharpe':>8}{'CAGR':>8}{'maxDD':>9}{'skew':>7}{'exKurt':>8}{'%in':>6}")
def row(nm, r, onmask=None):
    a=riskadj(r, spy); pin = (np.mean(onmask[np.isfinite(onmask)])*100 if onmask is not None else 100)
    print(f"  {nm:24}{a['sh']:>+8.2f}{a['cagr']*100:>+7.0f}%{a['dd']*100:>+8.0f}%{a['skew']:>+7.2f}{a['exkurt']:>+8.1f}{pin:>5.0f}%")
    return a
a_raw = row("raw harvest (−VIXY)", harvest)
row("SVXY (real vehicle)", R["SVXY"])
a_vol = row("gated: vol-regime", gated_vol, vol_on)
a_ts  = row("gated: term-structure", gated_ts, ts_on)
a_bo  = row("gated: both", gated_both, vol_on*ts_on)

# crisis: worst-5% SPY days — does the harvest get smashed exactly when SPY falls?
crash = spy <= np.percentile(spy,5)
print(f"\n  on SPY's worst-5% days — mean return:  raw {harvest[crash].mean()*100:+.1f}%   vol-gated {gated_vol[crash].mean()*100:+.1f}%   both {gated_both[crash].mean()*100:+.1f}%   (SPY {spy[crash].mean()*100:+.1f}%)")

best = max([("vol-regime",a_vol),("term-structure",a_ts),("both",a_bo)], key=lambda x:x[1]['sh'])
clean_tail = best[1]['skew'] > -1.5 and best[1]['dd'] > -0.35
if best[1]['sh']>0.7 and clean_tail: v=f"KEEPER-ish: the {best[0]} gate tames the roll-carry (Sharpe {best[1]['sh']:+.2f}, maxDD {best[1]['dd']*100:.0f}%, skew {best[1]['skew']:+.2f}) — a disciplined contango harvest, the sell-side done right. Pairs NEGATIVELY with the tail sleeve."
elif best[1]['sh']>0.5: v=f"CONDITIONAL: the {best[0]} gate lifts Sharpe to {best[1]['sh']:+.2f} and shrinks the crater, but the skew ({best[1]['skew']:+.2f}) / maxDD ({best[1]['dd']*100:.0f}%) is still an insurer's tail — size it small as what it is: selling vol."
else: v=f"NULL-ish: even gated, the roll-carry keeps a ruinous left tail (best Sharpe {best[1]['sh']:+.2f}, skew {best[1]['skew']:+.2f}) — a daily gate can't dodge the overnight vol gap it's short. brace's verdict stands; this is insurance-selling, not alpha."
print(f"\n  VERDICT: {v}")
print("  (The honest frame: bushel is the MIRROR of bleed/TAIL — it earns the calm and pays the crash. Whether the")
print("   gate makes it a keeper or just a smaller landmine is a skew/maxDD question, not a Sharpe one.)")
