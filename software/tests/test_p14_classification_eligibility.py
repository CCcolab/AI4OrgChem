from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import yaml


ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / "software/scripts/classify_p14_strained_aromatic_pi_distortivity.py"
SPEC = importlib.util.spec_from_file_location("p14_classifier", SCRIPT)
assert SPEC and SPEC.loader
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def fixtures() -> tuple[dict, dict]:
    protocol = yaml.safe_load(
        (ROOT / "configs/qm/p14_strained_aromatic_pi_distortivity_v0.1.yaml").read_text(encoding="utf-8")
    )
    record = json.loads(
        (ROOT / "evidence/P01-P14/P14/processed/p14_C12H6_five_parameter_pilot_v0.1.json").read_text(
            encoding="utf-8"
        )
    )
    return protocol, record


def qualified_record() -> tuple[dict, dict]:
    protocol, record = fixtures()
    protocol["production_calculation"]["geometry_optimization_authorized"] = True
    record["scientific_classification_allowed"] = True
    record["stage"] = "five_parameter_D3h_B3LYPG_6_31Gd_production"
    record["method"]["basis"] = "6-31g(d)"
    record["method"]["grid_level"] = protocol["production_calculation"]["grid_level"]
    for key in ("G_optimizer", "PLG_optimizer"):
        record[key]["success"] = True
        record[key]["termination_reason"] = "gradient_tolerance_satisfied"
        record[key]["gradient_max_abs_hartree_per_angstrom"] = 1.0e-3
        record[key]["active_bounds"] = []
    return protocol, record


def test_current_technical_pilot_is_not_scientifically_eligible() -> None:
    protocol, record = fixtures()
    checks = MODULE.assess_optimization_eligibility(protocol, record)
    assert not checks["optimization_scientific_classification_allowed"]
    assert checks["optimization_protocol_authorized"]
    assert not checks["optimization_stage_is_production"]
    assert not checks["optimization_basis_matches"]
    assert not checks["optimization_grid_matches"]
    assert not checks["G_gradient_within_tolerance"]
    assert not checks["PLG_gradient_within_tolerance"]
    assert not all(checks.values())


def test_optimizer_success_does_not_override_excess_gradient() -> None:
    protocol, record = qualified_record()
    record["G_optimizer"]["gradient_max_abs_hartree_per_angstrom"] = 3.0e-3
    record["G_optimizer"]["termination_reason"] = "function_tolerance_satisfied"
    checks = MODULE.assess_optimization_eligibility(protocol, record)
    assert checks["G_optimizer_success"]
    assert not checks["G_gradient_within_tolerance"]
    assert not checks["G_termination_qualified"]


def test_fully_qualified_production_record_passes() -> None:
    protocol, record = qualified_record()
    assert all(MODULE.assess_optimization_eligibility(protocol, record).values())


def test_method_or_basis_mismatch_is_rejected() -> None:
    protocol, record = qualified_record()
    wrong_method = copy.deepcopy(record)
    wrong_method["method"]["pyscf_xc"] = "PBE"
    wrong_basis = copy.deepcopy(record)
    wrong_basis["method"]["basis"] = "sto-3g"
    assert not MODULE.assess_optimization_eligibility(protocol, wrong_method)["optimization_method_matches"]
    assert not MODULE.assess_optimization_eligibility(protocol, wrong_basis)["optimization_basis_matches"]


def test_protocol_version_mismatch_is_rejected() -> None:
    protocol, record = qualified_record()
    record["protocol_id"] = "p14-strained-aromatic-pi-distortivity/wrong-version"
    assert not MODULE.assess_optimization_eligibility(protocol, record)["optimization_protocol_id_matches"]
