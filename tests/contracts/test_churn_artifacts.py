"""Contract tests for churn-model analytical artifacts.

These tests protect the public schema, grain, lineage, and decision
contracts of the M19 churn-modeling artifacts.

The tests intentionally validate artifacts rather than model internals.
Model implementation details may change, but downstream analytical
contracts must remain explicit and stable.
"""

from __future__ import annotations

import math

import pandas as pd

from src.contracts.paths import PROCESSED_DIR


TOLERANCE = 0.0001


# ---------------------------------------------------------------------------
# Artifact paths
# ---------------------------------------------------------------------------

BASELINE_ASSESSMENT_DATA = (
    PROCESSED_DIR / "baseline_assessment_m19_3_5.parquet"
)

BASELINE_CUTOFF_DIAGNOSTICS_DATA = (
    PROCESSED_DIR / "baseline_cutoff_diagnostics_m19_3_4.parquet"
)

BASELINE_PREDICTIONS_DATA = (
    PROCESSED_DIR / "baseline_model_predictions_m19_3_3.parquet"
)

BASELINE_THRESHOLD_ANALYSIS_DATA = (
    PROCESSED_DIR / "baseline_threshold_analysis_m19_3_4.parquet"
)

HISTORICAL_BASELINE_FEATURES_DATA = (
    PROCESSED_DIR / "historical_baseline_features_m19_3_1.parquet"
)

TRAINING_DATA = (
    PROCESSED_DIR / "training_dataset_m19_3_2.parquet"
)

RANDOM_FOREST_ASSESSMENT_DATA = (
    PROCESSED_DIR / "random_forest_assessment_m19_4_4.parquet"
)

RANDOM_FOREST_CUTOFF_DIAGNOSTICS_DATA = (
    PROCESSED_DIR / "random_forest_cutoff_diagnostics_m19_4_3.parquet"
)

RANDOM_FOREST_FEATURE_IMPORTANCE_DATA = (
    PROCESSED_DIR / "random_forest_feature_importance_m19_4_5.parquet"
)

RANDOM_FOREST_PREDICTIONS_DATA = (
    PROCESSED_DIR / "random_forest_predictions_m19_4_2.parquet"
)

RANDOM_FOREST_RANKING_DIAGNOSTICS_DATA = (
    PROCESSED_DIR / "random_forest_ranking_diagnostics_m19_4_3.parquet"
)

RANDOM_FOREST_THRESHOLD_ANALYSIS_DATA = (
    PROCESSED_DIR / "random_forest_threshold_analysis_m19_4_3.parquet"
)

MODEL_COMPARISON_DATA = (
    PROCESSED_DIR / "baseline_vs_random_forest_comparison_m19_4_6.parquet"
)

THRESHOLD_DIAGNOSTIC_DATA = (
    PROCESSED_DIR / "threshold_diagnostic_m19_5_3.parquet"
)

MODEL_THRESHOLD_DECISION_DATA = (
    PROCESSED_DIR / "model_threshold_decision_m19_5_4.parquet"
)

FINAL_PREDICTION_CONTRACT_DATA = (
    PROCESSED_DIR / "final_prediction_contract_m19_5_5.parquet"
)

RISK_POPULATION_DATA = (
    PROCESSED_DIR / "risk_population_analysis_m19_6_2.parquet"
)

BUSINESS_RISK_DATA = (
    PROCESSED_DIR / "business_risk_interpretation_m19_6_3.parquet"
)

THRESHOLD_SENSITIVITY_DATA = (
    PROCESSED_DIR / "threshold_sensitivity_analysis_m19_6_4.parquet"
)

THRESHOLD_DECISION_RECOMMENDATION_DATA = (
    PROCESSED_DIR / "threshold_decision_recommendation_m19_6_5.parquet"
)

FINAL_RISK_STRATEGY_DATA = (
    PROCESSED_DIR / "final_risk_strategy_m19_6_6.parquet"
)

