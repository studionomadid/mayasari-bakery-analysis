# M20.3 — Customer Cause → Effect Analysis

## Purpose

M20.3 translates customer-level analytics into evidence-based business explanations.

The analysis focuses on measurable customer drivers and management opportunities rather than assuming external causes that are not directly supported by the available dataset.

The objective is to explain how customer value, transaction behavior, recency, frequency, monetary contribution, and customer opportunity segments relate to the business outcome.

---

## Analytical Principle

Customer value should be interpreted through multiple measurable dimensions:

```text
Customer Value
      |
      +--> Revenue
      |
      +--> Gross Profit
      |
      +--> Transaction Frequency
      |
      +--> Average Transaction Value
      |
      +--> Historical CLV
      |
      +--> Annualized CLV

Customer Behavior
      |
      +--> Recency
      +--> Frequency
      +--> Monetary Value

Management Opportunity
      |
      +--> Protect
      +--> Rescue
      +--> Review
      +--> Develop
      +--> Grow
      +--> Monitor
      +--> Win-back

---

## Finding 1 — Customer Value Was Strongly Associated With Transaction Value

The customer performance dataset contains **850 customers**.

The correlation analysis shows that annualized CLV was strongly associated with several economic-value metrics.

| Customer Driver | Correlation with Annualized CLV |
|---|---:|
| Average Transaction Value | 0.947 |
| Revenue | 0.943 |
| Gross Profit | 0.941 |
| Transactions | 0.123 |
| Observed Lifetime Days | -0.019 |
| Active Months | -0.043 |
| Gross Margin | -0.463 |

The strongest relationship was observed between **average transaction value and annualized CLV**, with a correlation of approximately **0.947**.

Revenue and gross profit also showed very strong positive relationships with annualized CLV, at approximately **0.943** and **0.941** respectively.

By comparison, transaction count showed only a weak positive relationship with annualized CLV at approximately **0.123**.

### Cause → Effect Interpretation

```text
Higher Average Transaction Value
              |
              v
      Higher Customer Revenue
              |
              v
        Higher Gross Profit
              |
              v
       Higher Annualized CLV
---

## Finding 2 — High-Value Customers Represented a Significant Revenue Opportunity

The customer opportunity dataset contains **850 customers** with total historical revenue of approximately **Rp 761.8M** and total annualized CLV of approximately **Rp 466.9M**.

The largest opportunity groups by annualized CLV contribution were:

| Opportunity | Customers | Revenue Share | Annualized CLV Share |
|---|---:|---:|---:|
| Review | 184 | 29.78% | 29.70% |
| Rescue | 147 | 23.99% | 24.51% |
| Develop | 169 | 18.07% | 17.36% |
| Monitor | 208 | 13.49% | 14.41% |
| Protect | 46 | 8.54% | 7.44% |
| Win-back | 60 | 3.31% | 4.07% |
| Grow | 36 | 2.82% | 2.51% |

The **Review** and **Rescue** groups together represent **331 customers**, approximately **38.94% of the customer base**, while contributing approximately **54.21% of annualized CLV**.

This concentration makes these two groups particularly relevant for customer-value management.

### Cause → Effect Interpretation

```text
Review + Rescue Customers
          |
          v
331 Customers
          |
          v
54.21% of Annualized CLV
          |
          v
High Management Priority

## Finding 3 — Rescue and Review Concentrated Material Customer Value

The customer opportunity analysis shows that customer value is not evenly distributed across management opportunity groups.

The **Review** group contains 184 customers and contributes approximately **29.78% of total customer revenue** and **29.70% of total annualized CLV**.

The **Rescue** group contains 147 customers and contributes approximately **23.99% of total customer revenue** and **24.51% of total annualized CLV**.

Together, these two groups contain **331 customers**, representing approximately **38.94% of the customer base**, while contributing approximately **54.21% of total annualized CLV**.

This concentration is important because it means that customer-retention and engagement decisions affecting these groups can have a disproportionate impact on the economic value represented in the customer base.

The relationship can be summarized as:

```text
Customer Base
      |
      +-----------------------------+
      |                             |
  Other Groups               Review + Rescue
      |                             |
  61.06% of customers         38.94% of customers
                                    |
                                    v
                           54.21% of annualized CLV
