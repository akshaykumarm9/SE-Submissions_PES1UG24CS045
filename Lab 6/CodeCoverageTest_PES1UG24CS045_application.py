
import pytest
from warranty_claims import (
    out_of_warranty_charge,
    claim_allowed,
    sla_status,
)


# Tests for out_of_warranty_charge()

def test_unknown_plan():
    with pytest.raises(ValueError, match="unknown plan"):
        out_of_warranty_charge("gold", 10, "defect", False)


def test_negative_age():
    with pytest.raises(ValueError, match="invalid age"):
        out_of_warranty_charge("basic", -1, "defect", False)


def test_within_warranty():
    assert out_of_warranty_charge("standard", 20, "defect", False) == 0


def test_registered_basic_warranty_extension():
    assert out_of_warranty_charge("basic", 15, "defect", True) == 0


def test_premium_registration_no_extension():
    assert out_of_warranty_charge("premium", 37, "defect", True) == 100


def test_accidental_claim_charge():
    assert out_of_warranty_charge("basic", 13, "accidental", False) == 200


def test_non_accidental_claim_charge():
    assert out_of_warranty_charge("basic", 13, "defect", False) == 100


def test_excess_over_12_months_defect():
    assert out_of_warranty_charge("basic", 25, "defect", False) == 1950


def test_excess_over_12_months_accidental():
    assert out_of_warranty_charge("basic", 25, "accidental", False) == 3575

# Tests for claim_allowed()

def test_recall_with_five_claims_allowed():
    assert claim_allowed(10, 5, True) is True


def test_recall_with_six_claims_rejected():
    assert claim_allowed(10, 6, True) is False


def test_recent_claim_rejected():
    assert claim_allowed(29, 1, False) is False


def test_old_claim_with_two_claims_allowed():
    assert claim_allowed(30, 2, False) is True


def test_old_claim_with_three_claims_rejected():
    assert claim_allowed(30, 3, False) is False


# Tests for sla_status()

def test_hardware_on_track():
    assert sla_status(48, True, False) == "on_track"


def test_non_hardware_at_risk():
    assert sla_status(12, False, False) == "at_risk"


def test_non_hardware_critical():
    assert sla_status(11, False, False) == "critical"


def test_priority_hardware_on_track():
    assert sla_status(72, True, True) == "on_track"


def test_priority_non_hardware_at_risk():
    assert sla_status(36, False, True) == "at_risk"


def test_priority_non_hardware_critical():
    assert sla_status(35, False, True) == "critical"
