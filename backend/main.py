import os
import uuid
import asyncio
from typing import List, Dict

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from dotenv import load_dotenv
load_dotenv()

from models.schemas import CaseState, ReversalRecommendation, Patient, CasePhase
from agents.simulator_agent import SimulatorAgent
from agents.pk_agent import PKAgent
from agents.reversal_agent import ReversalAgent

app = FastAPI(title="NMB Predictor")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

simulator = SimulatorAgent()
pk_agent = PKAgent()
reversal_agent = ReversalAgent()

CASES: Dict[str, CaseState] = {}

class PhaseUpdateReq(BaseModel):
    phase: CasePhase

@app.on_event('startup')
async def startup_event():
    demo_cases = simulator.initialize_demo_cases()
    for case in demo_cases:
        cid = str(case.patient.id)
        CASES[cid] = pk_agent.update_case_with_pk(case)

@app.get("/health")
def health() -> dict:
    return {"status": "ok"}

@app.get("/cases", response_model=List[CaseState])
def get_cases() -> List[CaseState]:
    return list(CASES.values())

@app.post("/cases/start", response_model=CaseState)
def start_case() -> CaseState:
    state = CaseState(
        patient=Patient(name="Stub", age=45, weight_kg=70.0, crcl_ml_min=100.0, height_cm=170.0, asa_class=1, case_type="General"),
        phase=CasePhase.INDUCTION,
        elapsed_min=0.0
    )
    CASES[str(state.patient.id)] = state
    return state

@app.get("/cases/{id}", response_model=CaseState)
def get_case(id: str) -> CaseState:
    if id not in CASES:
        raise HTTPException(status_code=404, detail="Case not found")
    return CASES[id]

@app.post("/cases/{id}/dose", response_model=CaseState)
def add_dose(id: str) -> CaseState:
    if id not in CASES:
        raise HTTPException(status_code=404)
    return CASES[id]

@app.post("/cases/{id}/phase", response_model=CaseState)
def update_phase(id: str, req: PhaseUpdateReq) -> CaseState:
    if id not in CASES:
        raise HTTPException(status_code=404)
        
    state = CASES[id]
    state = state.model_copy(update={"phase": req.phase})
    
    if req.phase == CasePhase.CLOSING:
        state = pk_agent.update_case_with_pk(state)
        if pk_agent.should_recommend(state):
            rec = reversal_agent.generate_recommendation(state)
            state = state.model_copy(update={"recommendation": rec})
            
    CASES[id] = state
    return state

@app.post("/cases/{id}/acknowledge", response_model=CaseState)
def acknowledge(id: str) -> CaseState:
    if id not in CASES:
        raise HTTPException(status_code=404)
    return CASES[id]

@app.get("/cases/{id}/recommend", response_model=ReversalRecommendation)
def recommend(id: str) -> ReversalRecommendation:
    if id not in CASES:
        raise HTTPException(status_code=404)
    if not CASES[id].recommendation:
        raise HTTPException(status_code=400, detail="No recommendation generated")
    return CASES[id].recommendation

@app.get("/cases/{id}/stream")
async def stream_case(id: str, request: Request):
    if id not in CASES:
        raise HTTPException(status_code=404)
        
    async def event_generator():
        try:
            ticks = 0
            while True:
                await asyncio.sleep(5.0)
                ticks += 5
                if await request.is_disconnected():
                    break
                
                # SSE Stream constraint: Call PK model, DO NOT call reversal logic 
                if id in CASES:
                    state = CASES[id]
                    updated_state = pk_agent.update_case_with_pk(state)
                    CASES[id] = updated_state
                    
                if ticks % 25 == 0:
                    yield "event: ping\ndata: {\"message\": \"keepalive\"}\n\n"
                
                yield f"data: {{\"tick\": {ticks}}}\n\n"
        except asyncio.CancelledError:
            pass
            
    return StreamingResponse(event_generator(), media_type="text/event-stream")
