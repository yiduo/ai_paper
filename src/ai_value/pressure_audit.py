"""Finite Poisson Ising certificate audit; never tests the thermodynamic theorem.

Oracle A keeps the original interaction count and an integer dynamic law of
loop/cross score sums. Oracle B thins the Poisson process and integrates the
cross couplings separately. Count tails have exact rational majorants;
transcendental arithmetic is numerical and checked at a second precision.
"""

from __future__ import annotations

from collections import defaultdict
from decimal import Decimal, ROUND_CEILING, localcontext
from fractions import Fraction
from itertools import product
from math import factorial


LAWS = ("symmetric_rademacher", "deterministic_positive_one", "zero")


def decimal_fraction(value: Fraction) -> Decimal:
    return Decimal(value.numerator) / Decimal(value.denominator)


def upper_decimal(value: Fraction) -> Decimal:
    with localcontext() as ctx:
        ctx.rounding = ROUND_CEILING
        return decimal_fraction(value)


def poisson_tail_majorants(mean: Fraction, cutoff: int) -> tuple[Fraction, Fraction]:
    """Upper bounds for P(Q>cutoff) and E[Q 1_(Q>cutoff)].

    Drop exp(-mean)<=1 and majorize the remaining series geometrically.
    These fractions require no transcendental evaluation or tail subtraction.
    """
    if mean < 0 or cutoff < 0 or mean >= cutoff + 1:
        raise ValueError("Tail majorant requires 0<=mean<cutoff+1")
    probability = mean ** (cutoff + 1) / factorial(cutoff + 1)
    probability /= 1 - mean / (cutoff + 2)
    first_moment = mean * mean ** cutoff / factorial(cutoff)
    first_moment /= 1 - mean / (cutoff + 1)
    return probability, first_moment


def conditional_profiles(law: str, cutoff: int) -> list[dict]:
    """Exact conditional integer counts for the original M interactions.

    In N=2 each ordered index pair is a loop with probability1/2. In the
    symmetric law its sign is an independent fair coin. Distinct ordered
    pairs inducing the same score vector are combined, with multiplicity.
    """
    if law not in LAWS or cutoff < 0:
        raise ValueError("Unsupported finite fixture")
    outcomes = {"symmetric_rademacher": ((1, 0), (-1, 0), (0, 1), (0, -1)),
                "deterministic_positive_one": ((1, 0), (0, 1)),
                "zero": ((0, 0),)}[law]
    branch = len(outcomes)
    distribution = {(0, 0): 1}
    profiles = []
    for count in range(cutoff + 1):
        total = branch ** count
        if sum(distribution.values()) != total:
            raise ArithmeticError("Original-count dynamic law lost probability mass")
        cross = defaultdict(int)
        for (loop_score, cross_score), multiplicity in distribution.items():
            cross[cross_score] += multiplicity
        profiles.append({"count": count, "denominator": total,
                         "cross_counts": dict(cross),
                         "loop_score_sum": sum(l * w for (l, _), w in distribution.items()),
                         "joint_states": len(distribution)})
        if count < cutoff:
            next_distribution = defaultdict(int)
            for (loop_score, cross_score), multiplicity in distribution.items():
                for dl, dc in outcomes:
                    next_distribution[loop_score + dl, cross_score + dc] += multiplicity
            distribution = dict(next_distribution)
    return profiles


def literal_spin_log_partition(beta: Decimal, cross_score: int) -> Decimal:
    # Common loop score factors out as beta*loop_score. The remaining four
    # configuration weights are enumerated literally, without a cosh formula.
    return sum((beta * cross_score * s * t).exp()
               for s, t in product((-1, 1), repeat=2)).ln()


def conditional_pressure(profile: dict, beta: Decimal,
                         partition_logs: dict[int, Decimal]) -> Decimal:
    total = Decimal(profile["denominator"])
    log_partition_mean = beta * profile["loop_score_sum"] / total
    log_partition_mean += sum(Decimal(w) / total * partition_logs[c]
                              for c, w in profile["cross_counts"].items())
    return log_partition_mean / 2


def poisson_weights(mean: Decimal, cutoff: int) -> list[Decimal]:
    probabilities = [(-mean).exp()]
    for count in range(1, cutoff + 1):
        probabilities.append(probabilities[-1] * mean / count)
    return probabilities


def original_count_expectation(alpha: Fraction, beta: Decimal, profiles: list[dict],
                               partition_logs: dict[int, Decimal]) -> tuple[Decimal, Fraction, Fraction]:
    weights = poisson_weights(decimal_fraction(2 * alpha), len(profiles) - 1)
    value = sum(p * conditional_pressure(profile, beta, partition_logs)
                for p, profile in zip(weights, profiles))
    tail_probability, tail_first = poisson_tail_majorants(2 * alpha, len(profiles) - 1)
    return value, tail_probability, tail_first


