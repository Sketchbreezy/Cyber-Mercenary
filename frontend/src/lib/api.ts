const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export async function api<T>(endpoint: string, options?: RequestInit): Promise<T> {
  const response = await fetch(`${API_URL}${endpoint}`, {
    headers: {
      'Content-Type': 'application/json',
      ...options?.headers,
    },
    ...options,
  })

  if (!response.ok) {
    const error = await response.json().catch(() => ({ message: response.statusText }))
    throw new Error(error.message || `API Error: ${response.statusText}`)
  }

  // Handle empty responses
  const text = await response.text()
  return text ? JSON.parse(text) : null
}

export const apiClient = {
  // Health check
  health: () => api<{ status: string; agent: string; phase: string; services: string }>('/health'),

  // Scanner - using correct /api/v1/ prefix
  scan: (address: string) => api<{ scan_id: string; status: string }>('/api/v1/scan', {
    method: 'POST',
    body: JSON.stringify({ contract_address: address }),
  }),
  getScanStatus: (scanId: string) => api<{ scan_id: string; status: string; results?: any }>(`/api/v1/scan/${scanId}`),
  getRecentScans: () => api<any[]>('/api/v1/scans'),

  // Stats
  getStats: () => api<{
    total_scans: number
    vulnerabilities_found: number
    bounties_claimed: number
    total_earnings: string
  }>('/api/v1/stats'),

  // Agent
  getAgentAddress: () => api<{ address: string }>('/api/v1/agent/address'),
}
