# Mayasari Bakery — Sales Performance Analysis

> Reproducible analytical report generated from `data/processed/monthly_kpi.parquet`.

## Executive Summary

The 2025 sales dataset contains **13,000 transactions** and **38,602 units sold**, generating **Rp 761,804,925 in net sales**.

Gross profit reached **Rp 334,282,225** with a **43.88% gross margin**. After **Rp 167,518,730** in operating expenses, estimated operating profit was **Rp 166,763,495**, equivalent to a **21.89% operating margin**.

## Annual KPI

| KPI | Value |
|---|---:|
| Gross sales | Rp 790,613,000 |
| Discount | Rp 28,808,075 |
| Net sales | Rp 761,804,925 |
| Transactions | 13,000 |
| Units sold | 38,602 |
| Product cost | Rp 427,522,700 |
| Gross profit | Rp 334,282,225 |
| Gross margin | 43.88% |
| Operating expense | Rp 167,518,730 |
| Operating profit | Rp 166,763,495 |
| Operating margin | 21.89% |
| Discount rate | 3.64% |
| Average transaction value | Rp 58,600 |

## First-to-Last Month Movement

This section describes the movement between the first and last observed months. It is not a CAGR.

| Metric | Movement |
|---|---:|
| Net sales | +30.97% |
| Transactions | +18.65% |
| Units sold | +20.51% |
| Gross profit | +30.39% |
| Average transaction value | +10.39% |

## Monthly Performance

| Month | Net Sales | Transactions | Units | Gross Profit | Gross Margin | Operating Profit |
|---|---:|---:|---:|---:|---:|---:|
| January 2025 | Rp 59,493,475 | 1,019 | 3,067 | Rp 26,036,675 | 43.76% | Rp 11,305,914 |
| February 2025 | Rp 57,073,225 | 941 | 2,898 | Rp 24,864,925 | 43.57% | Rp 11,271,183 |
| March 2025 | Rp 66,694,775 | 1,149 | 3,373 | Rp 29,272,675 | 43.89% | Rp 15,534,207 |
| April 2025 | Rp 68,770,675 | 1,095 | 3,270 | Rp 29,954,575 | 43.56% | Rp 15,384,764 |
| May 2025 | Rp 64,480,075 | 1,083 | 3,209 | Rp 28,469,775 | 44.15% | Rp 14,608,743 |
| June 2025 | Rp 60,030,800 | 1,117 | 3,198 | Rp 26,412,400 | 44.00% | Rp 12,700,640 |
| July 2025 | Rp 60,665,775 | 1,140 | 3,279 | Rp 26,815,475 | 44.20% | Rp 13,585,282 |
| August 2025 | Rp 63,309,250 | 1,065 | 3,268 | Rp 27,717,750 | 43.78% | Rp 13,938,518 |
| September 2025 | Rp 63,365,275 | 1,112 | 3,196 | Rp 27,870,675 | 43.98% | Rp 13,642,410 |
| October 2025 | Rp 58,382,700 | 1,070 | 3,063 | Rp 25,845,400 | 44.27% | Rp 11,368,041 |
| November 2025 | Rp 61,620,100 | 1,000 | 3,085 | Rp 27,073,800 | 43.94% | Rp 13,987,848 |
| December 2025 | Rp 77,918,800 | 1,209 | 3,696 | Rp 33,948,100 | 43.57% | Rp 19,435,945 |

## Monthly Rankings

### Net Sales

| Rank | Month | Net Sales |
|---:|---|---:|
| 1 | December 2025 | Rp 77,918,800 |
| 2 | April 2025 | Rp 68,770,675 |
| 3 | March 2025 | Rp 66,694,775 |
| 4 | May 2025 | Rp 64,480,075 |
| 5 | September 2025 | Rp 63,365,275 |

### Gross Profit

| Rank | Month | Gross Profit |
|---:|---|---:|
| 1 | December 2025 | Rp 33,948,100 |
| 2 | April 2025 | Rp 29,954,575 |
| 3 | March 2025 | Rp 29,272,675 |
| 4 | May 2025 | Rp 28,469,775 |
| 5 | September 2025 | Rp 27,870,675 |

### Transactions

| Rank | Month | Transactions |
|---:|---|---:|
| 1 | December 2025 | 1,209 |
| 2 | March 2025 | 1,149 |
| 3 | July 2025 | 1,140 |
| 4 | June 2025 | 1,117 |
| 5 | September 2025 | 1,112 |

### Average Transaction Value

| Rank | Month | ATV |
|---:|---|---:|
| 1 | December 2025 | Rp 64,449 |
| 2 | April 2025 | Rp 62,804 |
| 3 | November 2025 | Rp 61,620 |
| 4 | February 2025 | Rp 60,652 |
| 5 | May 2025 | Rp 59,538 |

## Descriptive Insights

- Highest net sales occurred in 2025-12 at Rp 77,918,800.
- Lowest net sales occurred in 2025-02 at Rp 57,073,225.
- Highest gross profit occurred in 2025-12 at Rp 33,948,100.
- Lowest gross profit occurred in 2025-02 at Rp 24,864,925.
- Highest average transaction value occurred in 2025-12 at Rp 64,448.97.
- Lowest average transaction value occurred in 2025-07 at Rp 53,215.59.

## Analytical Interpretation

The observed period shows positive first-to-last movement in both sales and transaction activity. Net sales increased faster than transaction volume, while average transaction value also increased. This indicates that the final observed month generated more revenue per transaction than the first observed month.

December 2025 was the strongest month across the primary sales metrics in this analysis, recording the highest net sales, gross profit, transaction count, and average transaction value.

These findings are descriptive. They identify observed patterns in the dataset and do not establish causal relationships such as seasonality, promotion effects, or changes in customer behavior.

## Data Integrity

This report uses the validated monthly KPI layer from `data/processed/monthly_kpi.parquet`. Financial reconciliation was completed in M20, including transactional sales reconciliation, expense reconciliation, derived KPI formula checks, and the final financial bridge.

## Reproducibility

Generate this report with:

```bash
python scripts/generate_sales_performance_report.py
```

Run the CLI analysis with:

```bash
python scripts/analyze_sales_performance.py
```
