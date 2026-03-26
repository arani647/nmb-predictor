export enum CasePhase {
    INDUCTION = "INDUCTION",
    MAINTENANCE = "MAINTENANCE",
    CLOSING = "CLOSING",
    EXTUBATED = "EXTUBATED"
}

export interface Patient {
    id: string;
    name: string;
    age: number;
    weight_kg: number;
    height_cm: number;
    crcl_ml_min: number;
    asa_class: number;
    case_type: string;
}

export interface DrugDose {
    drug: 'rocuronium' | 'neostigmine' | 'sugammadex';
    dose_mg: number;
    time_min: number;
}

export interface TOFReading {
    time_min: number;
    tof_ratio: number;
    source: 'model' | 'measured';
}

export interface PKState {
    plasma_conc_ug_ml: number;
    effect_site_conc_ug_ml: number;
    tof_ratio: number;
    neostigmine_ceiling: boolean;
    max_tof_with_neostigmine: number;
}

export interface ReversalRecommendation {
    id: string;
    agent: 'sugammadex' | 'neostigmine' | 'wait';
    dose_mg: number;
    rationale: string;
    time_to_tof_0_9_min: number;
    neostigmine_contraindicated: boolean;
    sugammadex_cost_usd: number;
    complication_probability: number;
    expected_complication_cost_usd: number;
    net_roi_usd: number;
}

export interface CaseState {
    patient: Patient;
    doses: DrugDose[];
    tof_history: TOFReading[];
    phase: CasePhase;
    elapsed_min: number;
    pk_state: PKState | null;
    recommendation: ReversalRecommendation | null;
    acknowledged: boolean;
    override_note: string | null;
}
