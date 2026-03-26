import React from 'react';
import type { CaseState } from '../types';

interface Props {
    cases: CaseState[];
    onSelectCase: (id: string) => void;
}

export const Dashboard: React.FC<Props> = ({ cases, onSelectCase }) => {
    const getTofStyle = (tof: number) => {
        if (tof >= 0.9) return "from-emerald-400 to-green-500 shadow-[0_0_10px_rgba(16,185,129,0.3)]";
        if (tof >= 0.7) return "from-amber-300 to-orange-400 shadow-[0_0_10px_rgba(245,158,11,0.3)]";
        return "from-rose-400 to-red-500 shadow-[0_0_10px_rgba(225,29,72,0.3)]";
    };

    const getStatus = (c: CaseState) => {
        if (c.acknowledged) return { text: "Acknowledged", border: "bg-blue-400", dot: "bg-blue-500", ping: false };
        if (c.recommendation) return { text: "Rec Pending", border: "bg-rose-400", dot: "bg-rose-500", ping: true };
        if (c.phase === "CLOSING" || (c.pk_state && c.pk_state.tof_ratio < 0.9)) return { text: "Monitor", border: "bg-amber-400", dot: "bg-amber-500", ping: false };
        return { text: "Safe", border: "bg-emerald-400", dot: "bg-emerald-500", ping: false };
    };

    return (
        <div className="p-8 h-full w-full min-h-screen bg-gradient-to-br from-slate-50 relative overflow-hidden to-blue-50/50">
            {/* Decorative background blobs for depth */}
            <div className="absolute top-0 left-0 w-96 h-96 bg-blue-400/10 rounded-full mix-blend-multiply filter blur-3xl opacity-70 animate-pulse"></div>

            <div className="relative z-10 max-w-7xl mx-auto">
                <div className="flex items-center justify-between mb-10">
                    <h1 className="text-4xl font-extrabold tracking-tight text-slate-800 bg-clip-text text-transparent bg-gradient-to-r from-slate-800 to-slate-500">
                        Clinical Overview
                    </h1>
                    <div className="text-sm font-medium text-slate-500 bg-white/60 px-5 py-2.5 rounded-full shadow-sm backdrop-blur-md border border-white/50">
                        {cases.length} Active Streams
                    </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
                    {cases.map(c => {
                        const status = getStatus(c);
                        const tof = c.pk_state ? c.pk_state.tof_ratio : 1.0;

                        return (
                            <div key={c.patient.id}
                                className={`group relative bg-white/80 backdrop-blur-xl rounded-3xl shadow-[0_8px_30px_rgb(0,0,0,0.04)] border border-white p-7 hover:shadow-[0_20px_40px_rgb(0,0,0,0.08)] hover:-translate-y-1 transition-all duration-300 overflow-hidden`}
                            >
                                {/* Left accent indicator strip */}
                                <div className={`absolute top-0 left-0 w-1.5 h-full ${status.border}`}></div>

                                <div className="flex justify-between items-start mb-6 pl-2">
                                    <div>
                                        <h2 className="text-xl font-bold text-slate-800 tracking-tight">{c.patient.name}</h2>
                                        <p className="text-sm font-medium text-slate-500 mt-1">{c.patient.case_type}</p>
                                    </div>
                                    <div className="flex items-center space-x-2">
                                        <div className="relative flex h-3 w-3 items-center justify-center">
                                            {status.ping && <span className={`absolute inline-flex h-full w-full rounded-full ${status.dot} opacity-75 animate-ping`}></span>}
                                            <span className={`relative inline-flex rounded-full h-2 w-2 ${status.dot}`}></span>
                                        </div>
                                        <span className={`px-2.5 py-0.5 rounded-md text-[10px] uppercase tracking-wider font-extrabold text-slate-600 bg-slate-100`}>
                                            {status.text}
                                        </span>
                                    </div>
                                </div>

                                <div className="mb-8 pl-2">
                                    <div className="flex justify-between text-sm mb-2">
                                        <span className="font-semibold text-slate-400 uppercase tracking-widest text-[10px]">TCI Dynamics</span>
                                        <span className="font-mono font-bold text-slate-800">{tof.toFixed(2)}</span>
                                    </div>
                                    <div className="w-full bg-slate-100 rounded-full h-2.5 shadow-inner overflow-hidden">
                                        <div
                                            className={`h-full bg-gradient-to-r ${getTofStyle(tof)} transition-all duration-[800ms] ease-out`}
                                            style={{ width: `${Math.min(100, Math.max(0, tof * 100))}%` }}
                                        ></div>
                                    </div>
                                </div>

                                <button
                                    onClick={() => onSelectCase(c.patient.id)}
                                    className="w-full relative bg-slate-50 hover:bg-slate-900 text-slate-600 hover:text-white font-bold py-3.5 px-4 rounded-2xl shadow-sm hover:shadow-md transition-all active:scale-[0.98] duration-300 outline-none"
                                >
                                    Review Target Chart
                                </button>
                            </div>
                        );
                    })}
                </div>
            </div>
        </div>
    );
};
