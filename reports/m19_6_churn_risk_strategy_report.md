# M19.6 — Churn Risk Strategy Executive Report

> **Analysis stage:** M19.6 — Business Risk Strategy
> **Model:** `random_forest`
> **Prediction contract:** `m19.5.5`
> **Production status:** `not_production_validated`

---

## 1. Executive Summary

The M19.6 analysis evaluates how the final churn prediction contract can
be translated into a practical customer-risk screening strategy.

The evaluated population contains **120 customer-cutoff records**,
of which **31 (25.83%)** were observed as
churners.

The recommended analytical threshold is **0.25**,
which is also the existing prediction-contract baseline threshold.

At this threshold:

- High-risk screening population: **116 (96.67%)**
- Precision: **26.72%**
- Recall: **100.00%**
- Observed churn capture: **100.00%**
- False positives: **85**

The result indicates that the model is better interpreted as a
**broad recall-oriented screening mechanism** rather than a selective,
high-confidence churn list.

The evaluated threshold grid does **not** demonstrate the requested
high-precision targeting capability.

The model must therefore **not be claimed or positioned as a high-precision churn targeting model**.

---

## 2. Business Objective

The objective of M19.6 is not to retrain or replace the prediction model.

Instead, the analysis translates the existing prediction contract into
a business decision framework:

1. Determine how threshold changes affect the size of the high-risk
   population.
2. Measure the resulting trade-off between precision and recall.
3. Identify a threshold appropriate for a recall-first retention screen.
4. Establish whether the model supports high-precision customer targeting.
5. Define operational and business-risk boundaries before deployment.

The analysis therefore focuses on **decision quality and operational
interpretation**, not model optimization alone.

---

## 3. Evaluation Population

| Metric | Value |
|---|---:|
| Evaluation population | 120 |
| Actual churners | 31 |
| Observed churn rate | 25.83% |
| Model | `random_forest` |
| Prediction contract | `m19.5.5` |
| Production status | `not_production_validated` |

The observed churn labels represent evaluation outcomes. They should not
be interpreted as evidence of the causal reasons why customers churned.

---

## 4. Baseline Risk Performance

The existing prediction contract uses a baseline threshold of
**0.25**.

The M19.6 decision analysis retains this threshold for the recall-first
screening strategy.

At the baseline threshold:

- 116 customers are classified as high risk.
- 31 observed churners are captured.
- 85 customers are classified as high risk but were
  not observed to churn.
- Precision is 26.72%.
- Recall is 100.00%.

The key business implication is that **high recall is achieved at the cost
of a very broad intervention population**.

---

## 5. Threshold Sensitivity Analysis

The evaluated threshold grid contains:

`0.20, 0.25, 0.30, 0.35, 0.40, 0.45, 0.50, 0.55, 0.60, 0.65, 0.70`

As the threshold increases, the high-risk population decreases and
observed churn capture also decreases.

Two evaluated thresholds preserve 100% observed churn capture:

- **0.20**
- **0.25**

Threshold **0.25** is preferred because it preserves full observed churn
capture while producing a smaller high-risk population than threshold
0.20.

Increasing the threshold above 0.25 immediately sacrifices some observed
churn capture.

### Maximum observed precision

The highest precision observed anywhere in the evaluated grid is
**26.85%**, occurring at threshold
**0.35**.

This remains substantially below the configured precision target of
**50%**.

Therefore, the evaluated grid provides **no evidence that the current
prediction contract supports high-precision targeting**.

---

## 6. Threshold Decision

### Recommended analytical threshold

**0.25**

### Decision mode

`recall_first_broad_screening`

### Threshold strategy

`retain_baseline_threshold`

The recommendation is to **retain the existing baseline threshold** rather
than change the prediction contract.

This is a business-risk decision rather than a claim that 0.25 is a
universally optimal threshold.

The threshold is appropriate for the evaluated use case because it
maintains 100% observed churn capture within the evaluated population.

---

## 7. Recommended Risk Strategy

The final risk strategy is:

> **Use the model as a broad recall-first screening signal, not as a
> high-confidence customer-level churn declaration.**

The recommended operating posture is:

`broad_retention_screening_with_cost_awareness`

The model should therefore be used to identify customers who may warrant
further retention consideration or prioritization.

It should not be interpreted as establishing that every high-risk
customer will churn.

---

## 8. False-Positive Exposure

At the recommended threshold, the model produces:

- **85 false positives**
- **70.83% of the evaluation population**

This is the primary operational risk of the current strategy. The 85 false positives demonstrate substantial **false-positive risk** and potential operational exposure.

A broad screening population may create:

- unnecessary campaign exposure,
- higher communication costs,
- intervention capacity pressure,
- customer fatigue,
- inefficient allocation of retention incentives.

Consequently, campaign deployment should not be based on the model score
alone.