---

## Finding 4 — Recency Differentiated Customer Engagement Risk

Recency provides an important behavioral dimension for interpreting the customer opportunity groups.

The opportunity dataset shows substantial differences in average recency between groups.

| Opportunity | Customers | Average Recency (Days) |
|---|---:|---:|
| Grow | 36 | 4.22 |
| Develop | 169 | 5.59 |
| Protect | 46 | 14.20 |
| Review | 184 | 17.58 |
| Monitor | 208 | 19.83 |
| Rescue | 147 | 41.80 |
| Win-back | 60 | 65.58 |

The **Win-back** group has the highest average recency at approximately **65.58 days**, followed by **Rescue** at approximately **41.80 days**.

By comparison, the **Grow** and **Develop** groups have much lower average recency at approximately **4.22 days** and **5.59 days** respectively.

This pattern indicates that opportunity classification separates customers not only by economic value, but also by observable differences in recent engagement.

### Cause → Effect Interpretation

```text
Higher Recency
      |
      v
Longer Time Since Last Purchase
      |
      v
Lower Recent Engagement
      |
      v
Greater Need for Re-engagement

---

## Finding 5 — Frequency Alone Did Not Explain Customer Value

Transaction frequency was positively related to annualized CLV, but the relationship was substantially weaker than the relationships observed for average transaction value, revenue, and gross profit.

The customer performance analysis produced the following correlations with annualized CLV:

| Customer Driver | Correlation with Annualized CLV |
|---|---:|
| Average Transaction Value | 0.947 |
| Revenue | 0.943 |
| Gross Profit | 0.941 |
| Transactions | 0.123 |
| Observed Lifetime Days | -0.019 |
| Active Months | -0.043 |
| Gross Margin Percentage | -0.463 |

The correlation between **transactions and annualized CLV was approximately 0.123**, which is materially weaker than the relationship between annualized CLV and average transaction value at approximately **0.947**.

This means that transaction count by itself was not a strong explanatory variable for modeled customer value within this dataset.

### Cause → Effect Interpretation

```text
More Transactions
       |
       v
Does Not Automatically Mean
Higher Customer Value
       |
       v
Transaction Value Matters
       |
       v
Higher Value per Transaction
Can Contribute More Strongly
to Annualized CLV

---

## Cause → Effect Summary

The customer evidence supports a multi-dimensional explanation of customer value and customer opportunity.

The observed relationships can be summarized as follows:

