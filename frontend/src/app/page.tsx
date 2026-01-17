"use client";

import { useState } from "react";
import { RiskMeter } from "@/components/RiskMeter";
import { Search, ShieldAlert, TrendingUp } from "lucide-react";
import Link from "next/link";
import { LiveTicker } from "@/components/LiveTicker";
import { ReportList } from "@/components/ReportList";
import { ExplainabilityPanel } from "@/components/ExplainabilityPanel";
import { ActionCard } from "@/components/ActionCard";
import { RiskScore } from "@/types";

export default function Home() {
  const [query, setQuery] = useState("");
  const [result, setResult] = useState<RiskScore | null>(null);
  const [loading, setLoading] = useState(false);

  const handleScan = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!query) return;
    setLoading(true);

    try {
      const API_URL = process.env.NEXT_PUBLIC_API_URL || "http://127.0.0.1:8000";
      const res = await fetch(`${API_URL}/api/v1/scan?q=${encodeURIComponent(query)}`);
      if (!res.ok) throw new Error("Scan failed");
      const data = await res.json();

      setResult({
        value: query,
        risk_score: data.risk_score,
        level: data.level,
        report_count: data.report_count,
        reports: data.reports,
        confidence_score: data.confidence_score,
        reasons: data.reasons,
        action_advice: data.action_advice,
        scan_id: data.scan_id
      });
    } catch (err) {
      console.error(err);
      // Fallback for demo if API is down
      setResult({
        value: query,
        risk_score: 0,
        level: "Safe",
        report_count: 0,
        reports: [],
        confidence_score: 0,
        reasons: ["API Error - Could not scan"],
        action_advice: "System offline. Please try again."
      });
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen flex flex-col items-center justify-center p-4 bg-fixed bg-center">
      {/* Background Gradient Blob */}
      <div className="fixed inset-0 bg-gradient-to-tr from-violet-900/20 via-background to-background -z-10" />

      <div className="absolute top-6 right-6 flex items-center gap-3">
        <Link href="/trends" className="flex items-center gap-2 px-4 py-2 bg-zinc-800/50 hover:bg-zinc-800 border border-zinc-700 text-zinc-300 rounded-lg transition-colors text-sm font-medium backdrop-blur-sm">
          <TrendingUp className="w-4 h-4" />
          Trends
        </Link>
        <Link href="/report" className="flex items-center gap-2 px-4 py-2 bg-red-500/10 hover:bg-red-500/20 border border-red-500/20 text-red-500 rounded-lg transition-colors text-sm font-medium backdrop-blur-sm">
          <ShieldAlert className="w-4 h-4" />
          Report a Scam
        </Link>
      </div>

      <div className="w-full max-w-2xl space-y-8 text-center">
        <div className="space-y-4">
          <h1 className="text-5xl md:text-7xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-white to-white/50 tracking-tight">
            ScamShield
          </h1>
          <p className="text-muted-foreground text-lg md:text-xl max-w-lg mx-auto">
            Community-driven real-time scam detection.
            <br />
            Check UPI, Phone, URL, or Text instantly.
          </p>
        </div>

        <form onSubmit={handleScan} className="relative group">
          <div className="absolute -inset-0.5 bg-gradient-to-r from-violet-600 to-indigo-600 rounded-2xl blur opacity-30 group-hover:opacity-75 transition duration-500" />
          <div className="relative flex items-center bg-card rounded-xl border border-white/10 p-2 shadow-2xl">
            <Search className="w-6 h-6 ml-3 text-muted-foreground" />
            <input
              type="text"
              placeholder="Paste UPI, Phone Number, or URL..."
              className="flex-1 bg-transparent border-none outline-none px-4 py-3 text-lg placeholder:text-muted-foreground/50"
              value={query}
              onChange={(e) => setQuery(e.target.value)}
            />
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2.5 bg-white text-black font-semibold rounded-lg hover:bg-gray-200 transition disabled:opacity-50"
            >
              {loading ? "Scanning..." : "Scan Now"}
            </button>
          </div>
        </form>

        {result && (
          <div className="animate-in fade-in slide-in-from-bottom-8 duration-700 w-full max-w-2xl mx-auto space-y-6">
            <RiskMeter score={result.risk_score} level={result.level} />

            <ActionCard data={result} />
            <ExplainabilityPanel data={result} />

            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {/* Stats linked to API */}
              <div className="glass p-4 rounded-xl">
                <div className="text-2xl font-bold">{result.report_count}</div>
                <div className="text-xs text-muted-foreground uppercase">Reports Found</div>
              </div>
              <div className="glass p-4 rounded-xl">
                <div className="text-2xl font-bold">
                  {result.level === "Safe" ? "Verified" : "Flagged"}
                </div>
                <div className="text-xs text-muted-foreground uppercase">Status</div>
              </div>
              <div className="glass p-4 rounded-xl">
                <div className="text-2xl font-bold">
                  {result.risk_score > 50 ? "High" : "Low"}
                </div>
                <div className="text-xs text-muted-foreground uppercase">Confidence</div>
              </div>
            </div>

            <ReportList reports={result.reports} />
          </div>
        )}

        {!result && (
          <LiveTicker />
        )}
      </div>
    </main>
  );
}