Customer value, intervention cost, campaign capacity, and expected
treatment benefit should be incorporated into any future operational
decision framework.

---

## 9. Business Interpretation

The model currently provides stronger evidence for **recall-oriented
screening** than for **selective targeting**.

The observed pattern is:

**Lower threshold → broader population → higher churn capture**

**Higher threshold → smaller population → lower churn capture**

However, increasing the threshold does not produce the required 50%
precision target within the evaluated grid.

Therefore:

- The model can support risk screening.
- The model can help prioritize customers for additional assessment.
- The model should not be presented as a high-confidence churn classifier.
- Campaign economics should be evaluated before operational deployment.

---

## 10. Operational Recommendations

### 10.1 Retain the baseline threshold for recall-first screening

The analytical recommendation is to retain threshold **0.25**.

No prediction-contract modification is required for this analytical use case.

### 10.2 Do not claim high-precision targeting

The evaluated maximum precision is only **26.85%**,
below the **50%** target.

Therefore:

`do_not_claim_high_precision_targeting`

### 10.3 Introduce business-value prioritization

Future campaign prioritization should combine churn risk with additional
business dimensions such as:

- customer lifetime value,
- expected revenue contribution,
- intervention cost,
- campaign capacity,
- historical treatment response,
- expected treatment uplift.

These dimensions are outside the current M19.6 model evaluation.

### 10.4 Treat model output as a screening signal

The appropriate interpretation is:

`screening_signal_not_customer_level_certainty`

The predicted class should not be treated as a deterministic statement
about individual customer behavior.

---

## 11. Business Decision

### Threshold decision

`retain_baseline_for_recall_first_screening`

### Campaign decision

`do_not_claim_high_precision_targeting`

The final recommendation is therefore to preserve the existing analytical
threshold while explicitly accounting for the cost of false-positive
exposure.

---

## 12. Limitations

This analysis has several important limitations.

### Evaluation population

The evaluation contains only **120 customer-cutoff records**.
Results should not automatically be generalized to all customers,
future periods, or different populations.

### Observational interpretation

Observed churn labels indicate outcomes, not causal explanations.

The model does not establish why a customer churned.

### Threshold-grid limitation

The threshold analysis covers the evaluated grid only.

Conclusions about threshold behavior are therefore specific to these
evaluated scenarios and the underlying prediction contract.

### Business economics

The current analysis does not model:

- customer lifetime value,
- campaign cost,
- intervention capacity,
- incentive cost,
- treatment uplift,
- incremental retention revenue.

### Production validation

The artifact remains:

`not_production_validated`

Therefore M19.6 does **not** establish production readiness.

---

## 13. Production Boundary

The M19.6 analysis is an analytical decision-support exercise.

The M19.6 analysis **does not establish production readiness**.

It does not:

- change the production prediction contract,
- establish production model monitoring,
- establish production data quality,
- establish model drift monitoring,
- establish causal treatment effectiveness,
- establish campaign ROI,
- establish production validation.

The production boundary remains:

> **`not_production_validated`**

Any future production deployment should require separate validation,
monitoring, governance, and business-effectiveness evaluation.

---

## 14. Final Recommendation

The recommended strategy is to **retain threshold 0.25
for recall-first analytical screening** because it preserves
**100.00% observed churn capture** on the evaluated
population.

However, the model should **not** be positioned as a high-precision churn
targeting model.

The high-risk population is broad at **116 of
120 records**, with **85 false positives**.

The model should therefore be treated as a **screening and prioritization
signal**, with final campaign decisions incorporating customer value,
intervention capacity, campaign economics, and—when available—measured
treatment uplift.

---

## 15. M19.6 Final Metrics

| Metric | Result |
|---|---:|
| Analytical threshold | 0.25 |
| High-risk population | 116 |
| High-risk rate | 96.67% |
| Precision | 26.72% |
| Recall | 100.00% |
| Churn capture | 100.00% |
| False positives | 85 |
| Maximum observed precision | 26.85% |
| Maximum precision threshold | 0.35 |
| Precision target | 50% |
| High-precision targeting | Not supported by evaluated grid |
| Production status | `not_production_validated` |

---

## 16. Source Artifacts

This report was generated from the following M19.6 artifacts:

1. `data/processed/business_risk_interpretation_m19_6_3.parquet`
2. `data/processed/threshold_sensitivity_analysis_m19_6_4.parquet`
3. `data/processed/threshold_decision_recommendation_m19_6_5.parquet`
4. `data/processed/final_risk_strategy_m19_6_6.parquet`

The report is therefore downstream of the validated M19.6 analytical
artifacts and does not independently alter their values.

---

## 17. Milestone Status

**M19.6 — Final Risk Strategy: COMPLETE**

**M19.6 — Final QA: PASS**

**M19.7.1 — Executive Report: GENERATED**

Next milestone:

**M19.7.2 — Report QA**
