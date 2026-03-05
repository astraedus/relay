import type { BriefingRow, GenerateRequest, GenerateResponse } from './types';

const API_BASE = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function getBriefings(limit = 20): Promise<BriefingRow[]> {
  const res = await fetch(`${API_BASE}/api/briefings?limit=${limit}`);
  if (!res.ok) throw new Error('Failed to fetch briefings');
  return res.json();
}

export async function getBriefing(id: number): Promise<BriefingRow> {
  const res = await fetch(`${API_BASE}/api/briefings/${id}`);
  if (!res.ok) throw new Error('Failed to fetch briefing');
  return res.json();
}

export async function generateBriefing(req: GenerateRequest): Promise<GenerateResponse> {
  const res = await fetch(`${API_BASE}/api/generate`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(req),
  });
  if (!res.ok) {
    const text = await res.text();
    throw new Error(`Generate failed: ${text}`);
  }
  return res.json();
}
