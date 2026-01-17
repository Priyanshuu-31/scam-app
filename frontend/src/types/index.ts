export type RiskLevel = "Safe" | "Caution" | "Critical";

export interface RiskScore {
    value: string;
    risk_score: number;
    level: RiskLevel;
    report_count: number;
    reports: any[];
    // New V2 fields
    confidence_score: number;
    reasons: string[];
    action_advice: string;
    scan_id?: string;
}
