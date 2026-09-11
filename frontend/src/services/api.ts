import { AuditResponse } from '../types/audit';

export async function analyserUrl(urlToAudit: string): Promise<AuditResponse> {
  const response = await fetch('/api/audit/analyser', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ url: urlToAudit }), // Ou en query params selon votre route
  });

  if (!response.ok) {
    const errorData = await response.json();
    throw new Error(errorData.detail || 'Erreur lors de l\'audit');
  }

  return response.json();
}