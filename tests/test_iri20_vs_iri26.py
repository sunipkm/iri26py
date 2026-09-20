# %%
"""Comparison plot between IRI-2020 (`iri20py`) and IRI-2026 (`iri26py`)
at the same point/time, both with default settings. These are genuinely
different model vintages (new topside-Te model, new B0/B1 family, IBP-2023
bubble model in 2026), so this isn't a golden test -- just a sanity check
on how far apart the two real vintages land, matching `test_iri2020.py`'s
own plotting style.
"""
from __future__ import annotations

from datetime import datetime, UTC

import matplotlib
import matplotlib.pyplot as plt
import numpy as np

from iri20py import Iri2020
from iri26py import Iri2026

matplotlib.rcParams.update({'mathtext.fontset': 'cm'})
matplotlib.rc('font', **{'family': 'serif', 'serif': ['Times New Roman']})

GLAT, GLON = 42.6, -71.2
DATE = datetime(2022, 3, 21, 12, 0, 0, tzinfo=UTC)
ALT_KM = np.arange(60, 801, 5)

_, ds20 = Iri2020().evaluate(DATE, GLAT, GLON, ALT_KM)
_, ds26 = Iri2026().evaluate(DATE, GLAT, GLON, ALT_KM)

fig, ax = plt.subplots(figsize=(6.4, 4.8), dpi=150)
tax = ax.twiny()

l20, = ds20['Ne'].plot(y='alt_km', ax=ax, color='r', lw=1.2)  # type: ignore
l26, = ds26['Ne'].plot(y='alt_km', ax=ax, color='r', lw=1.2, linestyle='--')  # type: ignore
t20, = ds20['Te'].plot(y='alt_km', ax=tax, color='k', lw=1.0)  # type: ignore
t26, = ds26['Te'].plot(y='alt_km', ax=tax, color='k', lw=1.0, linestyle='--')  # type: ignore
i20, = ds20['Ti'].plot(y='alt_km', ax=tax, color='c', lw=1.0, alpha=0.7)  # type: ignore
i26, = ds26['Ti'].plot(y='alt_km', ax=tax, color='c', lw=1.0, alpha=0.7, linestyle='--')  # type: ignore

ax.set_xscale('log')
ax.set_xlabel('$N_e$ [cm$^{-3}$]')
tax.set_xlabel('Temperature [K]')
ax.set_xlim(1e-3, None)
tax.set_xlim(100, None)
ax.set_ylabel('Altitude [km]')
ax.set_title(f'IRI-2020 (solid) vs IRI-2026 (dashed)\nLowell, MA, {DATE.isoformat()}')
ax.legend(
    [l20, l26, t20, t26, i20, i26],
    ['$N_e$ 2020', '$N_e$ 2026', '$T_e$ 2020', '$T_e$ 2026', '$T_i$ 2020', '$T_i$ 2026'],
    loc='upper left', fontsize='small',
)
fig.tight_layout()
fig.savefig('iri20_vs_iri26.png', dpi=150)
plt.show()

for name in ('Ne', 'Te', 'Ti'):
    a = ds20[name].values
    b = ds26[name].values
    mask = a > 1.0
    rel = np.abs(b[mask] - a[mask]) / np.abs(a[mask])
    print(f"{name}: median rel diff {np.median(rel):.3f}, max {rel.max():.3f}")
print("2020 nmF2/hmF2:", ds20.attrs.get('nmF2'), ds20.attrs.get('hmF2'))
print("2026 nmF2/hmF2:", ds26.attrs.get('nmF2'), ds26.attrs.get('hmF2'))
