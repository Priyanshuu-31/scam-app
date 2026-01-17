"use client";

import { motion } from "framer-motion";
import { MessageSquare, Calendar, Globe, Smartphone, AlertTriangle } from "lucide-react";

interface Report {
    scammer_identifier: string;
    category: string;
    description: string;
    created_at: string;
    evidence_urls?: string[];
}

interface ReportListProps {
    reports: Report[];
}

export function ReportList({ reports }: ReportListProps) {
    if (!reports || reports.length === 0) return null;

    return (
        <div className="w-full max-w-2xl mt-8">
            <div className="flex items-center gap-2 mb-4 text-zinc-400 text-sm uppercase tracking-wider font-semibold">
                <MessageSquare className="w-4 h-4" />
                Recent Reports ({reports.length})
            </div>

            <div className="space-y-4">
                {reports.map((report, i) => (
                    <motion.div
                        key={i}
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        transition={{ delay: i * 0.1 }}
                        className="group bg-zinc-900/50 border border-white/5 rounded-xl p-4 backdrop-blur-sm hover:border-red-500/20 transition-all"
                    >
                        <div className="flex justify-between items-start mb-2">
                            <div className="flex items-center gap-2">
                                <span className={`text-xs px-2 py-1 rounded bg-zinc-800 text-zinc-300 capitalize border border-white/5 group-hover:bg-red-500/10 group-hover:text-red-400 group-hover:border-red-500/20 transition-colors`}>
                                    {report.category}
                                </span>
                                <span className="text-zinc-600 text-xs flex items-center gap-1">
                                    <Calendar className="w-3 h-3" />
                                    {new Date(report.created_at).toLocaleDateString()}
                                </span>
                            </div>
                        </div>

                        <p className="text-zinc-300 text-sm leading-relaxed">
                            "{report.description || "No description provided."}"
                        </p>

                    </motion.div>
                ))}
            </div>
        </div>
    );
}
