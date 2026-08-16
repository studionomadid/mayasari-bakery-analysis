# M20.5 — Customer × Product Strategy & Cross-Sell Analysis

> **Purpose:** identify segment-specific product priorities and cross-product opportunities from observed customer purchase behavior.

## 1. Executive Summary

This analysis combines customer-product affinity with cross-product co-purchase analysis to identify where Mayasari Bakery can prioritize products, segment-specific commercial actions, and bundle/cross-sell opportunities.

The analysis is **descriptive and prioritization-oriented**. Affinity, lift, and opportunity scores are analytical ranking tools and should not be interpreted as causal models.

### Key Findings

- **Corporate priority:** Birthday Cake is the strongest product-level priority for Corporate customers, with 52.2% segment penetration and Rp 22,846,250 revenue.
- **Corporate cross-sell:** Donat Cokelat + Kue Sus is the strongest cross-sell opportunity by the composite opportunity score (0.858) with 82.6% of Corporate customers purchasing both products.
- **Strongest association:** Nastar + Paket Hampers Mini in Corporate has the highest observed lift (1.259), indicating co-purchase is stronger than the segment-level independence baseline.
- **Broad cross-sell base:** 282 segment-product pairs have at least 60% pair penetration, suggesting that several cross-sell recommendations can be positioned as bundles or basket-expansion prompts rather than narrow niche recommendations.
- **Interpretation guardrail:** co-purchase association is descriptive. Lift and opportunity scores identify commercially useful patterns but do not establish causality, customer preference mechanisms, or incremental sales impact.

## 2. Analytical Framework

### Customer × Product Affinity

Affinity score combines product penetration within a customer segment with the product's revenue contribution inside that segment:

`Affinity Score = Penetration % × Revenue Share % / 100`

This favors products that are both broadly adopted by the segment and economically important.

### Product-Pair Cross-Sell

Cross-product opportunity combines pair penetration, lift, and symmetric conditional purchase strength:

`Opportunity Score = Support × Lift × Conditional Score`

Lift compares observed co-purchase against the expected co-purchase under an independence assumption:

`Lift = Observed Pair Customers / Expected Pair Customers`

Lift > 1 indicates that the pair occurs more often than would be expected from the individual product penetration rates within the segment.

## 3. Segment Overview

| Segment | Customers | Top Product | Penetration | Revenue | Affinity | Top Cross-Sell | Pair Penetration | Lift |
|---|---:|---|---:|---:|---:|---|---:|---:|
| Corporate | 46 | Birthday Cake | 52.2% | Rp 22,846,250 | 8.631 | Donat Cokelat + Kue Sus | 82.6% | 1.093 |
| Loyal | 159 | Birthday Cake | 40.9% | Rp 22,443,750 | 6.015 | Croissant Butter + Bolen Pisang | 70.4% | 1.038 |
| Occasional | 233 | Birthday Cake | 35.6% | Rp 22,863,750 | 4.717 | Roti Cokelat + Croissant Butter | 63.1% | 1.043 |
| Regular | 412 | Birthday Cake | 30.1% | Rp 35,997,500 | 3.630 | Roti Manis + Donat Gula | 65.0% | 1.040 |

## 4. Segment Product Priorities

### Corporate

The leading product priority is **Birthday Cake**, with 52.2% penetration, Rp 22,846,250 revenue, and 8.631 affinity score.

