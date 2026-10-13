# NimbusAI GPU FinOps Write-up

## Baseline and optimized result

Monthly baseline spend is $27,133. Optimized spend is $14,549. Total savings are $12,584, or 46.4%. Inference cost falls from $6.488 to $1.126 per 1M tokens. Inference savings are 82.6%.

## Main findings

The largest monthly lever is purchasing at $10,117. Spot fits interruptible jobs because checkpoint rework is cheaper than on-demand. Reserved fits steady jobs above the 55% utilization break-even point.

`gpu-h100-4` reports 98.2% GPU-Util but only 0.194 MFU. GPU-Util shows active clocks, not useful FLOPs. Memory stalls, I/O waits, or inefficient kernels can keep a GPU busy while throughput stays low. Its cost impact supports right-sizing. A10G also meets the lie rule.

M1 idle waste is $600 per month, or 2.2% of baseline spend. M2 cascade contributes the largest incremental inference saving at $37.40 per day. Batch contributes $1.79 per day and cache contributes $1.20 per day. Batch should not serve latency-sensitive requests.

M3 recommends spot for interruptible training and evaluation jobs. Effective hours include checkpoint overhead and expected rework after interruptions. Reserved fits continuous inference jobs. M4 shows assistant as the largest team at 30.6% of tagged cost. Tag coverage is 92%, so chargeback is ready. FOCUS normalizes cost fields across cloud providers.

## Extensions completed

Extension 1 adds GPU-specific spot interruption rates and selects one-year reserved rates for jobs shorter than 30 days. The policy changes spot estimates for five jobs in this dataset. It captures interruption risk and avoids treating a short job as a three-year commitment.

Extension 5 estimates energy from catalog watts and actual interruptible-job duration. Moving those jobs from us-east-1 to europe-north1 reduces carbon by 626,150 gCO2e, or 92.1%. This is a carbon estimate, not a latency or transfer-cost decision.

## Recommended actions

1. Right-size flagged GPUs and stop idle capacity.
2. Route easy requests to small models, then add cache and batch controls.
3. Enforce team and project tags before chargeback, then schedule interruptible jobs in low-carbon regions when latency allows.

## Manual actions

No photos or screenshots are required by the guide. Optional manual review: open `outputs/savings.png`, inspect `outputs/report.md`, and confirm `outputs/focus_export.csv` before submission.
