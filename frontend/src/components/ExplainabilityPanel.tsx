import { AlertTriangle, CheckCircle, Info } from "lucide-react";
import { RiskScore } from "@/types";

export function ExplainabilityPanel({ data }: { data: RiskScore }) {
    if (!data.reasons || data.reasons.length === 0) return null;

    return (
        <div className="w-full glass p-6 rounded-2xl text-left space-y-4 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-100">
            <div className="flex items-center justify-between">
                <h3 className="text-xl font-semibold flex items-center gap-2">
                    <Info className="w-5 h-5 text-blue-400" />
                    Why this score?
                </h3>
                <div className="text-sm font-mono text-muted-foreground">
                    Confidence: {data.confidence_score}%
                </div>
            </div>

            <ul className="space-y-3">
                {data.reasons.map((reason, idx) => (
                    <li key={idx} className="flex items-start gap-3 bg-white/5 p-3 rounded-lg border border-white/5">
                        <AlertTriangle className="w-5 h-5 text-amber-500 shrink-0 mt-0.5" />
                        <span className="text-zinc-200">{reason}</span>
                    </li>
                ))}
            </ul>
        </div>
    );
}
