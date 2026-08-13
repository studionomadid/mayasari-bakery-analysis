# M19.9 — Business Findings & Churn Risk Interpretation

## Business Findings Report

**Status:** COMPLETE — M19.9  
**Source milestone:** M19.6 Churn Risk Strategy  
**Prediction contract:** m19.5.5  
**Model:** Random Forest  
**Production status:** Not production validated

---

## 1. Executive Summary

The M19 churn-risk model is more suitable for broad recall-first churn screening than high-precision customer targeting.

At threshold **0.25**, the evaluated population contains **120 customer-cutoff records**. The model classifies **116** customers as high-risk and captures all **31 observed churners**.

Key results:

- **100.00%** observed churn capture
- **100.00%** recall
- **26.72%** precision
- **85** false positives
- **96.67%** classified as high-risk

The model should therefore be treated as a screening signal rather than customer-level churn certainty.

---

## 2. Evaluated Business Population

| Metric | Value |
|---|---:|
| Customer-cutoff records | 120 |
| Observed churners | 31 |
| Observed non-churners | 89 |
| Churn prevalence | 25.83% |

These findings are specific to the evaluated population and should not be generalized without additional validation.

---

## 3. Baseline Risk Screening

The retained baseline threshold is **0.25**.

| Metric | Result |
|---|---:|
| Threshold | 0.25 |
| High-risk customers | 116 |
| Low-risk customers | 4 |
| High-risk population rate | 96.67% |
| True positives | 31 |
| False positives | 85 |
| True negatives | 4 |
| False negatives | 0 |
| Recall | 100.00% |
| Precision | 26.72% |
| Churn capture rate | 100.00% |

The model captures every observed churner, but the high-risk population is extremely broad.

Only approximately one in four high-risk customers was an observed churner.

---

## 4. Business Interpretation

The model is best interpreted as a **broad risk-screening mechanism**.

It can support:

- retention screening;
- low-cost outreach;
- prioritization for additional analysis;
- secondary business rules;
- customer-value-based filtering.

It should not be presented as a deterministic churn diagnosis.

The prediction represents an analytical risk signal within the evaluated prediction contract.

---

## 5. False-Positive Exposure

At threshold **0.25**:

- 116 customers are high-risk;
- 31 are observed churners;
- 85 are false positives.

This creates substantial false-positive exposure.

High-cost intervention should therefore not automatically be applied to every model-positive customer.

The model is better suited to broad screening followed by secondary business filtering.

---

## 6. Threshold Sensitivity

| Threshold | Precision | Recall | Churn Capture |
|---|---:|---:|---:|
| 0.25 | 26.72% | 100.00% | 100.00% |
| 0.30 | 26.09% | 96.77% | 96.77% |
| 0.35 | 26.85% | 93.55% | 93.55% |
| 0.40 | 25.61% | 67.74% | 67.74% |
| 0.45 | 26.67% | 51.61% | 51.61% |
| 0.50 | 21.62% | 25.81% | 25.81% |

The strongest observed precision in the evaluated threshold grid occurs at **0.35**, with precision of **26.85%** and recall of **93.55%**.

The evaluated threshold grid does not reach the desired **50% precision target**.

Raising the threshold therefore does not solve the fundamental targeting limitation.

---

## 7. Recommended Threshold Strategy

Retain threshold **0.25** for recall-first analytical screening.

The recommendation is based on complete observed churn capture rather than high precision.

At the retained threshold:

- all observed churners are captured;
- the high-risk population remains broad;
- false-positive exposure is substantial.

This is appropriate when missing a potential churner is considered more problematic than screening additional customers.

---

## 8. Recommended Business Workflow

The recommended business workflow is:

1. Apply the Random Forest risk screen at threshold **0.25**.
2. Identify the broad high-risk population.
3. Apply secondary business filtering.
4. Prioritize customers using customer value and business context.
5. Consider intervention cost and available campaign capacity.
6. Apply retention intervention only after business filtering.

Suggested secondary filters include:

- Customer Value
- Intervention Cost
- Engagement History
- Recency / Frequency
- Campaign Capacity

The model should therefore function as the **first-stage screening signal**, not the final intervention decision.

---

## 9. Executive Recommendation

Retain threshold **0.25** for recall-first analytical screening because it preserves **100.00% observed churn capture** on the evaluated population.

Do not position the model as a high-precision churn targeting model.

The best observed precision in the evaluated threshold grid is only **26.85%**, well below the **50% precision target**.

The broad high-risk population and substantial false-positive exposure require downstream business filtering before any high-cost retention intervention.

---

## 10. Analytical Limitations

1. Observed churn labels establish evaluated outcomes but do not establish causal reasons for churn.
2. The evaluated population contains only **120 customer-cutoff records**.
3. Threshold performance is specific to the evaluated prediction contract and threshold grid.
4. Campaign cost is not modeled.
5. Customer lifetime value is not incorporated into the churn decision.
6. Intervention capacity is not modeled.
7. Treatment uplift is not modeled.
8. The prediction artifact remains **not production validated**.

---

## 11. Portfolio Interpretation

The key portfolio finding is the trade-off between **churn capture and targeting efficiency**.

The model successfully identifies the observed churn population at the retained threshold, but it does so by classifying almost the entire evaluated population as high-risk.

This demonstrates why model evaluation must extend beyond a single performance metric.

The business recommendation therefore deliberately avoids overstating model capability and positions the output as an analytical screening mechanism requiring downstream business filtering.

---

## 12. Conclusion

M19.9 establishes the business interpretation of the completed churn-risk analysis.

The final recommendation is:

> **Use threshold 0.25 for recall-first churn screening, but do not use the model as a high-precision standalone retention targeting mechanism.**

The next analytical step should focus on converting this broad screening signal into a more actionable business prioritization framework, potentially incorporating customer value, intervention cost, and campaign capacity.

---

**M19.9 STATUS: COMPLETE**
