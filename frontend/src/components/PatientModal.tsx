import React, { useState } from 'react';
import { Line } from 'react-chartjs-2';
import type { CaseState } from '../types';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Title, Tooltip, Legend);

interface Props {
    caseState: CaseState;
    onClose: () => void;
    onAcknowledge: (action: 'acknowledge' | 'override', note?: string) => void;
}

export const PatientModal: React.FC<Props> = ({ caseState, onClose, onAcknowledge }) => {
    const [overrideNote, setOverrideNote] = useState('');
    const [actionType, setActionType] = useState<'acknowledge' | 'override'>('acknowledge');

    const tofHistory = caseState.tof_history || [];
    const labels = tofHistory.map(t => t.time_min.toFixed(0));
    const dataPoints = tofHistory.map(t => t.tof_ratio);

    const chartData = {
        labels,
        datasets: [{
            label: 'Pharmacokinetic TOF Ratio',
            data: dataPoints,
            borderColor: 'rgb(59, 130, 246)',
            backgroundColor: 'rgba(59, 130, 246, 0.05)',
            fill: true,
            tension: 0.4,
            pointRadius: 0,
            borderWidth: 3,
        }],
    };

    const chartOptions: any = {
        responsive: true,
        interaction: { intersect: false, mode: 'index' as const },
        plugins: { legend: { display: false }, title: { display: false } },
        scales: { y: { min: 0, max: 1.2, grid: { borderDash: [4, 4] } }, x: { grid: { display: false } } }
    };

    const rec = caseState.recommendation;

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 sm:p-6">
            <div className="absolute inset-0 bg-slate-900/30 backdrop-blur-md" onClick={onClose}></div>

            <div className="relative bg-white/95 backdrop-blur-2xl rounded-[2rem] shadow-[0_20px_60px_-15px_rgba(0,0,0,0.3)] w-full max-w-6xl max-h-[92vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-300 border border-white/50">
                <div className="px-8 py-5 flex justify-between items-center bg-transparent z-10">
                    <div>
                        <h2 className="text-3xl font-extrabold tracking-tight text-slate-800">{caseState.patient.name}</h2>
                        <div className="flex items-center gap-3 mt-1.5">
                            <span className="px-3 py-1 rounded-full bg-slate-100 text-slate-600 text-[10px] font-black tracking-widest uppercase">{caseState.phase}</span>
                            <span className="text-xs font-semibold text-slate-400">T+{caseState.elapsed_min.toFixed(1)}m</span>
                        </div>
                    </div>
                    <button onClick={onClose} className="w-10 h-10 flex items-center justify-center rounded-full bg-slate-100 hover:bg-slate-200 text-slate-500 transition-colors outline-none">&times;</button>
                </div>

                <div className="px-8 pb-8 pt-2 grid grid-cols-1 lg:grid-cols-5 gap-8 overflow-y-auto">
                    {/* Left Analytical Context */}
                    <div className="lg:col-span-3 space-y-6 flex flex-col">
                        <div className="bg-white rounded-3xl p-7 border border-slate-100 shadow-[0_4px_20px_rgb(0,0,0,0.03)] flex-grow">
                            <h3 className="text-xs font-bold text-slate-400 uppercase tracking-widest mb-6">Receptor Dynamics</h3>
                            <Line options={chartOptions} data={chartData} />

                            <div className="mt-8 pt-5 border-t border-slate-100">
                                <h4 className="text-[10px] font-extrabold text-slate-400 uppercase tracking-widest mb-3">Infusion Log History</h4>
                                <div className="flex flex-wrap gap-2">
                                    {caseState.doses.map((d, i) => (
                                        <span key={i} className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-xl bg-blue-50/80 text-blue-700 text-xs font-bold border border-blue-100/50">
                                            <span className="w-1.5 h-1.5 rounded-full bg-blue-500"></span>
                                            {d.drug} {d.dose_mg.toFixed(1)}mg @ {d.time_min}m
                                        </span>
                                    ))}
                                </div>
                            </div>
                        </div>

                        <div className="bg-gradient-to-br from-slate-50 to-slate-100 rounded-3xl p-7 border border-slate-200/60 shadow-inner">
                            <h3 className="text-[10px] font-extrabold text-slate-500 uppercase tracking-widest mb-5">Value Economics Tracker</h3>
                            {rec ? (
                                <div className="space-y-4 font-medium text-sm">
                                    <div className="flex justify-between items-center text-slate-600">
                                        <span>Agent Payload Limit Cost</span>
                                        <span className="font-mono text-rose-500 bg-rose-50 px-2 py-0.5 rounded-md">-${rec.sugammadex_cost_usd.toFixed(2)}</span>
                                    </div>
                                    <div className="flex justify-between items-center text-slate-600">
                                        <span>Complication Risk Deferred</span>
                                        <span className="font-mono text-emerald-600 bg-emerald-50 px-2 py-0.5 rounded-md">+${rec.expected_complication_cost_usd.toFixed(2)}</span>
                                    </div>
                                    <div className="border-t border-slate-200 pt-4 mt-4 flex justify-between items-center">
                                        <span className="text-slate-800 font-extrabold text-lg">Net Case ROI</span>
                                        <span className="text-2xl font-mono font-black text-emerald-500 tracking-tight">${rec.net_roi_usd.toFixed(2)}</span>
                                    </div>
                                </div>
                            ) : (
                                <p className="text-sm text-slate-400 italic">Awaiting AI gating parameters...</p>
                            )}
                        </div>
                    </div>

                    {/* Right HITL Column */}
                    <div className="lg:col-span-2 space-y-6 flex flex-col h-full">
                        {rec && !caseState.acknowledged ? (
                            <div className="flex flex-col bg-gradient-to-br from-rose-50/50 to-orange-50/30 border border-orange-200/60 rounded-3xl p-7 shadow-sm h-full relative overflow-hidden">
                                {/* Decorative gradient flare */}
                                <div className="absolute top-0 right-0 w-32 h-32 bg-orange-400/10 rounded-full blur-2xl"></div>

                                <div className="flex items-center gap-3 mb-6 relative z-10">
                                    <span className="relative flex h-4 w-4">
                                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-rose-400 opacity-75"></span>
                                        <span className="relative inline-flex rounded-full h-3 w-3 bg-rose-500 m-0.5"></span>
                                    </span>
                                    <h3 className="text-xl font-extrabold text-slate-900 tracking-tight">AI Protocol Rendered</h3>
                                </div>

                                <div className="bg-white p-5 rounded-2xl border border-orange-100 shadow-[0_4px_20px_rgba(0,0,0,0.02)] mb-6 text-slate-700 leading-relaxed font-serif text-[15px] relative z-10">
                                    <p>{rec.rationale}</p>
                                </div>

                                <div className="grid grid-cols-2 gap-4 mb-8">
                                    <div className="bg-white/60 p-4 rounded-xl border border-rose-100/50">
                                        <span className="text-[10px] font-black text-rose-400 uppercase tracking-widest block mb-1">Target Agent</span>
                                        <span className="font-extrabold text-slate-800 text-lg">{rec.agent.toUpperCase()}</span>
                                    </div>
                                    <div className="bg-white/60 p-4 rounded-xl border border-rose-100/50">
                                        <span className="text-[10px] font-black text-rose-400 uppercase tracking-widest block mb-1">Dose Target</span>
                                        <span className="font-extrabold text-slate-800 text-lg">{rec.dose_mg.toFixed(1)} <span className="text-xs">mg</span></span>
                                    </div>
                                </div>

                                <div className="mt-auto bg-white rounded-2xl p-5 shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-slate-100 relative z-10">
                                    <h4 className="font-bold text-slate-800 mb-4 text-sm">HITL Security Gate</h4>
                                    <select
                                        className="w-full mb-4 px-4 py-3 bg-slate-50 border border-slate-100 rounded-xl text-slate-700 text-sm font-bold focus:bg-white focus:border-rose-400 focus:ring-2 focus:ring-rose-100 transition-all outline-none"
                                        value={actionType}
                                        onChange={(e) => setActionType(e.target.value as any)}
                                    >
                                        <option value="acknowledge">Acknowledge & Sign Protocol</option>
                                        <option value="override">Override AI Target</option>
                                    </select>

                                    {actionType === 'override' && (
                                        <textarea
                                            className="w-full mb-4 p-4 bg-slate-50 border border-slate-100 rounded-xl focus:bg-white focus:border-rose-400 transition-all text-sm outline-none"
                                            placeholder="Justification required for logging..."
                                            rows={2}
                                            value={overrideNote}
                                            onChange={e => setOverrideNote(e.target.value)}
                                        />
                                    )}

                                    <button
                                        className={`w-full py-3.5 rounded-xl font-bold text-white shadow-lg transition-all hover:-translate-y-0.5 active:translate-y-0 duration-300 ${actionType === 'acknowledge' ? 'bg-slate-900 hover:bg-slate-800 shadow-slate-900/20' : 'bg-rose-500 hover:bg-rose-600 shadow-rose-500/20'}`}
                                        onClick={() => onAcknowledge(actionType, actionType === 'override' ? overrideNote : undefined)}
                                    >
                                        {actionType === 'acknowledge' ? 'Authenticate Validation' : 'Execute System Override'}
                                    </button>
                                </div>
                            </div>
                        ) : caseState.acknowledged ? (
                            <div className="flex flex-col items-center justify-center bg-emerald-50/50 border border-emerald-100 rounded-3xl p-8 text-center h-full">
                                <div className="w-16 h-16 bg-emerald-100 rounded-full flex items-center justify-center mb-6 shadow-inner">
                                    <svg className="w-8 h-8 text-emerald-600" fill="none" viewBox="0 0 24 24" stroke="currentColor"><path strokeLinecap="round" strokeLinejoin="round" strokeWidth="3" d="M5 13l4 4L19 7" /></svg>
                                </div>
                                <h3 className="text-2xl font-bold text-slate-800 tracking-tight mb-2">Protocol Secured</h3>
                                <p className="text-slate-500 font-medium text-sm">Intervention safely signed and registered to immutable log.</p>
                            </div>
                        ) : (
                            <div className="flex flex-col items-center justify-center border-2 border-dashed border-slate-200 rounded-3xl p-10 bg-slate-50/50 h-full">
                                <div className="w-10 h-10 border-4 border-slate-200 border-t-slate-400 rounded-full animate-spin mb-4"></div>
                                <h3 className="font-bold text-slate-400">Awaiting Clinical Hooks</h3>
                            </div>
                        )}
                    </div>
                </div>
            </div>
        </div>
    );
};
