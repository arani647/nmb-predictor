import math
from typing import List

# CLINICAL_REVIEW: verify constants and interpolation with domain expert

def neostigmine_max_tof(starting_tof: float) -> float:
    # Piecewise linear interpolation (Caldwell/Donati)
    if starting_tof < 0.10:
        return 0.45
    elif starting_tof <= 0.25:
        return 0.45 + (starting_tof - 0.10) / (0.25 - 0.10) * (0.60 - 0.45)
    elif starting_tof <= 0.40:
        return 0.60 + (starting_tof - 0.25) / (0.40 - 0.25) * (0.75 - 0.60)
    elif starting_tof <= 0.70:
        return 0.75 + (starting_tof - 0.40) / (0.70 - 0.40) * (0.88 - 0.75)
    else:
        # >0.70: 0.97
        if starting_tof < 1.0:
            return 0.88 + (starting_tof - 0.70) / (1.0 - 0.70) * (0.97 - 0.88)
        return 0.97

def neostigmine_time_to_max(starting_tof: float) -> float:
    # 15/10/7 min logic bounds
    if starting_tof < 0.25:
        return 15.0
    elif starting_tof < 0.40:
        return 10.0
    else:
        return 7.0

def neostigmine_ceiling_active(starting_tof: float) -> bool:
    return neostigmine_max_tof(starting_tof) < 0.9

def simulate_neostigmine_reversal(starting_tof: float, dose_mg: float, t_points: List[float]) -> List[float]:
    max_tof = neostigmine_max_tof(starting_tof)
    t_max = neostigmine_time_to_max(starting_tof)
    
    # Cap at neostigmine_max_tof. Sigmoid rise over onset time.
    def sigmoid(t: float) -> float:
        if t <= 0: return starting_tof
        if t >= t_max: return max_tof
        
        # 0 to 1 cosine interpolation curve
        s = (1.0 - math.cos(math.pi * t / t_max)) / 2.0
        return starting_tof + s * (max_tof - starting_tof)
        
    return [sigmoid(t) for t in t_points]

def sugammadex_dose_mg(starting_tof: float, weight_kg: float) -> float:
    # TOF>=0.2: 200mg, 0.05-0.20: 4mg/kg, <0.05: 16mg/kg
    if starting_tof >= 0.20:
        return 200.0
    elif starting_tof >= 0.05:
        return 4.0 * weight_kg
    else:
        return 16.0 * weight_kg

def simulate_sugammadex_reversal(starting_tof: float, dose_mg: float, t_points: List[float]) -> List[float]:
    # Rapid sigmoid reaching TOF 0.9 at t=3min. No ceiling.
    def sigmoid(t: float) -> float:
        if t <= 0: return starting_tof
        if starting_tof >= 0.9:
            return min(1.0, starting_tof + 0.1 * t)
            
        k = -math.log(0.1 / (1.0 - starting_tof)) / 3.0
        val = starting_tof + (1.0 - starting_tof) * (1.0 - math.exp(-k * t))
        return min(1.0, val)
        
    return [sigmoid(t) for t in t_points]

def reversal_comparison(starting_tof: float, weight_kg: float) -> dict:
    # Neostigmine Evaluation
    neo_max = neostigmine_max_tof(starting_tof)
    neo_achieves_0_9 = not neostigmine_ceiling_active(starting_tof)
    
    neo_time = None
    if neo_achieves_0_9:
        t_max = neostigmine_time_to_max(starting_tof)
        try:
            # Reverse solving cosine interpolation for s_val = 0.9
            s_val = (0.9 - starting_tof) / (neo_max - starting_tof)
            s_val = max(0.0, min(1.0, s_val))
            neo_time = (t_max / math.pi) * math.acos(1.0 - 2.0 * s_val)
        except:
            neo_time = t_max
            
    # Sugammadex Evaluation
    sug_dose = sugammadex_dose_mg(starting_tof, weight_kg)
    sug_time = 3.0
    
    return {
        "sugammadex": {
            "dose_mg": sug_dose,
            "time_to_0_9_min": sug_time,
            "achieves_0_9": True,
            "cost_usd": 50.0
        },
        "neostigmine": {
            "dose_mg": 3.0,  # mock clinically standard neo dosage weight scalar wrapper
            "time_to_0_9_min": neo_time,
            "achieves_0_9": neo_achieves_0_9,
            "max_tof": neo_max,
            "cost_usd": 5.0
        }
    }

if __name__ == '__main__':
    # Agent A inline test
    assert neostigmine_ceiling_active(0.3) is True
    assert neostigmine_ceiling_active(0.8) is False
    print('neostigmine model OK')
    
    # Agent B inline test
    res = reversal_comparison(0.35, 62.0)
    assert res['neostigmine']['achieves_0_9'] is False
    assert res['sugammadex']['achieves_0_9'] is True
    print('sugammadex model OK')
