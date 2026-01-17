"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { ArrowLeft, Send, AlertTriangle, ShieldAlert } from "lucide-react";
import Link from "next/link";
import { cn } from "@/lib/utils";

export default function ReportPage() {
    const [formData, setFormData] = useState({
        value: "",
        type: "phone",
        description: "",
    });
    const [status, setStatus] = useState<"idle" | "loading" | "success" | "error">("idle");

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setStatus("loading");

        try {
            const res = await fetch("http://127.0.0.1:8000/api/v1/reports", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(formData),
            });

            if (!res.ok) {
                throw new Error("Failed to submit report");
            }

            setStatus("success");
            setFormData({ value: "", type: "phone", description: "" });
        } catch (err) {
            console.error(err);
            setStatus("error");
        }
    };

    return (
        <main className="min-h-screen bg-black text-white p-4 font-sans selection:bg-purple-500/30">
            <div className="max-w-2xl mx-auto pt-10">
                <Link
                    href="/"
                    className="inline-flex items-center text-zinc-400 hover:text-white mb-8 transition-colors"
                >
                    <ArrowLeft className="w-4 h-4 mr-2" />
                    Back to Scanner
                </Link>

                <motion.div
                    initial={{ opacity: 0, y: 20 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="bg-zinc-900/50 border border-white/5 rounded-2xl p-8 backdrop-blur-xl"
                >
                    <div className="flex items-center gap-4 mb-8">
                        <div className="p-3 bg-red-500/10 rounded-xl text-red-500 border border-red-500/20">
                            <ShieldAlert className="w-6 h-6" />
                        </div>
                        <div>
                            <h1 className="text-2xl font-bold bg-gradient-to-r from-white to-zinc-400 bg-clip-text text-transparent">
                                Report a Scam
                            </h1>
                            <p className="text-zinc-400 text-sm">
                                Help the community by reporting suspicious entities.
                            </p>
                        </div>
                    </div>

                    {status === "success" ? (
                        <motion.div
                            initial={{ scale: 0.9, opacity: 0 }}
                            animate={{ scale: 1, opacity: 1 }}
                            className="bg-green-500/10 border border-green-500/20 rounded-xl p-6 text-center"
                        >
                            <h3 className="text-green-400 font-semibold text-lg mb-2">Report Submitted!</h3>
                            <p className="text-zinc-400 mb-4">
                                Thank you for contributing to ScamShield. Your report has been logged.
                            </p>
                            <button
                                onClick={() => setStatus("idle")}
                                className="text-white bg-green-600/20 hover:bg-green-600/30 px-4 py-2 rounded-lg transition-colors border border-green-500/30"
                            >
                                Submit Another
                            </button>
                        </motion.div>
                    ) : (
                        <form onSubmit={handleSubmit} className="space-y-6">
                            <div className="space-y-2">
                                <label className="text-sm font-medium text-zinc-300">Scammer Details</label>
                                <div className="grid grid-cols-4 gap-4">
                                    <select
                                        value={formData.type}
                                        onChange={(e) => setFormData({ ...formData, type: e.target.value })}
                                        className="col-span-1 bg-black/50 border border-white/10 rounded-xl px-3 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50"
                                    >
                                        <option value="phone">Phone</option>
                                        <option value="upi">UPI ID</option>
                                        <option value="url">Website URL</option>
                                        <option value="message_text">Message</option>
                                    </select>
                                    <input
                                        required
                                        type="text"
                                        placeholder="e.g. +91 9876543210 or admin@scam.com"
                                        value={formData.value}
                                        onChange={(e) => setFormData({ ...formData, value: e.target.value })}
                                        className="col-span-3 bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 placeholder:text-white/20"
                                    />
                                </div>
                            </div>

                            <div className="space-y-2">
                                <label className="text-sm font-medium text-zinc-300">Description</label>
                                <textarea
                                    required
                                    rows={4}
                                    placeholder="Describe what happened..."
                                    value={formData.description}
                                    onChange={(e) => setFormData({ ...formData, description: e.target.value })}
                                    className="w-full bg-black/50 border border-white/10 rounded-xl px-4 py-3 text-sm focus:outline-none focus:ring-2 focus:ring-purple-500/50 placeholder:text-white/20 resize-none"
                                />
                            </div>

                            {status === "error" && (
                                <div className="flex items-center gap-2 text-red-400 text-sm bg-red-500/10 p-3 rounded-lg border border-red-500/20">
                                    <AlertTriangle className="w-4 h-4" />
                                    Failed to submit. Please try again.
                                </div>
                            )}

                            <button
                                type="submit"
                                disabled={status === "loading"}
                                className={cn(
                                    "w-full flex items-center justify-center gap-2 bg-white text-black font-semibold py-3 rounded-xl transition-all",
                                    "hover:bg-zinc-200 focus:ring-2 focus:ring-white/20",
                                    status === "loading" && "opacity-50 cursor-not-allowed"
                                )}
                            >
                                {status === "loading" ? "Submitting..." : (
                                    <>
                                        Submit Report <Send className="w-4 h-4" />
                                    </>
                                )}
                            </button>
                        </form>
                    )}
                </motion.div>
            </div>
        </main>
    );
}
