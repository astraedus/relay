export interface BriefingReport {
  summary: string;
  key_decisions: string[];
  blockers: string[];
  momentum: string;
  action_items: string[];
}

export interface BriefingRow {
  id: number;
  workspace_id: number | null;
  team_name: string;
  content: BriefingReport;
  created_at: string;
}

export interface GenerateRequest {
  team_name?: string;
  github_repos?: string[];
  slack_channel_id?: string;
  hours?: number;
  workspace_id?: number | null;
}

export interface GenerateResponse {
  briefing_id: number;
  status: string;
  report: BriefingReport | null;
}