| Rank | Product | Category | Penetration | Revenue | Gross Profit | Affinity | Priority |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | Birthday Cake | Cake | 52.2% | Rp 22,846,250 | Rp 9,028,250 | 8.631 | 184.685 |
| 2 | Brownies Box | Cake | 76.1% | Rp 12,665,250 | Rp 5,525,250 | 6.978 | 56.758 |
| 3 | Paket Snack Box | Snack Box | 87.0% | Rp 10,669,750 | Rp 3,843,250 | 6.718 | 40.282 |
| 4 | Chiffon Cake | Cake | 69.6% | Rp 8,758,750 | Rp 3,799,750 | 4.412 | 27.145 |
| 5 | Paket Hampers Mini | Hampers | 50.0% | Rp 7,565,000 | Rp 2,715,000 | 2.739 | 20.250 |
| 6 | Nastar | Cookies | 58.7% | Rp 6,261,600 | Rp 2,736,600 | 2.661 | 13.873 |
| 7 | Cookies Choco Chip | Cookies | 82.6% | Rp 4,807,600 | Rp 2,154,100 | 2.876 | 8.178 |
| 8 | Brownies Slice | Cake | 89.1% | Rp 4,271,250 | Rp 1,892,250 | 2.757 | 6.455 |
| 9 | Bolen Pisang | Pastry | 91.3% | Rp 4,191,000 | Rp 1,734,000 | 2.771 | 6.215 |
| 10 | Croissant Cokelat | Pastry | 82.6% | Rp 4,117,600 | Rp 1,780,100 | 2.463 | 5.999 |

### Loyal

The leading product priority is **Birthday Cake**, with 40.9% penetration, Rp 22,443,750 revenue, and 6.015 affinity score.

| Rank | Product | Category | Penetration | Revenue | Gross Profit | Affinity | Priority |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | Birthday Cake | Cake | 40.9% | Rp 22,443,750 | Rp 9,507,750 | 6.015 | 46.684 |
| 2 | Brownies Box | Cake | 62.9% | Rp 13,819,000 | Rp 6,373,000 | 5.697 | 17.698 |
| 3 | Paket Hampers Mini | Hampers | 40.3% | Rp 10,871,500 | Rp 4,271,500 | 2.869 | 10.953 |
| 4 | Paket Snack Box | Snack Box | 65.4% | Rp 9,177,000 | Rp 3,683,000 | 3.935 | 7.805 |
| 5 | Chiffon Cake | Cake | 48.4% | Rp 8,351,750 | Rp 3,827,750 | 2.651 | 6.464 |
| 6 | Nastar | Cookies | 45.9% | Rp 6,645,600 | Rp 3,095,600 | 2.000 | 4.093 |
| 7 | Cookies Choco Chip | Cookies | 58.5% | Rp 6,252,400 | Rp 2,917,400 | 2.397 | 3.623 |
| 8 | Kastengel | Cookies | 40.3% | Rp 5,339,250 | Rp 2,435,250 | 1.409 | 2.642 |
| 9 | Brownies Slice | Cake | 76.1% | Rp 5,130,750 | Rp 2,377,350 | 2.560 | 2.440 |
| 10 | Croissant Cokelat | Pastry | 71.1% | Rp 5,096,000 | Rp 2,325,000 | 2.374 | 2.407 |

### Occasional

The leading product priority is **Birthday Cake**, with 35.6% penetration, Rp 22,863,750 revenue, and 4.717 affinity score.

| Rank | Product | Category | Penetration | Revenue | Gross Profit | Affinity | Priority |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | Birthday Cake | Cake | 35.6% | Rp 22,863,750 | Rp 9,633,750 | 4.717 | 29.209 |
| 2 | Paket Hampers Mini | Hampers | 41.6% | Rp 15,482,750 | Rp 6,132,750 | 3.733 | 13.394 |
| 3 | Brownies Box | Cake | 48.5% | Rp 15,187,250 | Rp 6,993,250 | 4.266 | 12.888 |
| 4 | Chiffon Cake | Cake | 49.8% | Rp 11,258,500 | Rp 5,197,500 | 3.246 | 7.082 |
| 5 | Paket Snack Box | Snack Box | 59.2% | Rp 10,354,750 | Rp 4,102,250 | 3.552 | 5.991 |
| 6 | Kastengel | Cookies | 35.6% | Rp 6,682,500 | Rp 3,010,500 | 1.379 | 2.495 |
| 7 | Nastar | Cookies | 37.3% | Rp 6,542,400 | Rp 3,067,400 | 1.415 | 2.392 |
| 8 | Croissant Cokelat | Pastry | 71.2% | Rp 6,020,000 | Rp 2,739,000 | 2.484 | 2.025 |
| 9 | Cookies Choco Chip | Cookies | 50.6% | Rp 6,018,600 | Rp 2,814,100 | 1.765 | 2.024 |
| 10 | Bolen Pisang | Pastry | 80.7% | Rp 5,865,600 | Rp 2,589,600 | 2.741 | 1.922 |

