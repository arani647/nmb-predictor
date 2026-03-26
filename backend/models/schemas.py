import uuid
from enum import Enum
from typing import Literal
from pydantic import BaseModel, Field

class CasePhase(str, Enum):
    INDUCTION = "INDUCTION"
    MAINTENANCE = "MAINTENANCE"
    CLOSING = "CLOSING"
    EXTUBATED = "EXTUBATED"

class Patient(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    name: str
    age: int = Field(ge=18, le=100)
    weight_kg: float = Field(ge=30.0, le=250.0)
    height_cm: float = Field(ge=140.0, le=220.0)
    crcl_ml_min: float = Field(ge=10.0, le=150.0)
    asa_class: int = Field(ge=1, le=4)
    case_type: str

class DrugDose(BaseModel):
    drug: Literal['rocuronium', 'neostigmine', 'sugammadex']
    dose_mg: float
    time_min: float

class TOFReading(BaseModel):
    time_min: float
    tof_ratio: float = Field(ge=0.0, le=1.0)
    source: Literal['model', 'measured']

class PKState(BaseModel):
    plasma_conc_ug_ml: float
    effect_site_conc_ug_ml: float
    tof_ratio: float
    neostigmine_ceiling: bool
    max_tof_with_neostigmine: float

class ReversalRecommendation(BaseModel):
    id: uuid.UUID = Field(default_factory=uuid.uuid4)
    agent: Literal['sugammadex', 'neostigmine', 'wait']
    dose_mg: float
    rationale: str
    time_to_tof_0_9_min: float
    neostigmine_contraindicated: bool
    sugammadex_cost_usd: float = 50.0
    complication_probability: float
    expected_complication_cost_usd: float
    net_roi_usd: float

class CaseState(BaseModel):
    patient: Patient
    doses: list[DrugDose] = Field(default_factory=list)
    tof_history: list[TOFReading] = Field(default_factory=list)
    phase: CasePhase
    elapsed_min: float
    pk_state: PKState | None = None
    recommendation: ReversalRecommendation | None = None
    acknowledged: bool = False
    override_note: str | None = None

class AcknowledgeRequest(BaseModel):
    case_id: uuid.UUID
    action: Literal['acknowledge', 'override']
    override_note: str | None = None
    override_agent: str | None = None
