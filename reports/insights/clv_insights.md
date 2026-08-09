# Mayasari Bakery — Customer Lifetime Value Insights

## 1. Executive Overview

The customer portfolio contains **850 customers**.

Customers generated total revenue of
**Rp 761,804,925**
and total gross profit of
**Rp 334,282,225**.

Historical CLV averages
**Rp 393,273**
per customer.

Annualized CLV averages
**Rp 549,345**,
with a median of
**Rp 461,554**.

In this analytical model, historical CLV represents
historical customer gross-profit contribution.

Therefore:

**Historical CLV = Customer Gross Profit**

---

## 2. Annualized CLV Distribution

Annualized CLV distribution:

| Statistic | Value |
| --------- | ----: |
| Minimum | Rp 115,114 |
| Q1 | Rp 355,833 |
| Median | Rp 461,554 |
| Q3 | Rp 599,938 |
| Maximum | Rp 2,672,143 |

The distribution shows the spread of normalized customer value
across the observed customer population.

The gap between median and maximum CLV should be monitored because
a large difference may indicate a concentrated high-value customer
population.

---

## 3. CLV Tier Performance

CLV tiers are based on relative annualized CLV:

- **Platinum** — top 25%
- **Gold** — 25–50%
- **Silver** — 50–75%
- **Bronze** — bottom 25%

| Tier | Customers | Customer Share | Revenue | Revenue Share | Gross Profit | GP Share | Annualized CLV | CLV Share | Avg Annualized CLV | Avg Transactions | Avg Lifetime (Days) | Avg Margin |
| ---- | --------: | -------------: | ------: | ------------: | -----------: | -------: | --------------: | --------: | -----------------: | ---------------: | ------------------: | ---------: |
| Bronze | 213 | 25.1% | Rp 97,118,700 | 12.7% | Rp 43,514,400 | 13.0% | Rp 61,098,214 | 13.1% | Rp 286,846 | 13.43 | 312.7 | 44.85% |
| Silver | 212 | 24.9% | Rp 140,851,925 | 18.5% | Rp 62,788,825 | 18.8% | Rp 86,279,233 | 18.5% | Rp 406,978 | 15.30 | 320.1 | 44.62% |
| Gold | 212 | 24.9% | Rp 184,651,575 | 24.2% | Rp 81,717,775 | 24.4% | Rp 111,702,690 | 23.9% | Rp 526,899 | 16.08 | 317.3 | 44.30% |
| Platinum | 213 | 25.1% | Rp 339,182,725 | 44.5% | Rp 146,261,225 | 43.8% | Rp 207,863,517 | 44.5% | Rp 975,885 | 16.38 | 314.4 | 43.62% |

The annualized CLV share column shows how normalized customer value
is distributed across the four relative-value tiers.

Platinum and Gold customers should receive greater retention and
development attention because they represent the highest-value
segments of the current customer portfolio.

---

## 4. High-Value Customer Analysis

### Highest Annualized CLV

Customer **C0346**
has the highest annualized CLV at
**Rp 2,672,143**.

Historical CLV:
**Rp 1,558,750**

Revenue:
**Rp 3,715,450**

Transactions:
**14**

Observed lifetime:
**322 days**

### Highest Historical CLV

Customer **C0531**
has the highest historical CLV at
**Rp 2,000,425**.

### Highest Revenue Customer

Customer **C0560**
has the highest historical revenue at
**Rp 4,851,300**.

### Highest Gross-Margin Customer

Customer **C0066**
has the highest gross-margin percentage at
**47.93%**.

These customers should be evaluated separately because revenue,
historical gross-profit contribution, margin, and annualized CLV
represent different dimensions of customer economics.

---

## 5. CLV Concentration

### Annualized CLV Concentration

The top 10 customers by annualized CLV account for
**5.13%**
of total annualized CLV.

The top 25% of customers by annualized CLV account for
**44.52%**
of total annualized CLV.

This is the primary CLV concentration metric because both the
numerator and denominator use the same annualized CLV measure.

### Historical CLV Concentration

The same customers selected by annualized CLV ranking contribute:

- Top 10 annualized-CLV customers:
  **4.71%**
  of total historical CLV.

- Top 25% annualized-CLV customers:
  **43.75%**
  of total historical CLV.

Historical CLV concentration provides a realized profitability view,
while annualized CLV concentration provides a normalized customer-value
view.

---

## 6. Customer Value Drivers

Annualized CLV is compared with selected customer economic and
behavioral variables.

The correlation values below indicate **association**, not causation.

