# Blaque Baux Bushel

**VIX term-structure roll-carry — harvest the contango, gated. The sell-side of volatility, where the tail is the whole story.**

Bushel is a member of the Blaque Baux family. It harvests the **contango** the VIX futures curve usually sits in —
front-month vol rolls down to a lower spot, so the short side earns the roll — but *gated*, so you're not short vol
into a spike. It's the disciplined counterpart to `brace` (which found naive short-vol is the insurer's side) and
the **mirror of bleed / the TAIL sleeve** (bushel earns the calm and pays the crash; they earn the crash).

> **Not investment advice.** Educational/research software. See [DISCLAIMER](DISCLAIMER.md) and [LICENSE](LICENSE).

```bash
python3 research/bushel_1_rollcarry.py   # needs Alpaca data keys in the environment
```

## The finding (honest)

[`research/bushel_1_rollcarry.py`](research/bushel_1_rollcarry.py) — 2016→2026, SIP daily. Harvest = short the
front-month VIX ETF (−VIXY); two causal gates (vol-regime, term-structure) try to tame it:

| book | Sharpe | CAGR | maxDD | skew | exKurt |
|------|--------|------|-------|------|--------|
| raw harvest (−VIXY) | +0.58 | +15% | **−92%** | −1.83 | +10 |
| SVXY (real vehicle) | +0.41 | +2% | **−95%** | **−7.9** | **+175** |
| gated: vol-regime | +0.35 | +6% | −58% | −1.85 | +13 |
| **gated: term-structure** | **+0.52** | +13% | **−64%** | −2.2 | +14 |
| gated: both (over-gated) | −0.01 | −8% | −75% | −2.8 | +21 |

On SPY's worst-5% days the raw harvest loses **−10.8%/day**; the term-structure gate cuts that to **−3.1%**
(vs SPY −2.7%). So **gating shrinks the crater — but not the structural short-vol tail**: skew stays ~−2.2 and
drawdown −64%, because a daily gate can't react to an overnight vol gap it is short.

## Verdict

**CONDITIONAL — a *smaller* landmine, not a clean keeper.** The roll-carry is real and the term-structure gate is
the best discipline (Sharpe +0.52, a far shallower crater, crash-days a third as bad), but it remains
**insurance-selling, not alpha**. It ships only as a **tiny, disclosed, sized-as-risk** position, and only paired
with the buy-side tail it mirrors. `brace`'s law — short-vol is the insurer's side — holds from the term-structure
angle too. (Term-structure signal uses VIXY/VIXM ETF proxies; a cleaner VIX-futures-curve feed is a `bushel_2`.)

## Status
**Research — conditional; a risk-budgeted carry at best, the honest sell-side of vol.** No live rail by default.

## Layout
```
research/  _bushel_common.py       — bars + fat-tail toolkit
           bushel_1_rollcarry.py   — raw vs vol-gated vs term-structure-gated roll-carry
```

## The Blaque Baux family
One sleeve of the **Blaque Baux** family. The [core repo](https://github.com/blaquebaux/base) is the
base/blueprint and holds the [full family roster](https://github.com/blaquebaux/base#the-blaquebaux-family).

## License
[MIT](LICENSE). (c) 2026 Carter Warrens.
