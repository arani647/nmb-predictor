import numpy as np
from models.schemas import Patient, DrugDose, CaseState, CasePhase, PKState
from pk.rocuronium import plasma_concentration, effect_site_concentration, tof_from_effect_site

# Rule 4: Seed np.random(42) and use synthetic floats
np.random.seed(42)

class SimulatorAgent:
    def create_case(self, name: str, age: int, weight_kg: float, crcl_ml_min: float, case_type: str) -> CaseState:
        patient = Patient(
            name=name, 
            age=age, 
            weight_kg=weight_kg, 
            height_cm=165.0,  # synthetic assumed bounds
            crcl_ml_min=crcl_ml_min, 
            asa_class=2, 
            case_type=case_type
        )
        return CaseState(patient=patient, phase=CasePhase.MAINTENANCE, elapsed_min=0.0)

    def standard_doses_for(self, patient: Patient) -> list[DrugDose]:
        # Typical mg/kg rocuronium induction + maintenance topup
        induction_mg = patient.weight_kg * 0.6
        return [
            DrugDose(drug="rocuronium", dose_mg=induction_mg, time_min=0.0),
            DrugDose(drug="rocuronium", dose_mg=induction_mg * 0.25, time_min=45.0)
        ]

    def advance_case(self, state: CaseState, dt: float) -> CaseState:
        # Rule 2: NEVER mutate CaseState in place. Use model_copy.
        new_time = state.elapsed_min + dt
        
        pc = plasma_concentration(state.patient, state.doses, new_time)
        ec = effect_site_concentration(state.patient, state.doses, new_time)
        tof = tof_from_effect_site(ec)
        
        pk = PKState(
            plasma_conc_ug_ml=pc,
            effect_site_conc_ug_ml=ec,
            tof_ratio=tof,
            neostigmine_ceiling=False,  # Stubbed; PKAgent handles this
            max_tof_with_neostigmine=1.0  # Stubbed
        )
        
        return state.model_copy(update={"elapsed_min": new_time, "pk_state": pk})

    def initialize_demo_cases(self) -> list[CaseState]:
        # 3 Archetypes
        c1 = self.create_case("Alex Chen", 42, 78.0, 98.0, "lap chole")
        c2 = self.create_case("Margaret Walsh", 74, 61.0, 36.0, "TKR")
        c3 = self.create_case("Robert Torres", 55, 138.0, 82.0, "sleeve")
        
        cases = [c1, c2, c3]
        dosed_cases = [c.model_copy(update={"doses": self.standard_doses_for(c.patient)}) for c in cases]
        
        # Advance to elapsed_min=85
        return [self.advance_case(c, 85.0) for c in dosed_cases]

if __name__ == "__main__":
    sim = SimulatorAgent()
    cases = sim.initialize_demo_cases()
    walsh = cases[1]
    
    val = walsh.pk_state.tof_ratio
    assert 0.55 <= val <= 0.85, f"Walsh TOF out of expected block bounds: {val}"
    print(f"SimulatorAgent OK. Walsh pk_state.tof_ratio={val:.3f}")
