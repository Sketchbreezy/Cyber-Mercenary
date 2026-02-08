import { useEffect, useState } from 'react'
import { Card } from '../components/ui/Card'
import { ShieldCheck, Bug, DollarSign, Target } from 'lucide-react'
import { apiClient } from '../lib/api'

interface Stats {
  total_scans: number
  vulnerabilities_found: number
  bounties_claimed: number
  total_earnings: string
}

interface Activity {
  id: string
  type: string
  message: string
  timestamp: string
}

export default function Dashboard() {
  const [stats, setStats] = useState<Stats>({
    total_scans: 0,
    vulnerabilities_found: 0,
    bounties_claimed: 0,
    total_earnings: '0',
  })
  const [activities, setActivities] = useState<Activity[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    async function fetchData() {
      try {
        const [statsData, recentScans] = await Promise.all([
          apiClient.getStats().catch(() => stats),
          apiClient.getRecentScans().catch(() => []),
        ])
        setStats(statsData)

        // Transform recent scans to activities
        const newActivities: Activity[] = recentScans.map((scan: any) => ({
          id: scan.scan_id,
          type: 'scan',
          message: `Scan completed for ${scan.contract_address?.slice(0, 8)}...${scan.contract_address?.slice(-4)}`,
          timestamp: scan.timestamp,
        }))
        setActivities(newActivities)
      } catch (err) {
        setError('Failed to load dashboard data')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [])

  const statCards = [
    { name: 'Contracts Scanned', value: stats.total_scans.toLocaleString(), icon: ShieldCheck, color: 'text-primary' },
    { name: 'Vulnerabilities Found', value: stats.vulnerabilities_found.toLocaleString(), icon: Bug, color: 'text-accent' },
    { name: 'Active Bounties', value: '0', icon: Target, color: 'text-warning' },
    { name: 'Total Earned', value: `${stats.total_earnings} ETH`, icon: DollarSign, color: 'text-success' },
  ]

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold text-white tracking-wider">
        OPERATIONAL <span className="text-primary">OVERVIEW</span>
      </h1>

      {error && (
        <div className="p-4 bg-red-500/10 border border-red-500 rounded text-red-500">
          {error}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => (
          <Card key={stat.name} className="flex items-center space-x-4">
            <div className={`p-3 rounded-full bg-surface ${stat.color} bg-opacity-10`}>
              <stat.icon className={`w-6 h-6 ${stat.color}`} />
            </div>
            <div>
              <p className="text-sm font-medium text-text-muted">{stat.name}</p>
              <p className="text-2xl font-bold text-white">{loading ? '...' : stat.value}</p>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card className="h-96">
          <h3 className="text-xl font-bold mb-4">Recent Activity</h3>
          <div className="space-y-4">
            {loading ? (
              <p className="text-text-muted">Loading...</p>
            ) : activities.length > 0 ? (
              activities.map((activity) => (
                <div key={activity.id} className="flex items-center text-sm text-text-secondary">
                  <span className="w-2 h-2 rounded-full bg-success mr-2" />
                  {activity.message}
                </div>
              ))
            ) : (
              <div className="flex items-center text-sm text-text-secondary">
                <span className="w-2 h-2 rounded-full bg-success mr-2" />
                No recent activity
              </div>
            )}
          </div>
        </Card>

        <Card className="h-96">
          <h3 className="text-xl font-bold mb-4">System Status</h3>
          <div className="space-y-4">
            <div className="flex justify-between items-center">
              <span>Agent Core</span>
              <span className="text-success">ONLINE</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Database</span>
              <span className="text-success">CONNECTED</span>
            </div>
            <div className="flex justify-between items-center">
              <span>Blockchain Node</span>
              <span className="text-success">SYNCED</span>
            </div>
          </div>
        </Card>
      </div>
    </div>
  )
}
