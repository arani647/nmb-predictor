import { useEffect, useState } from 'react';
import { fetchCases, streamCase, postPhase, acknowledge } from './api/client';
import { type CaseState, CasePhase } from './types';
import { Dashboard } from './components/Dashboard';
import { PatientModal } from './components/PatientModal';

export default function App() {
  const [cases, setCases] = useState<CaseState[]>([]);
  const [selectedId, setSelectedId] = useState<string | null>(null);

  useEffect(() => {
    let eventSources: EventSource[] = [];
    const init = async () => {
      try {
        const initialCases = await fetchCases();
        setCases(initialCases);

        initialCases.forEach(c => {
          const sse = streamCase(c.patient.id, (updatedCase) => {
            setCases(prev => prev.map(p => p.patient.id === updatedCase.patient.id ? updatedCase : p));
          });
          eventSources.push(sse);
        });
      } catch (e) {
        console.error("Fetch cases failed:", e);
      }
    };
    init();

    return () => {
      eventSources.forEach(sse => sse.close());
    };
  }, []);

  const handleSelectCase = (id: string) => setSelectedId(id);
  const handleCloseModal = () => setSelectedId(null);

  // Demo Dev Hook
  const handleOverridePhase = async (id: string) => {
    try {
      const updated = await postPhase(id, CasePhase.CLOSING);
      setCases(prev => prev.map(p => p.patient.id === id ? updated : p));
    } catch (e) {
      console.error("Phase override failed", e);
    }
  };

  const handleAcknowledge = async (action: 'acknowledge' | 'override', note?: string) => {
    if (!selectedId) return;
    try {
      const updated = await acknowledge(selectedId, action, note);
      setCases(prev => prev.map(p => p.patient.id === selectedId ? updated : p));
      // Force modal close or just let it update reactively
    } catch (e) { }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col font-sans">
      <Dashboard cases={cases} onSelectCase={handleSelectCase} />

      <div className="p-6 bg-white border-t border-gray-200 mt-auto text-center shadow-inner">
        <h3 className="font-extrabold text-gray-400 mb-4 uppercase text-xs tracking-widest">Demo Environment Triggers</h3>
        {cases.filter(c => c.patient.name === "Margaret Walsh").map(walsh => (
          <button
            key={"dev-" + walsh.patient.id}
            id="btn-post-walsh"
            onClick={() => handleOverridePhase(walsh.patient.id)}
            className="bg-purple-600 text-white px-6 py-3 rounded-full font-extrabold hover:bg-purple-700 shadow-md transition-all active:scale-95 text-sm"
          >
            POST Walsh to phase=CLOSING
          </button>
        ))}
      </div>

      {selectedId && (
        <PatientModal
          caseState={cases.find(c => c.patient.id === selectedId)!}
          onClose={handleCloseModal}
          onAcknowledge={handleAcknowledge}
        />
      )}
    </div>
  );
}
