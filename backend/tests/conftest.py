import pytest
import uuid
from models.schemas import Patient, CaseState, CasePhase, DrugDose

@pytest.fixture
def patient_normal() -> Patient:
    return Patient(
        id=uuid.uuid4(),
        name="Normal Patient",
        age=45,
        weight_kg=75.0,
        height_cm=175.0,
        crcl_ml_min=95.0,
        asa_class=1,
        case_type="General"
    )

@pytest.fixture
def patient_elderly() -> Patient:
    return Patient(
        id=uuid.uuid4(),
        name="Elderly Patient",
        age=74,
        weight_kg=61.0,
        height_cm=165.0,
        crcl_ml_min=36.0,
        asa_class=3,
        case_type="General"
    )

@pytest.fixture
def patient_obese() -> Patient:
    return Patient(
        id=uuid.uuid4(),
        name="Obese Patient",
        age=52,
        weight_kg=138.0,
        height_cm=165.0,
        crcl_ml_min=82.0,
        asa_class=3,
        case_type="Bariatric"
    )

@pytest.fixture
def case_state_closing(patient_elderly: Patient) -> CaseState:
    doses = [
        DrugDose(drug="rocuronium", dose_mg=50.0, time_min=0.0),
        DrugDose(drug="rocuronium", dose_mg=20.0, time_min=45.0)
    ]
    return CaseState(
        patient=patient_elderly,
        phase=CasePhase.CLOSING,
        elapsed_min=85.0,
        doses=doses
    )