### Regular

The leading product priority is **Birthday Cake**, with 30.1% penetration, Rp 35,997,500 revenue, and 3.630 affinity score.

| Rank | Product | Category | Penetration | Revenue | Gross Profit | Affinity | Priority |
|---:|---|---|---:|---:|---:|---:|---:|
| 1 | Birthday Cake | Cake | 30.1% | Rp 35,997,500 | Rp 15,221,500 | 3.630 | 23.686 |
| 2 | Brownies Box | Cake | 50.0% | Rp 24,553,750 | Rp 11,361,750 | 4.113 | 11.020 |
| 3 | Paket Hampers Mini | Hampers | 37.9% | Rp 24,084,750 | Rp 9,484,750 | 3.055 | 10.603 |
| 4 | Paket Snack Box | Snack Box | 60.9% | Rp 20,452,250 | Rp 8,172,750 | 4.174 | 7.646 |
| 5 | Chiffon Cake | Cake | 43.9% | Rp 17,143,500 | Rp 7,805,500 | 2.523 | 5.372 |
| 6 | Nastar | Cookies | 36.7% | Rp 13,192,800 | Rp 6,092,800 | 1.620 | 3.181 |
| 7 | Kastengel | Cookies | 42.2% | Rp 12,721,500 | Rp 5,737,500 | 1.800 | 2.958 |
| 8 | Cookies Choco Chip | Cookies | 51.7% | Rp 11,781,000 | Rp 5,459,000 | 2.041 | 2.537 |
| 9 | Croissant Cokelat | Pastry | 68.2% | Rp 9,927,200 | Rp 4,504,200 | 2.268 | 1.801 |
| 10 | Brownies Slice | Cake | 71.8% | Rp 9,562,500 | Rp 4,430,100 | 2.302 | 1.671 |

## 5. Cross-Sell Opportunities

### Corporate

The highest-ranked cross-sell opportunity is **Donat Cokelat + Kue Sus**, observed among 38 customers (82.6% of the segment) with lift 1.093.

| Rank | Product A | Product B | Customers | Penetration | P(B\|A) | P(A\|B) | Lift | Opportunity |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Donat Cokelat | Kue Sus | 38 | 82.6% | 97.4% | 92.7% | 1.093 | 0.858 |
| 2 | Bolen Pisang | Brownies Slice | 39 | 84.8% | 92.9% | 95.1% | 1.042 | 0.830 |
| 3 | Roti Cokelat | Brownies Slice | 39 | 84.8% | 90.7% | 95.1% | 1.018 | 0.802 |
| 4 | Bolen Pisang | Bolen Cokelat | 37 | 80.4% | 88.1% | 97.4% | 1.066 | 0.795 |
| 5 | Roti Cokelat | Donat Gula | 39 | 84.8% | 90.7% | 92.9% | 0.993 | 0.773 |
| 6 | Roti Cokelat | Bolen Pisang | 39 | 84.8% | 90.7% | 92.9% | 0.993 | 0.773 |
| 7 | Roti Sosis | Bolen Pisang | 37 | 80.4% | 94.9% | 88.1% | 1.039 | 0.765 |
| 8 | Kue Sus | Klepon | 36 | 78.3% | 87.8% | 94.7% | 1.063 | 0.759 |
| 9 | Roti Keju | Risoles | 36 | 78.3% | 92.3% | 90.0% | 1.062 | 0.757 |
| 10 | Lemper Ayam | Paket Snack Box | 36 | 78.3% | 92.3% | 90.0% | 1.062 | 0.757 |

### Loyal

The highest-ranked cross-sell opportunity is **Croissant Butter + Bolen Pisang**, observed among 112 customers (70.4% of the segment) with lift 1.038.

