"use client";

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowLeft, TrendingUp, PieChart as PieChartIcon, Activity, AlertTriangle } from 'lucide-react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    PieChart, Pie, Cell, Legend
} from 'recharts';

interface StatsData {
    total_reports: number;
    categories: { name: string; value: number }[];
    trend: { date: string; count: number }[];
}

const COLORS = ['#ef4444', '#f97316', '#eab308', '#3b82f6', '#8b5cf6'];

import { ReportsModal } from '@/components/ReportsModal';

export default function TrendsPage() {
    const [data, setData] = useState<StatsData | null>(null);
    const [loading, setLoading] = useState(true);

    // Modal State
    const [modalOpen, setModalOpen] = useState(false);
    const [modalTitle, setModalTitle] = useState("");
    const [modalReports, setModalReports] = useState([]);
    const [modalLoading, setModalLoading] = useState(false);

    useEffect(() => {
        const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
        fetch(`${API_URL}/api/v1/stats`)
            .then(res => res.json())
            .then(setData)
            .catch(console.error)
            .finally(() => setLoading(false));
    }, []);

    const fetchFilteredReports = async (category?: string, date?: string) => {
        setModalLoading(true);
        setModalOpen(true);
        try {
            const params = new URLSearchParams();
            if (category) params.append("category", category);
            if (date) params.append("date", date);

            const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
            const res = await fetch(`${API_URL}/api/v1/reports/recent?limit=20&${params.toString()}`);
            const data = await res.json();
            setModalReports(data);
        } catch (e) {
            console.error(e);
        } finally {
            setModalLoading(false);
        }
    };

    if (loading) return (
        <div className="min-h-screen bg-[#050510] flex items-center justify-center text-cyan-400">
            <Activity className="animate-spin w-8 h-8" />
        </div>
    );

    return (
        <main className="min-h-screen bg-[#050510] text-gray-200 p-4 md:p-8 bg-grid-pattern relative overflow-hidden">
            <ReportsModal
                isOpen={modalOpen}
                onClose={() => setModalOpen(false)}
                title={modalTitle}
                reports={modalReports}
                loading={modalLoading}
            />

            <div className="max-w-6xl mx-auto relative z-10">

                {/* Header */}
                <header className="flex justify-between items-center mb-12">
                    <div className="flex items-center gap-3">
                        <Link href="/" className="p-2 rounded-full glass hover:bg-white/10 transition-colors">
                            <ArrowLeft className="w-5 h-5" />
                        </Link>
                        <h1 className="text-3xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-red-400 to-purple-600">
                            Threat Intelligence
                        </h1>
                    </div>
                </header>

                {/* KPI Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
                    <motion.div
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
                        className="glass p-6 rounded-2xl border-l-4 border-red-500"
                    >
                        <div className="text-zinc-400 text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                            <AlertTriangle className="w-4 h-4 text-red-500" /> Total Reports
                        </div>
                        <div className="text-4xl font-bold text-white mt-2">{data?.total_reports || 0}</div>
                        <div className="text-xs text-zinc-500 mt-1">All time community submissions</div>
                    </motion.div>

                    <motion.div
                        initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 }}
                        className="glass p-6 rounded-2xl border-l-4 border-blue-500"
                    >
                        <div className="text-zinc-400 text-sm font-semibold uppercase tracking-wider flex items-center gap-2">
                            <TrendingUp className="w-4 h-4 text-blue-500" /> Avg Daily (7d)
                        </div>
                        <div className="text-4xl font-bold text-white mt-2">
                            {data?.trend ? (data.trend.reduce((a, b) => a + b.count, 0) / 7).toFixed(1) : 0}
                        </div>
                        <div className="text-xs text-zinc-500 mt-1">Reports per day</div>
                    </motion.div>
                </div>

                {/* Charts Grid */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">

                    {/* Activity Chart */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.2 }}
                        className="glass p-6 rounded-2xl"
                    >
                        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                            <TrendingUp className="w-5 h-5 text-cyan-400" /> Scam Activity (Last 7 Days)
                        </h3>
                        <div className="h-64 cursor-pointer">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={data?.trend || []}
                                    onClick={(e: any) => {
                                        if (e && e.activePayload && e.activePayload[0]) {
                                            const date = e.activePayload[0].payload.date;
                                            setModalTitle(`Reports on ${date}`);
                                            fetchFilteredReports(undefined, date);
                                        }
                                    }}
                                >
                                    <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                                    <XAxis dataKey="date" stroke="#71717a" fontSize={12} tickFormatter={(val) => val.slice(5)} />
                                    <YAxis stroke="#71717a" fontSize={12} />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#18181b', borderColor: '#3f3f46', borderRadius: '8px' }}
                                        itemStyle={{ color: '#fff' }}
                                        cursor={{ stroke: '#ffffff20', strokeWidth: 1 }}
                                    />
                                    <Line
                                        type="monotone"
                                        dataKey="count"
                                        stroke="#22d3ee"
                                        strokeWidth={3}
                                        dot={{ fill: '#22d3ee', r: 4, strokeWidth: 0 }}
                                        activeDot={{ r: 6, fill: '#fff' }}
                                    />
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                        <p className="text-xs text-zinc-500 mt-2 text-center">Click on a data point to view reports</p>
                    </motion.div>

                    {/* Category Chart */}
                    <motion.div
                        initial={{ opacity: 0, scale: 0.95 }} animate={{ opacity: 1, scale: 1 }} transition={{ delay: 0.3 }}
                        className="glass p-6 rounded-2xl"
                    >
                        <h3 className="text-lg font-semibold mb-6 flex items-center gap-2">
                            <PieChartIcon className="w-5 h-5 text-purple-400" /> Scam Types Distribution
                        </h3>
                        <div className="h-64 cursor-pointer">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={data?.categories || []}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={80}
                                        paddingAngle={5}
                                        dataKey="value"
                                        onClick={(entry) => {
                                            setModalTitle(`Category: ${entry.name}`);
                                            fetchFilteredReports(entry.name.toLowerCase());
                                        }}
                                    >
                                        {(data?.categories || []).map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} className="hover:opacity-80 transition-opacity outline-none" />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#18181b', borderColor: '#3f3f46', borderRadius: '8px' }}
                                        itemStyle={{ color: '#fff' }}
                                    />
                                    <Legend />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                        <p className="text-xs text-zinc-500 mt-2 text-center">Click on a slice to view reports</p>
                    </motion.div>

                </div>
            </div>
        </main>
    );
}
