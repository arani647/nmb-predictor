import axios from 'axios';
import { type CaseState, CasePhase } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

const client = axios.create({
    baseURL: API_BASE_URL,
});

export const fetchCases = async (): Promise<CaseState[]> => {
    const res = await client.get('/cases');
    return res.data;
};

export const fetchCase = async (id: string): Promise<CaseState> => {
    const res = await client.get(`/cases/${id}`);
    return res.data;
};

export const postPhase = async (id: string, phase: CasePhase): Promise<CaseState> => {
    const res = await client.post(`/cases/${id}/phase`, { phase });
    return res.data;
};

export const acknowledge = async (id: string, action: 'acknowledge' | 'override', note?: string): Promise<CaseState> => {
    const res = await client.post(`/cases/${id}/acknowledge`, { action, override_note: note });
    return res.data;
};

export const streamCase = (id: string, onMessage: (data: CaseState) => void): EventSource => {
    const sse = new EventSource(`${API_BASE_URL}/cases/${id}/stream`);
    sse.onmessage = (event) => {
        if (event.data === '{"message": "keepalive"}') return; // Safe ignore ping
        try {
            const parsed = JSON.parse(event.data);
            if (parsed.patient) {
                onMessage(parsed as CaseState);
            }
        } catch (e) {
            console.error("SSE parsing error:", e);
        }
    };
    return sse;
};
