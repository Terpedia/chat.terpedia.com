# Terpene search A/B report

> Synthetic RDKit proxy benchmark; not protein binding, docking, or private-harness evidence.

Library: 8,000 valid unique terpene-derived molecules.
Budget: 1,600 scoring calls per method per run.
Output: 100 unique diversity-filtered molecules.

| Proxy target | Naive mean | Evolution mean | Relative change | Paired wins |
|---:|---:|---:|---:|---:|
| 1 | 2.0239 | 2.1861 | +8.01% | 5/5 |
| 2 | 1.5830 | 1.7661 | +11.58% | 5/5 |
| 3 | 1.4733 | 1.5706 | +6.61% | 5/5 |
| 4 | 1.0100 | 1.0992 | +8.84% | 5/5 |
| 5 | 1.1441 | 1.2111 | +5.87% | 5/5 |
| 6 | 1.3299 | 1.4687 | +10.48% | 5/5 |
| 7 | 1.1355 | 1.2076 | +6.37% | 5/5 |
| 8 | 0.6308 | 0.8079 | +28.16% | 5/5 |

Overall mean relative change: **+10.74%**.
Paired wins: **40/40**.
Mean absolute delta 95% bootstrap CI: **[0.1080, 0.1387]**.

The only experimental variable is the search policy. These results demonstrate the A/B implementation; the experiment must be rerun with the private protein-ligand scorer before making efficacy claims.
