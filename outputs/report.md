# NimbusAI - GPU Cost Optimization Report

**Period:** monthly  
**Baseline spend:** $27,133  
**Optimized spend:** $14,549  
**Projected savings:** $12,584  (**46%**)

## Savings by lever

| Lever | Savings (USD) |
|---|---|
| Inference (cascade/cache/batch) | $1,212 |
| Purchasing (spot/reserved) | $10,117 |
| Right-size util-lies | $655 |
| Kill idle GPUs | $600 |

## Sustainability

- Energy per query: 0.24 Wh
- Carbon per query: 0.091 gCO2e
- Cheapest+cleanest region: europe-north1

## Extension 1: Purchasing policy

| Metric | Before | After |
|---|---:|---:|
| Optimized monthly cost | $15,627 | $15,550 |
| Purchasing savings vs on-demand | 39.1% | 39.4% |
| Jobs affected by added logic | 0 | 5 |

GPU-specific interruption rates drive spot estimates. Jobs shorter than 30 days use the one-year reserved rate. Jobs of 30 days or more use the three-year rate. This is a planning assumption, not a provider contract.
Affected jobs: job-train-llm, job-train-embed, job-finetune, job-dev-sandbox, job-batch-eval.

## Extension 5: Carbon-aware scheduling

| Metric | us-east-1 | Clean region |
|---|---:|---:|
| Region | us-east-1 | europe-north1 |
| Interruptible-job carbon | 679,820.0 gCO2e | 53,670.0 gCO2e |
| Carbon reduction | 0.0 gCO2e | 626,150.0 gCO2e (92.1%) |

Estimate uses observed job days, GPU count, catalog watts, and a 30-day month only for purchasing output. Carbon scheduling keeps job duration unchanged. Region latency and data transfer need review before migration.

_Figures are June-2026 as-of snapshots. Re-baseline before acting._