CHURN_LABELS_DATA = (
    PROCESSED_DIR / "churn_labels_m19_2.parquet"
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def assert_close(left: float, right: float) -> None:
    """Assert two numeric values are equal within contract tolerance."""
    assert math.isclose(
        float(left),
        float(right),
        rel_tol=0.0,
        abs_tol=TOLERANCE,
    ), f"Values do not reconcile: {left} != {right}"


def assert_columns(
    dataframe: pd.DataFrame,
    expected: list[str],
    artifact_name: str,
) -> None:
    """Assert exact public column ordering."""
    assert list(dataframe.columns) == expected, (
        f"Schema columns changed for {artifact_name}: "
        f"{list(dataframe.columns)}"
    )


# ---------------------------------------------------------------------------
# Existence contracts
# ---------------------------------------------------------------------------


def test_all_m19_churn_artifacts_exist() -> None:
    """Every required M19 churn artifact must exist."""

    artifacts = [
        BASELINE_ASSESSMENT_DATA,
        BASELINE_CUTOFF_DIAGNOSTICS_DATA,
        BASELINE_PREDICTIONS_DATA,
        BASELINE_THRESHOLD_ANALYSIS_DATA,
        HISTORICAL_BASELINE_FEATURES_DATA,
        TRAINING_DATA,
        RANDOM_FOREST_ASSESSMENT_DATA,
        RANDOM_FOREST_CUTOFF_DIAGNOSTICS_DATA,
        RANDOM_FOREST_FEATURE_IMPORTANCE_DATA,
        RANDOM_FOREST_PREDICTIONS_DATA,
        RANDOM_FOREST_RANKING_DIAGNOSTICS_DATA,
        RANDOM_FOREST_THRESHOLD_ANALYSIS_DATA,
        MODEL_COMPARISON_DATA,
        THRESHOLD_DIAGNOSTIC_DATA,
        MODEL_THRESHOLD_DECISION_DATA,
        FINAL_PREDICTION_CONTRACT_DATA,
        RISK_POPULATION_DATA,
        BUSINESS_RISK_DATA,
        THRESHOLD_SENSITIVITY_DATA,
        THRESHOLD_DECISION_RECOMMENDATION_DATA,
        FINAL_RISK_STRATEGY_DATA,
        CHURN_LABELS_DATA,
    ]

    for artifact in artifacts:
        assert artifact.exists(), f"Missing M19 artifact: {artifact}"


# ---------------------------------------------------------------------------
# Prediction artifact schemas
# ---------------------------------------------------------------------------


def test_baseline_prediction_schema() -> None:
    """Baseline prediction artifact must preserve its public schema."""

    dataframe = pd.read_parquet(BASELINE_PREDICTIONS_DATA)

    expected = [
        "customer_id",
        "cutoff",
        "purchase_count_before_cutoff",
        "recency_days",
        "customer_tenure_days",
        "active_month_count",
        "churn_label",
        "predicted_probability",
        "predicted_label",
    ]

    assert_columns(
        dataframe,
        expected,
        "baseline_model_predictions_m19_3_3",
    )


def test_random_forest_prediction_schema() -> None:
    """Random Forest prediction artifact must preserve its public schema."""

    dataframe = pd.read_parquet(RANDOM_FOREST_PREDICTIONS_DATA)

    expected = [
        "customer_id",
        "cutoff",
        "churn_label",
        "purchase_count_before_cutoff",
        "recency_days",
        "customer_tenure_days",
        "active_month_count",
        "predicted_probability",
        "predicted_label",
    ]

    assert_columns(
        dataframe,
        expected,
        "random_forest_predictions_m19_4_2",
    )


def test_final_prediction_contract_schema() -> None:
    """Final prediction contract must preserve its public schema."""

    dataframe = pd.read_parquet(FINAL_PREDICTION_CONTRACT_DATA)

    expected = [
        "customer_id",
        "cutoff",
        "churn_label",
        "predicted_probability",
        "model",
        "threshold",
        "predicted_label",
        "prediction_contract",
        "production_status",
    ]

    assert_columns(
        dataframe,
        expected,
        "final_prediction_contract_m19_5_5",
    )


# ---------------------------------------------------------------------------
# Grain contracts
# ---------------------------------------------------------------------------


def test_prediction_grain_is_customer_cutoff() -> None:
    """Prediction artifacts must contain one row per customer-cutoff pair."""

    for path in (
        BASELINE_PREDICTIONS_DATA,
        RANDOM_FOREST_PREDICTIONS_DATA,
        FINAL_PREDICTION_CONTRACT_DATA,
    ):
        dataframe = pd.read_parquet(path)

        assert not dataframe.duplicated(
            subset=["customer_id", "cutoff"]
        ).any(), f"Duplicate customer-cutoff rows found in {path.name}"


def test_prediction_artifacts_have_same_population() -> None:
    """Baseline, RF, and final prediction contracts must share population."""

    baseline = pd.read_parquet(BASELINE_PREDICTIONS_DATA)
    random_forest = pd.read_parquet(RANDOM_FOREST_PREDICTIONS_DATA)
    final = pd.read_parquet(FINAL_PREDICTION_CONTRACT_DATA)

    baseline_keys = set(
        zip(
            baseline["customer_id"],
            baseline["cutoff"],
        )
    )

    rf_keys = set(
        zip(
            random_forest["customer_id"],
            random_forest["cutoff"],
        )
    )

    final_keys = set(
        zip(
            final["customer_id"],
            final["cutoff"],
        )
    )

    assert baseline_keys == rf_keys
    assert rf_keys == final_keys


# ---------------------------------------------------------------------------
# Prediction validity contracts
# ---------------------------------------------------------------------------


def test_prediction_probabilities_are_valid() -> None:
    """Prediction probabilities must remain within [0, 1]."""

    for path in (
        BASELINE_PREDICTIONS_DATA,
        RANDOM_FOREST_PREDICTIONS_DATA,
        FINAL_PREDICTION_CONTRACT_DATA,
    ):
        dataframe = pd.read_parquet(path)

        assert dataframe["predicted_probability"].between(
            0.0,
            1.0,
            inclusive="both",
        ).all(), f"Invalid probability found in {path.name}"


def test_prediction_labels_are_binary() -> None:
    """Predicted labels and churn labels must remain binary."""

    for path in (
        BASELINE_PREDICTIONS_DATA,
        RANDOM_FOREST_PREDICTIONS_DATA,
        FINAL_PREDICTION_CONTRACT_DATA,
    ):
        dataframe = pd.read_parquet(path)

        assert set(
            dataframe["predicted_label"].unique()
        ).issubset({0, 1}), f"Invalid predicted label in {path.name}"

        assert set(
            dataframe["churn_label"].unique()
        ).issubset({0, 1}), f"Invalid churn label in {path.name}"


# ---------------------------------------------------------------------------
# Model comparison contracts
# ---------------------------------------------------------------------------


def test_model_comparison_schema() -> None:
    """Model comparison artifact must preserve its public schema."""

    dataframe = pd.read_parquet(MODEL_COMPARISON_DATA)

    expected = [
        "metric",
        "metric_group",
        "baseline",
        "random_forest",
        "difference_rf_minus_baseline",
        "baseline_decision",
        "random_forest_decision",
        "primary_metric_winner",
        "comparison_decision",
        "comparison_rationale",
        "validation_rows",
        "positive_count",
        "negative_count",
        "positive_rate_pct",
    ]

    assert_columns(
        dataframe,
        expected,
        "baseline_vs_random_forest_comparison_m19_4_6",
    )


def test_model_comparison_population_is_consistent() -> None:
    """Every comparison row must use the same validation population."""

    dataframe = pd.read_parquet(MODEL_COMPARISON_DATA)

    assert dataframe["validation_rows"].nunique() == 1
    assert dataframe["positive_count"].nunique() == 1
    assert dataframe["negative_count"].nunique() == 1
    assert dataframe["positive_rate_pct"].nunique() == 1

    validation_rows = int(dataframe.iloc[0]["validation_rows"])

    baseline = pd.read_parquet(BASELINE_PREDICTIONS_DATA)

    assert len(baseline) == validation_rows


def test_model_comparison_difference_is_reconciled() -> None:
    """RF-minus-baseline differences must equal source metric values."""

    dataframe = pd.read_parquet(MODEL_COMPARISON_DATA)

    expected_difference = (
        dataframe["random_forest"]
        - dataframe["baseline"]
    )

    pd.testing.assert_series_equal(
        dataframe["difference_rf_minus_baseline"],
        expected_difference,
        check_names=False,
        check_exact=False,
        rtol=0.0,
        atol=TOLERANCE,
    )


# ---------------------------------------------------------------------------
# Threshold / prediction contract
# ---------------------------------------------------------------------------


def test_final_prediction_contract_uses_declared_model() -> None:
    """Final prediction rows must identify the selected model consistently."""

    dataframe = pd.read_parquet(FINAL_PREDICTION_CONTRACT_DATA)

    assert dataframe["model"].nunique() == 1
    assert dataframe["model"].iloc[0] == "random_forest"


def test_final_prediction_contract_uses_declared_threshold() -> None:
    """Final prediction rows must use one explicit threshold."""

    dataframe = pd.read_parquet(FINAL_PREDICTION_CONTRACT_DATA)

    assert dataframe["threshold"].nunique() == 1

    threshold = float(dataframe["threshold"].iloc[0])

    assert 0.0 < threshold < 1.0


def test_final_prediction_labels_follow_threshold() -> None:
    """Final labels must be deterministic from probability and threshold."""

    dataframe = pd.read_parquet(FINAL_PREDICTION_CONTRACT_DATA)

    expected = (
        dataframe["predicted_probability"]
        >= dataframe["threshold"]
    ).astype(int)

    pd.testing.assert_series_equal(
        dataframe["predicted_label"],
        expected,
        check_names=False,
    )


def test_final_prediction_contract_is_not_production_validated() -> None:
    """Current M19 prediction contract must not claim production validation."""

    dataframe = pd.read_parquet(FINAL_PREDICTION_CONTRACT_DATA)

    assert dataframe["production_status"].nunique() == 1
    assert (
        dataframe["production_status"].iloc[0]
        == "not_production_validated"
    )

    assert dataframe["prediction_contract"].nunique() == 1
    assert dataframe["prediction_contract"].iloc[0] == "m19.5.5"


# ---------------------------------------------------------------------------
# Risk interpretation contracts
# ---------------------------------------------------------------------------


def test_business_risk_interpretation_schema() -> None:
    """Business-risk interpretation must remain a singleton decision artifact."""

    dataframe = pd.read_parquet(BUSINESS_RISK_DATA)

    assert len(dataframe) == 1

    required = {
        "analysis_version",
        "source_analysis_version",
        "model",
        "threshold",
        "prediction_contract",
        "production_status",
        "population",
        "actual_churners",
        "high_risk",
        "low_risk",
        "tp",
        "fp",
        "tn",
        "fn",
        "precision",
        "recall",
        "high_risk_rate",
        "churn_capture_rate",
        "risk_interpretation",
        "targeting_interpretation",
        "campaign_implication",
        "threshold_review_recommended",
    }

    assert required.issubset(set(dataframe.columns))


def test_business_risk_counts_reconcile() -> None:
    """Risk population confusion-matrix counts must reconcile."""

    dataframe = pd.read_parquet(BUSINESS_RISK_DATA)

    row = dataframe.iloc[0]

    assert int(row["tp"]) + int(row["fn"]) == int(
        row["actual_churners"]
    )

    assert int(row["tn"]) + int(row["fp"]) == (
        int(row["population"])
        - int(row["actual_churners"])
    )

    assert int(row["high_risk"]) == (
        int(row["tp"]) + int(row["fp"])
    )

    assert int(row["low_risk"]) == (
        int(row["tn"]) + int(row["fn"])
    )


def test_business_risk_metrics_reconcile() -> None:
    """Business-risk rates must reconcile with confusion-matrix counts."""

    dataframe = pd.read_parquet(BUSINESS_RISK_DATA)

    row = dataframe.iloc[0]

    precision = (
        float(row["tp"])
        / (int(row["tp"]) + int(row["fp"]))
    )

    recall = (
        float(row["tp"])
        / (int(row["tp"]) + int(row["fn"]))
    )

    high_risk_rate = (
        int(row["high_risk"])
        / int(row["population"])
    )

    assert_close(float(row["precision"]), precision)
    assert_close(float(row["recall"]), recall)
    assert_close(float(row["high_risk_rate"]), high_risk_rate)


def test_business_risk_status_matches_prediction_contract() -> None:
    """Risk interpretation must inherit the final prediction contract status."""

    risk = pd.read_parquet(BUSINESS_RISK_DATA)
    prediction = pd.read_parquet(FINAL_PREDICTION_CONTRACT_DATA)

    risk_row = risk.iloc[0]

    assert (
        risk_row["production_status"]
        == prediction["production_status"].iloc[0]
    )

    assert (
        risk_row["prediction_contract"]
        == prediction["prediction_contract"].iloc[0]
    )

    assert (
        risk_row["model"]
        == prediction["model"].iloc[0]
    )


# ---------------------------------------------------------------------------
# Threshold recommendation contracts
# ---------------------------------------------------------------------------


def test_threshold_recommendation_schema() -> None:
    """Threshold recommendation must remain a singleton decision artifact."""

    dataframe = pd.read_parquet(
        THRESHOLD_DECISION_RECOMMENDATION_DATA
    )

    assert len(dataframe) == 1

    required = {
        "analysis_version",
        "source_analysis_version",
        "model",
        "prediction_contract",
        "production_status",
        "baseline_threshold",
        "recommended_threshold",
        "recommendation_matches_baseline",
        "threshold_change_required",
        "population",
        "actual_churners",
        "recommended_high_risk",
        "recommended_precision",
        "recommended_recall",
        "recommended_churn_capture_rate",
        "precision_target",
        "high_precision_target_available",
        "best_precision_threshold",
        "best_precision_value",
        "best_precision_recall",
        "targeting_mode",
        "high_precision_targeting_status",
        "business_decision",
        "campaign_decision",
        "precision_warning",
        "risk_interpretation",
    }

    assert required.issubset(set(dataframe.columns))


def test_threshold_recommendation_matches_observed_contract() -> None:
    """Recommended threshold must remain the declared baseline threshold."""

    dataframe = pd.read_parquet(
        THRESHOLD_DECISION_RECOMMENDATION_DATA
    )

    row = dataframe.iloc[0]

    assert_close(
        float(row["baseline_threshold"]),
        float(row["recommended_threshold"]),
    )

    assert bool(row["recommendation_matches_baseline"]) is True
    assert bool(row["threshold_change_required"]) is False


def test_threshold_recommendation_preserves_precision_warning() -> None:
    """Current threshold recommendation must retain its precision warning."""

    dataframe = pd.read_parquet(
        THRESHOLD_DECISION_RECOMMENDATION_DATA
    )

    row = dataframe.iloc[0]

    assert bool(row["precision_warning"]) is True
    assert bool(row["high_precision_target_available"]) is False


# ---------------------------------------------------------------------------
# Final strategy contracts
# ---------------------------------------------------------------------------


def test_final_risk_strategy_is_singleton() -> None:
    """Final risk strategy must contain exactly one decision row."""

    dataframe = pd.read_parquet(FINAL_RISK_STRATEGY_DATA)

    assert len(dataframe) == 1


def test_final_risk_strategy_is_not_production_validated() -> None:
    """Final risk strategy must not claim production readiness."""

    dataframe = pd.read_parquet(FINAL_RISK_STRATEGY_DATA)

    row = dataframe.iloc[0]

    assert row["production_status"] == "not_production_validated"


def test_final_risk_strategy_recommends_recall_first_posture() -> None:
    """Current strategy must preserve the recall-first analytical posture."""

    dataframe = pd.read_parquet(FINAL_RISK_STRATEGY_DATA)

    row = dataframe.iloc[0]

    assert row["targeting_mode"] == "recall_first_broad_screening"
    assert row["campaign_posture"] == (
        "broad_retention_screening_with_cost_awareness"
    )
    assert row["business_decision"] == (
        "retain_baseline_for_recall_first_screening"
    )
    assert row["campaign_decision"] == (
        "do_not_claim_high_precision_targeting"
    )


# ---------------------------------------------------------------------------
# Cross-artifact reconciliation
# ---------------------------------------------------------------------------


def test_prediction_count_reconciles_across_m19() -> None:
    """Prediction population must reconcile across assessment artifacts."""

    baseline = pd.read_parquet(BASELINE_ASSESSMENT_DATA)
    rf = pd.read_parquet(RANDOM_FOREST_ASSESSMENT_DATA)
    comparison = pd.read_parquet(MODEL_COMPARISON_DATA)

    baseline_rows = int(baseline.iloc[0]["validation_rows"])
    rf_rows = int(rf.iloc[0]["validation_rows"])
    comparison_rows = int(comparison.iloc[0]["validation_rows"])

    assert baseline_rows == rf_rows == comparison_rows


def test_positive_count_reconciles_across_m19() -> None:
    """Validation positive count must remain consistent across models."""

    baseline = pd.read_parquet(BASELINE_ASSESSMENT_DATA)
    rf = pd.read_parquet(RANDOM_FOREST_ASSESSMENT_DATA)
    comparison = pd.read_parquet(MODEL_COMPARISON_DATA)

    baseline_positive = int(baseline.iloc[0]["positive_count"])
    rf_positive = int(rf.iloc[0]["positive_count"])
    comparison_positive = int(comparison.iloc[0]["positive_count"])

    assert baseline_positive == rf_positive == comparison_positive


def test_prediction_population_matches_assessment() -> None:
    """Final prediction rows must match the evaluated assessment population."""

    prediction = pd.read_parquet(FINAL_PREDICTION_CONTRACT_DATA)
    assessment = pd.read_parquet(RANDOM_FOREST_ASSESSMENT_DATA)

    assert len(prediction) == int(
        assessment.iloc[0]["validation_rows"]
    )


def test_prediction_churn_count_matches_assessment() -> None:
    """Final prediction labels must preserve observed churn count."""

    prediction = pd.read_parquet(FINAL_PREDICTION_CONTRACT_DATA)
    assessment = pd.read_parquet(RANDOM_FOREST_ASSESSMENT_DATA)

    expected = int(assessment.iloc[0]["positive_count"])
    actual = int(prediction["churn_label"].sum())

    assert actual == expected


# ---------------------------------------------------------------------------
# Threshold sensitivity contracts
# ---------------------------------------------------------------------------


def test_threshold_sensitivity_contains_baseline_scenario() -> None:
    """Threshold sensitivity analysis must explicitly contain baseline threshold."""

    dataframe = pd.read_parquet(THRESHOLD_SENSITIVITY_DATA)

    baseline_rows = dataframe[
        dataframe["threshold_is_baseline_contract"]
    ]

    assert len(baseline_rows) == 1

    baseline_threshold = float(
        baseline_rows.iloc[0]["scenario_threshold"]
    )

    recommendation = pd.read_parquet(
        THRESHOLD_DECISION_RECOMMENDATION_DATA
    )

    recommended_threshold = float(
        recommendation.iloc[0]["recommended_threshold"]
    )

    assert_close(
        baseline_threshold,
        recommended_threshold,
    )


def test_threshold_sensitivity_uses_same_prediction_population() -> None:
    """All threshold scenarios must evaluate the same population."""

    dataframe = pd.read_parquet(THRESHOLD_SENSITIVITY_DATA)

    assert dataframe["population"].nunique() == 1
    assert dataframe["actual_churners"].nunique() == 1
    assert dataframe["actual_non_churners"].nunique() == 1

    population = int(dataframe.iloc[0]["population"])

    prediction = pd.read_parquet(FINAL_PREDICTION_CONTRACT_DATA)

    assert len(prediction) == population