def log_cosh(value: Decimal) -> Decimal:
    return ((value.exp() + (-value).exp()) / 2).ln()


def thinned_expectation(alpha: Fraction, beta: Decimal, law: str, cutoff: int,
                       cosh_logs: dict[int, Decimal]) -> tuple[Decimal, Fraction]:
    if law not in LAWS:
        raise ValueError("Unsupported coupling law")
    log_two = Decimal(2).ln()
    if law == "zero":
        return log_two, Fraction(0)
    if law == "deterministic_positive_one":
        weights = poisson_weights(decimal_fraction(alpha), cutoff)
        cross_term = sum(w * cosh_logs[k] for k, w in enumerate(weights)) / 2
        _, first = poisson_tail_majorants(alpha, cutoff)
        return log_two + beta * decimal_fraction(alpha) / 2 + cross_term, first / 2
    # Independent positive/negative cross-edge counts have mean alpha/2.
    # Their exact loop contribution is zero by sign symmetry.
    half = alpha / 2
    weights = poisson_weights(decimal_fraction(half), cutoff)
    cross_term = sum(wi * wj * cosh_logs[abs(i - j)]
                     for i, wi in enumerate(weights) for j, wj in enumerate(weights)) / 2
    tail, first = poisson_tail_majorants(half, cutoff)
    # Union bound for E[(Q+ + Q-)1_(either count>cutoff)], divided by2.
    return log_two + cross_term, first + half * tail


def eligibility(law: str) -> tuple[bool, str]:
    if law == "symmetric_rademacher":
        return True, "All odd E[(-b)^n]=0; even moments=tanh(beta)^n>=0"
    if law == "zero":
        return True, "b=0 and every positive-order signed moment is zero"
    if law == "deterministic_positive_one":
        return False, "E[-b]=-tanh(beta)<0 for beta>0; first required moment fails"
    raise ValueError("No all-moment guard for an arbitrary coupling distribution")


def evaluate(spec: dict, precision: int, profiles_by_law: dict[str, list[dict]]) -> list[dict]:
    inp = spec["input"]
    cutoff = inp["count_cutoff"]
    rows = []
    with localcontext() as ctx:
        ctx.prec = precision
        for beta_text in inp["inverse_temperatures"]:
            beta_fraction = Fraction(beta_text)
            beta = decimal_fraction(beta_fraction)
            partition_logs = {c: literal_spin_log_partition(beta, c)
                              for c in range(-cutoff, cutoff + 1)}
            cosh_logs = {c: log_cosh(beta * c) for c in range(cutoff + 1)}
            for alpha_text in inp["densities"]:
                alpha = Fraction(alpha_text)
                for law in inp["coupling_laws"]:
                    value_a, tail_probability, tail_first = original_count_expectation(
                        alpha, beta, profiles_by_law[law], partition_logs)
                    value_b, tail_b_coefficient = thinned_expectation(
                        alpha, beta, law, cutoff, cosh_logs)
                    # |logZ/N|<=log2+beta*M/2. log2<1 makes this
                    # rational majorant weaker but exact, with no log rounding.
                    tail_a = tail_probability + beta_fraction * tail_first / 2
                    tail_b = beta_fraction * tail_b_coefficient
                    trial = Decimal(2).ln() + decimal_fraction(alpha) * (
                        cosh_logs[1] if law != "zero" else 0)
                    accepted, reason = eligibility(law)
                    arithmetic = Decimal(inp["arithmetic_allowance"])
                    uncertainty = upper_decimal(tail_a + tail_b) + 2 * arithmetic
                    excess = value_a - trial
                    rows.append({"alpha": alpha_text, "beta": beta_text, "law": law,
                                 "precision": precision, "pressure_oracle_a": str(value_a),
                                 "pressure_oracle_b": str(value_b), "trial_value": str(trial),
                                 "signed_excess": str(excess),
                                 "excess_lower_with_declared_allowance": str(excess - uncertainty),
                                 "oracle_absolute_disagreement": str(abs(value_a - value_b)),
                                 "original_count_tail_probability_majorant": str(tail_probability),
                                 "original_count_tail_first_moment_majorant": str(tail_first),
                                 "pressure_tail_a_majorant": str(tail_a),
                                 "pressure_tail_b_majorant": str(tail_b),
                                 "max_pressure_tail_decimal_upper": str(upper_decimal(max(tail_a, tail_b))),
                                 "combined_tail_and_arithmetic_allowance": str(uncertainty),
                                 "naive_even_arity_guard_accepts": True,
                                 "pt_guard_accepts": accepted, "eligibility_reason": reason,
                                 "upper_inequality_violated_beyond_allowance": excess > uncertainty,
                                 "raw_counterexample_margin_exceeds_threshold":
                                     excess - uncertainty > Decimal(spec["success"]["excess_threshold_nats_per_spin"])})
    return rows


