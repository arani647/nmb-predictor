from fastapi.testclient import TestClient
from main import app
import json
import os

def run_tests():
    # TestClient invokes @app.on_event("startup")
    with TestClient(app) as client:
        res = client.get("/cases")
        cases = res.json()
        assert len(cases) == 3, f"Expected 3 demo cases at startup, got {len(cases)}"
        
        walsh_id = None
        for c in cases:
            if c['patient']['name'] == 'Margaret Walsh':
                walsh_id = c['patient']['id']
                assert 'pk_state' in c
                assert c['pk_state'] is not None, "PKState not populated"
                break
                
        assert walsh_id is not None, "Walsh case not mapped in startup"
        
        # Test Phase transition trigger API
        res = client.post(f"/cases/{walsh_id}/phase", json={"phase": "CLOSING"})
        assert res.status_code == 200, res.text
        walsh_case = res.json()
        
        rec = walsh_case.get('recommendation')
        assert rec is not None, "No recommendation built during Phase switch"
        assert rec['agent'] == 'sugammadex', f"Expected sugammadex, got {rec['agent']}"
        
        print("Walsh API processing OK.")
        print(f"Rationale Evaluated via API: {rec['rationale']}")
        
        # Force writing abstract explicitly to brain folder
        output_path = os.path.join(
            "C:\\Users\\anant\\.gemini\\antigravity\\brain\\545898ce-8857-4f8e-8d2d-752e725a9c13",
            "walsh_api_artifact.json"
        )
        with open(output_path, 'w') as f:
            json.dump(walsh_case, f, indent=2)
            
if __name__ == "__main__":
    run_tests()