```text
Customer Economics
        |
        +--> Average Transaction Value
        |          |
        |          +--> Strong positive association
        |              with Annualized CLV
        |
        +--> Revenue
        |          |
        |          +--> Strong positive association
        |              with Annualized CLV
        |
        +--> Gross Profit
                   |
                   +--> Strong positive association
                       with Annualized CLV


Customer Behavior
        |
        +--> Recency
        |          |
        |          +--> Differentiates recent
        |              engagement from elevated risk
        |
        +--> Frequency
                   |
                   +--> Weak relationship with
                       Annualized CLV when considered alone


Customer Opportunity
        |
        +--> Review + Rescue
                   |
                   +--> 38.94% of customers
                   |
                   +--> 54.21% of annualized CLV
                   |
                   +--> High economic relevance
                       for management attention

---

## What the Data Does Not Prove

The customer analysis identifies measurable associations and concentration patterns, but it does not establish causal relationships beyond the observed data.

The following conclusions should therefore **not** be made from this analysis alone:

- Higher transaction frequency does not necessarily cause higher annualized CLV.
- Higher average transaction value does not by itself prove that customers will remain active longer.
- Higher recency does not prove that a customer has permanently churned.
- The Rescue or Win-back classifications do not prove that customers will leave without intervention.
- The negative correlation between gross margin percentage and annualized CLV does not prove that lower margin causes higher customer value.
- The concentration of annualized CLV within Review and Rescue does not prove that intervention will recover a specific amount of revenue or CLV.
- No external explanation such as seasonality, promotions, holidays, pricing changes, or marketing campaigns can be attributed to these customer patterns without additional evidence.

The analysis should therefore be interpreted as an **evidence-based diagnostic framework**, rather than a causal experiment.

To establish causal effects, additional information would be required, such as controlled campaign data, intervention history, pricing changes, promotional exposure, customer surveys, or experimental treatment and control groups.

---

## Management Takeaway

The customer evidence provides three main management priorities.

### 1. Protect High-Value Customers With Engagement Risk

The **Rescue** group contains 147 customers and approximately **24.51% of total annualized CLV**.

These customers combine meaningful economic value with elevated average recency.

They should therefore receive high-priority retention and re-engagement attention.

### 2. Review a Large Concentration of Customer Value

The **Review** group contains 184 customers and approximately **29.70% of total annualized CLV**.

Together, **Review and Rescue represent 331 customers, or approximately 38.94% of the customer base, while representing approximately 54.21% of annualized CLV**.

This makes these groups strategically important even before considering any external campaign or intervention.

### 3. Develop Customers Based on Recent Engagement and Economic Potential

The **Grow** and **Develop** groups show substantially lower average recency than Rescue and Win-back customers.

This suggests an opportunity to differentiate proactive development from reactive recovery.

A practical management framework is therefore:

```text
High Value + Elevated Recency
            |
            v
          RESCUE
            |
            v
Retention / Re-engagement


High Value Concentration
            |
            v
          REVIEW
            |
            v
Customer-level assessment


Low Recency + Development Potential
            |
            v
      GROW / DEVELOP
            |
            v
Upsell / Cross-sell / Engagement


Very High Recency
            |
            v
        WIN-BACK
            |
            v
Reactivation assessment

---

## M20.3 Acceptance Criteria

M20.3 is considered complete when the following conditions are satisfied:

- [x] Customer performance evidence is derived from `customer_performance.parquet`.
- [x] Customer opportunity evidence is derived from `customer_opportunity.parquet`.
- [x] Customer population size of 850 is documented.
- [x] Total historical customer revenue of approximately Rp 761.8M is documented.
- [x] Total annualized CLV of approximately Rp 466.9M is documented.
- [x] Average transaction value is identified as the strongest observed customer-value relationship at approximately 0.947 correlation with annualized CLV.
- [x] Revenue and gross profit relationships with annualized CLV are documented at approximately 0.943 and 0.941.
- [x] Transaction frequency is identified as a comparatively weak relationship with annualized CLV at approximately 0.123.
- [x] Review and Rescue concentration is documented.
- [x] Review and Rescue together are identified as 331 customers, approximately 38.94% of the customer base.
- [x] Review and Rescue together are identified as representing approximately 54.21% of annualized CLV.
- [x] Recency differences across opportunity groups are documented.
- [x] The analysis distinguishes observed associations from causal claims.
- [x] External factors are not attributed without supporting evidence.
- [x] Management implications are derived from measurable customer evidence.
- [x] The document contains a cause → effect synthesis.
- [x] The document contains explicit analytical limitations.
- [x] The document contains a management takeaway.
- [x] Markdown formatting passes `git diff --check`.
- [x] No known corruption or interrupted-terminal artifacts remain.

### M20.3 Outcome

M20.3 establishes an evidence-based customer cause → effect framework linking customer economics, engagement behavior, customer opportunity classification, and management prioritization.

The analysis identifies where customer value is concentrated, which measurable customer drivers are most strongly associated with modeled value, and where recency indicates elevated engagement risk.

The findings are intended for diagnostic and management prioritization purposes and should not be interpreted as proof of causal relationships.
