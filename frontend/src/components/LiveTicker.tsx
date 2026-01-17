"use client";

import { useEffect, useState } from "react";
import { motion } from "framer-motion";
import { ShieldAlert, AlertTriangle, Smartphone, Globe, MessageSquare } from "lucide-react";

interface Report {
    scammer_identifier: string;
    category: string;
    description: string;
    created_at: string;
}

export function LiveTicker() {
    const [reports, setReports] = useState<Report[]>([]);

    useEffect(() => {
        // Poll for new reports every 10 seconds
        const fetchReports = async () => {
            try {
                const res = await fetch("http://127.0.0.1:8000/api/v1/reports/recent?limit=10");
                if (res.ok) {
                    const data = await res.json();
                    setReports(data);
                }
            } catch (err) {
                console.error("Failed to fetch live feed", err);
            }
        };

        fetchReports();
        const interval = setInterval(fetchReports, 10000);
        return () => clearInterval(interval);
    }, []);

    if (reports.length === 0) return null;

    return (
        <div className="w-full max-w-4xl pt-8 pb-4">
            <div className="flex items-center gap-2 mb-4 text-zinc-400 text-sm uppercase tracking-wider font-semibold">
                <div className="w-2 h-2 rounded-full bg-red-500 animate-pulse" />
                Live Community Alerts
            </div>

            <div className="relative flex overflow-x-hidden mask-linear-fade">
                {/* Simple horizontal list for now, or marquee */}
                <div className="flex gap-4 animate-scroll-left hover:pause">
                    {[...reports, ...reports].map((report, i) => ( // Duplicate for seamless scroll
                        <div
                            key={i}
                            className="flex-shrink-0 w-80 bg-zinc-900/50 border border-white/5 rounded-xl p-4 backdrop-blur-sm hover:border-red-500/20 transition-colors"
                        >
                            <div className="flex items-start gap-3">
                                <div className="p-2 bg-red-500/10 rounded-lg text-red-400">
                                    {getIcon(report.category)}
                                </div>
                                <div>
                                    <h4 className="font-mono text-white text-sm font-semibold truncate w-48">
                                        {report.scammer_identifier}
                                    </h4>
                                    <span className="text-xs text-zinc-500 uppercase font-bold tracking-wider">
                                        {report.category} Scam
                                    </span>
                                    <p className="text-zinc-400 text-xs mt-1 line-clamp-2">
                                        "{report.description || "Suspicious activity reported."}"
                                    </p>
                                    <span className="text-[10px] text-zinc-600 mt-2 block">
                                        {new Date(report.created_at).toLocaleTimeString()}
                                    </span>
                                </div>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
}

function getIcon(type: string) {
    switch (type) {
        case "phone": return <Smartphone className="w-4 h-4" />;
        case "url": return <Globe className="w-4 h-4" />;
        case "message_text": return <MessageSquare className="w-4 h-4" />;
        default: return <AlertTriangle className="w-4 h-4" />;
    }
}