| Driver | Correlation with Annualized CLV | Relationship |
| ------ | ------------------------------: | ------------ |
| average_transaction_value | 0.947 | Strong positive |
| revenue | 0.943 | Strong positive |
| historical_clv | 0.941 | Strong positive |
| gross_margin_pct | -0.463 | Moderate negative |
| transactions | 0.123 | Very weak positive |
| active_months | -0.043 | Very weak negative |
| observed_lifetime_days | -0.019 | Very weak negative |

The strongest observed association is:

**average_transaction_value shows the strongest observed association with annualized CLV (0.95), with a positively relationship.**

This relationship should be investigated further through behavioral
analysis before being translated into a causal business conclusion.

---

## 7. Metric Reconciliation

The underlying CLV totals reconcile as follows:

| Metric | Total |
| ------ | ----: |
| Total annualized CLV | Rp 466,943,654 |
| Total historical CLV | Rp 334,282,225 |
| Total customer gross profit | Rp 334,282,225 |

Historical CLV and customer gross profit are equal in the current
analytical model.

Annualized CLV is intentionally **not** treated as historical gross profit.

It is a normalized customer-value indicator derived from customer
economics.

---

## 8. Management Priorities

### Priority 1 — Protect Platinum Customers

Platinum customers should receive priority retention attention because they contribute 44.5% of total annualized CLV.

Potential actions include:

- Priority service
- Personalized offers
- Repeat-purchase reminders
- Product recommendations
- Early access to seasonal products

### Priority 2 — Develop Gold Customers

Gold customers represent a potential upgrade pool because they occupy the second-highest relative CLV tier and contribute 23.9% of total annualized CLV.

Potential development levers include:

- Increasing purchase frequency
- Increasing basket value
- Expanding product breadth
- Encouraging repeat purchases
- Improving customer lifetime

### Priority 3 — Investigate Value Drivers

average_transaction_value shows the strongest observed association with annualized CLV (0.95), with a positively relationship.

Correlation identifies association rather than causation. Customer-level actions should therefore be validated through behavioral and commercial analysis.

---

## 9. Customer Value vs Profitability

Customer value should not be evaluated from revenue alone.

A customer can generate high revenue but lower margin, while another
customer may generate less revenue but stronger gross-profit economics.

Management should therefore combine:

- Revenue
- Gross profit
- Gross margin
- Transaction frequency
- Observed lifetime
- Historical CLV
- Annualized CLV

when evaluating strategic customer value.

---

## 10. Business Opportunities

### Opportunity 1 — Protect High-Value Customers

Create retention and relationship-management actions for Platinum
customers and other customers with unusually high annualized CLV.

### Opportunity 2 — Develop Gold Customers

Gold customers represent an attractive upgrade pool.

Focus on increasing purchase frequency, basket value, product breadth,
and customer lifetime.

### Opportunity 3 — Monitor Emerging Customers

Some Bronze and Silver customers may have relatively short observed
lifetimes.

These customers should be monitored for early signals of increasing
purchase frequency or transaction value.

### Opportunity 4 — Validate CLV Drivers

The strongest statistical associations with annualized CLV should
be investigated through customer behavior analysis.

Correlation should be treated as a prioritization tool for further
analysis, not as evidence of causality.

---

## 11. Analytical Limitations

Several limitations should be considered:

- Historical CLV represents realized gross-profit contribution,
  not future customer lifetime value.
- Annualized CLV is a normalized indicator rather than realized profit.
- Annualized CLV can be sensitive to short observed customer lifetimes.
- Relative CLV tiers rank customers within the current population but do not
  establish absolute economic thresholds.
- Correlation analysis identifies association rather than causation.
- Customer behavior may change after the observation period.
- Gross margin is based on the current analytical gross-profit definition.

Annualized CLV should therefore be interpreted as a comparative
customer-value indicator rather than a forecast of future realized profit.

---

## 12. Conclusion

The customer portfolio demonstrates meaningful variation in economic value.

Platinum customers represent the highest relative annualized customer
value and should receive priority retention attention.

Gold customers represent an important development opportunity because
they already demonstrate relatively strong annualized customer value.

The distribution and concentration metrics provide visibility into
whether customer value is broadly distributed or concentrated among
a smaller group of customers.

The value-driver analysis provides a structured starting point for
understanding which customer behaviors and economic characteristics
are most strongly associated with annualized CLV.

The combination of CLV, revenue, gross profit, transaction frequency,
customer lifetime, average transaction value, and margin provides a more
complete framework for customer-value management than revenue alone.