| Rank | Product A | Product B | Customers | Penetration | P(B\|A) | P(A\|B) | Lift | Opportunity |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Croissant Butter | Bolen Pisang | 112 | 70.4% | 86.2% | 84.8% | 1.038 | 0.625 |
| 2 | Roti Keju | Donat Gula | 108 | 67.9% | 86.4% | 83.7% | 1.065 | 0.615 |
| 3 | Roti Manis | Croissant Cokelat | 104 | 65.4% | 78.2% | 92.0% | 1.100 | 0.613 |
| 4 | Roti Cokelat | Roti Keju | 109 | 68.6% | 82.0% | 87.2% | 1.042 | 0.604 |
| 5 | Roti Manis | Croissant Butter | 111 | 69.8% | 83.5% | 85.4% | 1.021 | 0.602 |
| 6 | Roti Manis | Brownies Slice | 106 | 66.7% | 79.7% | 87.6% | 1.047 | 0.584 |
| 7 | Donat Gula | Bolen Pisang | 109 | 68.6% | 84.5% | 82.6% | 1.018 | 0.583 |
| 8 | Roti Manis | Donat Gula | 109 | 68.6% | 82.0% | 84.5% | 1.010 | 0.576 |
| 9 | Roti Manis | Bolen Pisang | 110 | 69.2% | 82.7% | 83.3% | 0.996 | 0.572 |
| 10 | Roti Manis | Roti Keju | 107 | 67.3% | 80.5% | 85.6% | 1.023 | 0.572 |

### Occasional

The highest-ranked cross-sell opportunity is **Roti Cokelat + Croissant Butter**, observed among 147 customers (63.1% of the segment) with lift 1.043.

| Rank | Product A | Product B | Customers | Penetration | P(B\|A) | P(A\|B) | Lift | Opportunity |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Roti Cokelat | Croissant Butter | 147 | 63.1% | 77.0% | 85.5% | 1.043 | 0.534 |
| 2 | Donat Gula | Bolen Pisang | 150 | 64.4% | 82.4% | 79.8% | 1.021 | 0.533 |
| 3 | Roti Cokelat | Donat Cokelat | 144 | 61.8% | 75.4% | 86.7% | 1.058 | 0.530 |
| 4 | Roti Cokelat | Bolen Pisang | 153 | 65.7% | 80.1% | 81.4% | 0.993 | 0.526 |
| 5 | Roti Manis | Roti Cokelat | 147 | 63.1% | 82.6% | 77.0% | 1.007 | 0.507 |
| 6 | Roti Cokelat | Donat Gula | 148 | 63.5% | 77.5% | 81.3% | 0.992 | 0.500 |
| 7 | Donat Gula | Kue Sus | 134 | 57.5% | 73.6% | 84.3% | 1.079 | 0.490 |
| 8 | Roti Manis | Bolen Pisang | 144 | 61.8% | 80.9% | 76.6% | 1.003 | 0.488 |
| 9 | Croissant Butter | Bolen Pisang | 140 | 60.1% | 81.4% | 74.5% | 1.009 | 0.472 |
| 10 | Roti Keju | Bolen Pisang | 137 | 58.8% | 83.0% | 72.9% | 1.029 | 0.472 |

### Regular

The highest-ranked cross-sell opportunity is **Roti Manis + Donat Gula**, observed among 268 customers (65.0% of the segment) with lift 1.040.

| Rank | Product A | Product B | Customers | Penetration | P(B\|A) | P(A\|B) | Lift | Opportunity |
|---:|---|---|---:|---:|---:|---:|---:|---:|
| 1 | Roti Manis | Donat Gula | 268 | 65.0% | 84.5% | 80.0% | 1.040 | 0.556 |
| 2 | Roti Cokelat | Donat Gula | 268 | 65.0% | 83.2% | 80.0% | 1.024 | 0.543 |
| 3 | Donat Gula | Bolen Pisang | 255 | 61.9% | 76.1% | 81.2% | 0.999 | 0.486 |
| 4 | Donat Gula | Kue Sus | 244 | 59.2% | 72.8% | 84.4% | 1.038 | 0.484 |
| 5 | Roti Keju | Donat Gula | 246 | 59.7% | 82.8% | 73.4% | 1.019 | 0.475 |
| 6 | Roti Manis | Roti Cokelat | 249 | 60.4% | 78.5% | 77.3% | 1.005 | 0.473 |
| 7 | Roti Cokelat | Bolen Pisang | 247 | 60.0% | 76.7% | 78.7% | 1.006 | 0.469 |
| 8 | Roti Manis | Brownies Slice | 237 | 57.5% | 74.8% | 80.1% | 1.041 | 0.463 |
| 9 | Roti Cokelat | Roti Keju | 238 | 57.8% | 73.9% | 80.1% | 1.025 | 0.456 |
| 10 | Donat Gula | Donat Cokelat | 244 | 59.2% | 72.8% | 81.1% | 0.997 | 0.454 |

