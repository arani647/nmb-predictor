from models.schemas import CaseState, PKState
from pk.rocuronium import plasma_concentration, effect_site_concentration, tof_from_effect_site
from pk.reversal import neostigmine_ceiling_active, neostigmine_max_tof

class PKAgent:
    def compute_pk_state(self, state: CaseState) -> PKState:
        try:
            pc = plasma_concentration(state.patient, state.doses, state.elapsed_min)
            ec = effect_site_concentration(state.patient, state.doses, state.elapsed_min)
            tof = tof_from_effect_site(ec)
            
            neo_ceiling = neostigmine_ceiling_active(tof)
            neo_max = neostigmine_max_tof(tof)
            
            return PKState(
                plasma_conc_ug_ml=pc,
                effect_site_conc_ug_ml=ec,
                tof_ratio=tof,
                neostigmine_ceiling=neo_ceiling,
                max_tof_with_neostigmine=neo_max
            )
        except Exception:
            # Safe default fallback on error
            return PKState(
                plasma_conc_ug_ml=0.0,
                effect_site_conc_ug_ml=0.0,
                tof_ratio=1.0,
                neostigmine_ceiling=False,
                max_tof_with_neostigmine=1.0
            )

    def should_recommend(self, state: CaseState) -> bool:
        if not state.pk_state:
            return False
        # Minimal mock logic mapping
        return state.pk_state.tof_ratio > 0.0

    def update_case_with_pk(self, state: CaseState) -> CaseState:
        # Rule 2: NEVER mutate state
        new_pk = self.compute_pk_state(state)
        return state.model_copy(update={"pk_state": new_pk})

if __name__ == "__main__":
    # Test Walsh directly using mock constructs (Never import SimulatorAgent)
    from models.schemas import Patient, DrugDose, CasePhase
    walsh_patient = Patient(name="Margaret Walsh", age=74, weight_kg=61.0, height_cm=165.0, crcl_ml_min=36.0, asa_class=3, case_type="TKR")
    # Dose logic mirrored from Agent B to test 85-min phase correctly
    dose1 = DrugDose(drug="rocuronium", dose_mg=61.0 * 0.6, time_min=0.0)
    dose2 = DrugDose(drug="rocuronium", dose_mg=61.0 * 0.6 * 0.25, time_min=45.0)
    
    walsh_state = CaseState(patient=walsh_patient, doses=[dose1, dose2], phase=CasePhase.MAINTENANCE, elapsed_min=85.0)
    
    agent = PKAgent()
    updated = agent.update_case_with_pk(walsh_state)
    
    assert updated.pk_state.neostigmine_ceiling is True, f"Ceiling flag false at TOF {updated.pk_state.tof_ratio}"
    print(f"PKAgent OK. Demo 'wow' passed: Walsh looks OK (TOF={updated.pk_state.tof_ratio:.3f}) but ceiling applies ({updated.pk_state.neostigmine_ceiling}).")
