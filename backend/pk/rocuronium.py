import math
from models.schemas import Patient, DrugDose, TOFReading

# Constant values given by requirements
KE0 = 0.12  # min^{-1}
EC50 = 1.5  # ug/mL
GAMMA = 4.0

def _get_pk_parameters(patient: Patient) -> tuple[float, float, float, float]:
    """
    Returns (V1, V2, Cl1, Cl2) scaled for the patient.
    Base Proost parameters: V1=4.0L, V2=7.6L, Cl1=0.25L/min, Cl2=0.87L/min.
    """
    # CLINICAL_REVIEW: verify with domain expert how scaling applies to each param
    weight_factor = patient.weight_kg / 70.0
    crcl_factor = patient.crcl_ml_min / 100.0

    v1 = 4.0 * weight_factor
    v2 = 7.6 * weight_factor
    cl1 = 0.25 * weight_factor * crcl_factor
    cl2 = 0.87 * weight_factor

    return v1, v2, cl1, cl2

def _compute_micro_constants(v1: float, v2: float, cl1: float, cl2: float) -> tuple[float, float, float]:
    k10 = cl1 / v1
    k12 = cl2 / v1
    k21 = cl2 / v2
    return k10, k12, k21

def _compute_macro_constants(k10: float, k12: float, k21: float) -> tuple[float, float]:
    # Quadratic: s^2 + (k10 + k12 + k21)*s + k10*k21 = 0
    b = k10 + k12 + k21
    c = k10 * k21
    discriminant = b**2 - 4 * c
    if discriminant < 0:
        discriminant = 0  # CLINICAL_REVIEW: mathematical fallback
    
    alpha = (b + math.sqrt(discriminant)) / 2.0
    beta = (b - math.sqrt(discriminant)) / 2.0
    return alpha, beta

def plasma_concentration(patient: Patient, doses: list[DrugDose], current_time_min: float) -> float:
    # CLINICAL_REVIEW: verify with domain expert
    v1, v2, cl1, cl2 = _get_pk_parameters(patient)
    k10, k12, k21 = _compute_micro_constants(v1, v2, cl1, cl2)
    alpha, beta = _compute_macro_constants(k10, k12, k21)

    conc = 0.0
    for d in doses:
        if d.drug != "rocuronium":
            continue
        dt = current_time_min - d.time_min
        if dt < 0:
            continue
        
        dose = d.dose_mg
        
        # Avoid division by zero
        if alpha == beta:
            continue
            
        A = (dose / v1) * (k21 - alpha) / (beta - alpha)
        B = (dose / v1) * (k21 - beta) / (alpha - beta)
        
        conc += A * math.exp(-alpha * dt) + B * math.exp(-beta * dt)
    return max(0.0, conc)

def effect_site_concentration(patient: Patient, doses: list[DrugDose], current_time_min: float) -> float:
    # CLINICAL_REVIEW: verify with domain expert
    v1, v2, cl1, cl2 = _get_pk_parameters(patient)
    k10, k12, k21 = _compute_micro_constants(v1, v2, cl1, cl2)
    alpha, beta = _compute_macro_constants(k10, k12, k21)
    
    conc = 0.0
    for d in doses:
        if d.drug != "rocuronium":
            continue
        dt = current_time_min - d.time_min
        if dt < 0:
            continue
            
        dose = d.dose_mg
        coef = (dose / v1) * KE0
        
        try:
            A_e = (k21 - alpha) / ((beta - alpha) * (KE0 - alpha))
            B_e = (k21 - beta) / ((alpha - beta) * (KE0 - beta))
            C_e = (k21 - KE0) / ((alpha - KE0) * (beta - KE0))
            
            val = coef * (
                A_e * math.exp(-alpha * dt) +
                B_e * math.exp(-beta * dt) +
                C_e * math.exp(-KE0 * dt)
            )
            conc += val
        except ZeroDivisionError:
            # CLINICAL_REVIEW: verify fallback logic
            pass 

    return max(0.0, conc)

def tof_from_effect_site(ce: float) -> float:
    # CLINICAL_REVIEW: verify with domain expert - exact formula mapping residency to 0-1
    if ce < 0: ce = 0.0
    if ce == 0: return 1.0
    
    occupancy = (ce ** GAMMA) / ((ce ** GAMMA) + (EC50 ** GAMMA))
    tof = 1.0 - occupancy 
    return max(0.0, min(1.0, tof))

def compute_tof_trajectory(patient: Patient, doses: list[DrugDose], end_time_min: float) -> list[TOFReading]:
    trajectory = []
    # Using integer steps from min time to end time
    if not doses:
        return []
    
    start_time = min(d.time_min for d in doses)
    t = start_time
    while t <= end_time_min:
        ce = effect_site_concentration(patient, doses, t)
        tof = tof_from_effect_site(ce)
        trajectory.append(TOFReading(time_min=t, tof_ratio=tof, source='model'))
        t += 1.0
    return trajectory
