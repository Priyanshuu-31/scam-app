import { Shield, ShieldAlert, ShieldCheck } from "lucide-react";
import { RiskScore } from "@/types";
import { cn } from "@/lib/utils";

export function ActionCard({ data }: { data: RiskScore }) {
    const issafe = data.level === "Safe";
    const iscritical = data.level === "Critical";

    return (
        <div className={cn(
            "w-full p-6 rounded-2xl text-left space-y-2 animate-in fade-in slide-in-from-bottom-4 duration-700 delay-200 border",
            issafe ? "bg-emerald-500/10 border-emerald-500/20" :
                iscritical ? "bg-red-500/10 border-red-500/20" : "bg-amber-500/10 border-amber-500/20"
        )}>
            <div className="flex items-start gap-4">
                <div className={cn("p-3 rounded-full shrink-0",
                    issafe ? "bg-emerald-500/20 text-emerald-400" :
                        iscritical ? "bg-red-500/20 text-red-400" : "bg-amber-500/20 text-amber-400"
                )}>
                    {issafe ? <ShieldCheck className="w-6 h-6" /> :
                        iscritical ? <ShieldAlert className="w-6 h-6" /> : <Shield className="w-6 h-6" />}
                </div>
                <div>
                    <h4 className={cn("font-bold text-lg mb-1",
                        issafe ? "text-emerald-400" :
                            iscritical ? "text-red-400" : "text-amber-400"
                    )}>
                        Recommendation
                    </h4>
                    <p className="text-zinc-300 leading-relaxed font-medium">
                        {data.action_advice}
                    </p>
                </div>
            </div>
        </div>
    );
}
