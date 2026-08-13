# M20.1 — Analytical Cause → Effect Framework

## Purpose

M20.1 establishes a standardized framework for translating analytical results into business explanations.

The objective is to move beyond reporting numerical results and explain what happened, what evidence supports the pattern, which factors are associated with it, what it means for the business, what consequence may follow, and what management action should be considered.

The framework separates observed evidence from interpretation and from hypotheses that have not been causally validated.

---

## Core Analytical Chain

```text
Observed Result
      |
      v
Supporting Evidence
      |
      v
Associated Driver / Pattern
      |
      v
Business Interpretation
      |
      v
Business Consequence
      |
      v
Recommended Action
```

---

## Analytical Explanation Rules

### 1. Observed Result

State the numerical or categorical result directly from a validated analytical artifact.

Example:

> The top 10 customers contribute approximately 5.85% of total customer revenue.

This is an observation, not a causal explanation.

### 2. Supporting Evidence

Identify the analytical evidence that helps explain the result.

Examples include:

* customer concentration
* purchase frequency
* average order value
* recency
* product mix
* gross margin
* customer segmentation
* churn-risk distribution
* revenue trend

### 3. Associated Driver / Pattern

Describe a factor or pattern that is empirically associated with the observed result.

Use careful language such as:

* associated with
* consistent with
* suggests
* indicates
* concentrated in
* correlated with

Do not claim causation unless the analysis supports causal inference.

### 4. Business Interpretation

Translate the analytical pattern into business meaning.

Example:

> Revenue is relatively diversified across the customer base, reducing dependence on a small number of individual customers.

### 5. Business Consequence

Explain what the observed pattern means operationally or strategically.

Example:

> A diversified customer base can reduce the revenue impact of losing any single customer, but it also means growth may require improving value across a broader customer population.

### 6. Recommended Action

Connect the finding to a practical management action.

Example:

> Management should combine retention of high-value customers with systematic development of mid-value customers.

---

## Evidence Hierarchy

The portfolio should distinguish between three levels of analytical statements.

| Level | Meaning | Example language |
|---|---|---|
| Observed | Directly measured from validated data | shows, contains, equals |
| Associated | Supported by analytical relationship or pattern | associated with, suggests, indicates |
| Hypothesized | Plausible explanation requiring validation | may be caused by, could reflect, requires investigation |

The README should never present a hypothesis as an established causal fact.

---

## Cause → Effect Template

Each major business finding should follow this structure:

```text
RESULT
What happened?

        ↓

EVIDENCE
What data supports the result?

        ↓

DRIVER / PATTERN
What factor or pattern is associated with it?

        ↓

MEANING
Why does this matter to the business?

        ↓

CONSEQUENCE
What could happen if the pattern continues?

        ↓

ACTION
What should management investigate or do?
```

---

## Example — Customer Revenue Concentration

### Result

The analysis contains **850 customers**, with total customer revenue of **Rp 761,804,925**. The top 10 customers contribute approximately **5.85%** of total customer revenue.

### Evidence

The relatively small share contributed by the top 10 customers indicates that revenue is distributed across a broad customer base rather than being dominated by a small number of customers.

### Associated Driver / Pattern

Customer revenue concentration is relatively low because the observed revenue contribution is spread across many customers.

### Business Interpretation

The business appears to have a diversified customer revenue base.

### Business Consequence

The business may be less exposed to the loss of a single major customer, but meaningful revenue growth may depend on improving purchasing behavior across a larger portion of the customer base.

### Recommended Action

Management should protect high-value customers while developing repeat-purchase frequency, basket size, and customer value among the broader customer portfolio.

---

## Causal Language Standard

Use:

* **Observed:** "The data shows..."
* **Associated:** "The pattern is associated with..."
* **Interpretation:** "This suggests..."
* **Hypothesis:** "This may indicate... and should be investigated."

Avoid unsupported statements such as:

> "Customers churn because the product mix is poor."

Prefer:

> "Customers with the observed churn-risk pattern also show differences in purchasing behavior. The available analysis identifies an association, but does not establish that purchasing behavior causes churn."

---

## M20.1 Acceptance Criteria

M20.1 is complete when:

- The cause-effect framework is documented.
- Observed results are separated from interpretations.
- Associated patterns are distinguished from causal claims.
- Business consequences are explicitly described.
- Recommended actions are connected to analytical findings.
- The framework is suitable for extending the README.

---

**M20.1 STATUS: COMPLETE**
