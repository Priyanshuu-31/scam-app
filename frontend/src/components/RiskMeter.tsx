"use client";

import { motion } from "framer-motion";
import { cn } from "@/lib/utils";

interface RiskMeterProps {
    score: number; // 0 to 100
    level: "Safe" | "Caution" | "Critical";
}

export function RiskMeter({ score, level }: RiskMeterProps) {
    const getColor = () => {
        if (score < 30) return "text-emerald-500 from-emerald-500 to-emerald-700";
        if (score < 70) return "text-amber-500 from-amber-500 to-amber-700";
        return "text-red-500 from-red-500 to-red-700";
    };

    return (
        <div className="flex flex-col items-center justify-center p-8 rounded-3xl glass w-full max-w-sm mx-auto transition-all duration-500">
            <div className="relative w-48 h-48 flex items-center justify-center">
                {/* Background Circle */}
                <svg className="w-full h-full transform -rotate-90">
                    <circle
                        cx="96"
                        cy="96"
                        r="88"
                        stroke="currentColor"
                        strokeWidth="12"
                        fill="transparent"
                        className="text-muted/30"
                    />
                    {/* Progress Circle */}
                    <motion.circle
                        initial={{ strokeDasharray: 565, strokeDashoffset: 565 }}
                        animate={{ strokeDashoffset: 565 - (565 * score) / 100 }}
                        transition={{ duration: 1.5, ease: "easeOut" }}
                        cx="96"
                        cy="96"
                        r="88"
                        stroke="currentColor"
                        strokeWidth="12"
                        fill="transparent"
                        strokeLinecap="round"
                        className={cn(getColor().split(" ")[0])} // Use just text color for stroke
                    />
                </svg>

                {/* Inner Score Text */}
                <div className="absolute flex flex-col items-center">
                    <motion.span
                        initial={{ opacity: 0, y: 10 }}
                        animate={{ opacity: 1, y: 0 }}
                        className="text-5xl font-bold tracking-tighter"
                    >
                        {score}
                    </motion.span>
                    <span className="text-sm text-muted-foreground uppercase tracking-widest mt-1">Risk Score</span>
                </div>
            </div>

            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                transition={{ delay: 0.5 }}
                className={cn(
                    "mt-6 px-6 py-2 rounded-full font-semibold border bg-background/50 backdrop-blur-md",
                    score < 30 ? "border-emerald-500/50 text-emerald-400" :
                        score < 70 ? "border-amber-500/50 text-amber-400" : "border-red-500/50 text-red-400"
                )}
            >
                {level.toUpperCase()}
            </motion.div>
        </div>
    );
}