## 6. Corporate Commercial Priority

Corporate is the smallest customer segment in the dataset, but its product economics and concentrated purchase behavior make it particularly useful for targeted commercial programs.

Recommended product priorities:

- **Birthday Cake** — penetration 52.2%, revenue Rp 22,846,250, gross margin 39.5%, priority score 184.685.
- **Brownies Box** — penetration 76.1%, revenue Rp 12,665,250, gross margin 43.6%, priority score 56.758.
- **Paket Snack Box** — penetration 87.0%, revenue Rp 10,669,750, gross margin 36.0%, priority score 40.282.
- **Chiffon Cake** — penetration 69.6%, revenue Rp 8,758,750, gross margin 43.4%, priority score 27.145.
- **Paket Hampers Mini** — penetration 50.0%, revenue Rp 7,565,000, gross margin 35.9%, priority score 20.250.

Recommended cross-sell candidates:

- **Donat Cokelat + Kue Sus** — 38 shared customers, pair penetration 82.6%, lift 1.093, opportunity score 0.858.
- **Bolen Pisang + Brownies Slice** — 39 shared customers, pair penetration 84.8%, lift 1.042, opportunity score 0.830.
- **Roti Cokelat + Brownies Slice** — 39 shared customers, pair penetration 84.8%, lift 1.018, opportunity score 0.802.
- **Bolen Pisang + Bolen Cokelat** — 37 shared customers, pair penetration 80.4%, lift 1.066, opportunity score 0.795.
- **Roti Cokelat + Donat Gula** — 39 shared customers, pair penetration 84.8%, lift 0.993, opportunity score 0.773.

## 7. Recommended Business Actions

### A. Build segment-specific bundles

Use high-support, high-opportunity product pairs as candidate bundles. The strongest candidates should be tested with controlled pricing and promotion rather than immediately treated as proven incremental-sales drivers.

### B. Prioritize Corporate for targeted offers

Corporate customers show concentrated product behavior. Use high-affinity products as anchor SKUs and attach high-lift or high-support complementary products as cross-sell recommendations.

### C. Use high-penetration products as anchors

Products with broad segment penetration can serve as entry points for bundle construction because the customer base already demonstrates familiarity with them.

### D. Test bundle economics

Before deployment, evaluate bundle gross margin, discount depth, cannibalization risk, and incremental conversion. The current analysis identifies associations but does not measure incremental uplift.

### E. Operationalize recommendations

The resulting priority tables can be translated into CRM segments, product recommendations, campaign rules, bundle candidates, or POS cross-sell prompts.

## 8. Limitations

- Product-pair analysis is based on observed customer co-purchase behavior.
- Association does not establish causality.
- Lift can become unstable for low-support pairs; a minimum pair-customer threshold was therefore applied upstream.
- Opportunity scores are analytical prioritization metrics rather than machine-learning predictions.
- No A/B test or counterfactual analysis is performed.
- Bundle recommendations should be validated against actual incremental revenue and gross profit.

## 9. Output Artifacts

- `data/processed/m20_5_segment_product_priorities.parquet` — segment-level product priority dataset.
- `data/processed/m20_5_cross_sell_priorities.parquet` — cross-product opportunity dataset.
- `reports/m20_5_customer_product_strategy.md` — synthesized strategic report.

## 10. Validation

Chunk 6 validates the persisted Chunk 4 and Chunk 5 datasets, explicitly rebuilds ranking metrics, verifies segment coverage, and writes reproducible parquet outputs.

**Validation status: PASS**