def experiment(spec: dict) -> tuple[list[dict], dict]:
    inp, success = spec["input"], spec["success"]
    if inp["spins"] != 2 or inp["arity"] != 2 or inp["external_field"] != 0:
        raise ValueError("Only the preregistered N=2,p=2,zero-field fixtures are implemented")
    if any(law not in LAWS for law in inp["coupling_laws"]):
        raise ValueError("Unsupported sign-law eligibility claim")
    if any(Fraction(x) <= 0 for x in inp["densities"] + inp["inverse_temperatures"]):
        raise ValueError("Positive density and inverse temperature required")
    if inp["cross_precision"] <= inp["decimal_precision"]:
        raise ValueError("Cross-check precision must exceed primary precision")
    profiles = {law: conditional_profiles(law, inp["count_cutoff"]) for law in inp["coupling_laws"]}
    rows = evaluate(spec, inp["decimal_precision"], profiles)
    cross = evaluate(spec, inp["cross_precision"], profiles)
    with localcontext() as ctx:
        ctx.prec = inp["cross_precision"]
        for row, high in zip(rows, cross):
            assert (row["alpha"], row["beta"], row["law"]) == (high["alpha"], high["beta"], high["law"])
            row["cross_precision_pressure_oracle_a"] = high["pressure_oracle_a"]
            row["cross_precision_pressure_oracle_b"] = high["pressure_oracle_b"]
            row["cross_precision_trial_value"] = high["trial_value"]
            row["precision_sensitivity"] = str(max(abs(Decimal(row[field]) - Decimal(high[field]))
                                                    for field in ("pressure_oracle_a", "pressure_oracle_b", "trial_value")))
            row["cross_precision_oracle_disagreement"] = high["oracle_absolute_disagreement"]
        max_disagreement = max(Decimal(r[f]) for r in rows
                               for f in ("oracle_absolute_disagreement", "cross_precision_oracle_disagreement"))
        max_tail = max(Decimal(r["max_pressure_tail_decimal_upper"]) for r in rows)
        max_sensitivity = max(Decimal(r["precision_sensitivity"]) for r in rows)
        rejected = [r for r in rows if not r["pt_guard_accepts"]]
        accepted = [r for r in rows if r["pt_guard_accepts"]]
        valid_violations = sum(r["upper_inequality_violated_beyond_allowance"] for r in accepted)
        substantial = sum(r["raw_counterexample_margin_exceeds_threshold"] for r in rejected)
        summary = {"instances": len(rows), "positive_sign_cases_rejected": len(rejected),
                   "valid_control_cases_accepted": len(accepted),
                   "valid_control_upper_inequality_violations": valid_violations,
                   "naive_guard_accepts_all": all(r["naive_even_arity_guard_accepts"] for r in rows),
                   "naive_accepted_but_pt_ineligible": len(rejected),
                   "rejected_cases_with_certified_excess": substantial,
                   "rejected_cases_with_any_excess_beyond_allowance":
                       sum(r["upper_inequality_violated_beyond_allowance"] for r in rejected),
                   "maximum_oracle_disagreement": str(max_disagreement),
                   "maximum_analytic_pressure_tail_bound": str(max_tail),
                   "maximum_precision_sensitivity": str(max_sensitivity),
                   "maximum_rejected_excess_lower_with_allowance":
                       str(max(Decimal(r["excess_lower_with_declared_allowance"]) for r in rejected)),
                   "conditional_count_mass_checks": sum(len(p) for p in profiles.values()),
                   "arithmetic_allowance": inp["arithmetic_allowance"],
                   "tail_evidence": "Exact rational geometric majorants, dropping exp(-mean)<=1; numerical log/exp allowance is separately declared and precision-checked, not a formal interval proof",
                   "interpretation": "Nonblind synthetic applicability audit of the older PT upper certificate; no thermodynamic theorem validation or incremental solver/decoder benefit"}
        summary["meets_prediction"] = (
            len(rows) == success["cases"]
            and max_disagreement <= Decimal(success["oracle_absolute_disagreement_max"])
            and max_tail <= Decimal(success["discarded_tail_budget_max"])
            and max_sensitivity <= Decimal(inp["arithmetic_allowance"])
            and len(rejected) == success["positive_sign_cases_rejected"]
            and len(accepted) == success["valid_control_cases_accepted"]
            and valid_violations == success["valid_control_upper_inequality_violations"]
            and substantial >= success["rejected_cases_with_certified_excess_min"])
    return rows, summary
