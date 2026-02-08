import { useState, useEffect } from 'react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { Globe, Clock } from 'lucide-react'
import { apiClient } from '../lib/api'

interface Bounty {
  bounty_id: string
  title: string
  reward: string
  severity: string
  status: string
  protocol: string
  expires_at: string
}

export default function Bounties() {
  const [bounties, setBounties] = useState<Bounty[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadBounties() {
      try {
        const data = await apiClient.getBounties()
        setBounties(data)
      } catch (err) {
        console.error('Failed to load bounties:', err)
      } finally {
        setLoading(false)
      }
    }
    loadBounties()
  }, [])

  const severityVariant = (severity: string) => {
    switch (severity.toLowerCase()) {
      case 'critical': return 'danger'
      case 'high': return 'warning'
      case 'medium': return 'default'
      default: return 'default'
    }
  }

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white tracking-wider">
          ACTIVE <span className="text-primary">BOUNTIES</span>
        </h1>
        <Button variant="outline">Post Bounty</Button>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {loading ? (
          <p className="text-text-muted col-span-full">Loading...</p>
        ) : bounties.length > 0 ? (
          bounties.map((bounty) => (
            <Card key={bounty.bounty_id} className="relative overflow-hidden group hover:border-primary/50 transition-all cursor-pointer">
              <div className="absolute top-0 right-0 p-4">
                <Badge variant={severityVariant(bounty.severity)}>
                  {bounty.severity}
                </Badge>
              </div>

              <div className="mb-4">
                <h3 className="text-lg font-bold text-white group-hover:text-primary transition-colors">
                  {bounty.title}
                </h3>
                <p className="text-sm text-text-secondary mt-1">{bounty.protocol}</p>
              </div>

              <div className="space-y-2 mb-6">
                <div className="flex items-center text-sm text-text-muted">
                  <Globe className="w-4 h-4 mr-2" />
                  <span>Monad Testnet</span>
                </div>
                <div className="flex items-center text-sm text-text-muted">
                  <Clock className="w-4 h-4 mr-2" />
                  <span>Expires in 2 days</span>
                </div>
              </div>

              <div className="flex items-center justify-between mt-auto pt-4 border-t border-white/5">
                <span className="text-xl font-bold text-success text-shadow-neon">
                  {bounty.reward} ETH
                </span>
                <Button size="sm" variant="secondary">View Details</Button>
              </div>
            </Card>
          ))
        ) : (
          <p className="text-text-muted col-span-full">No bounties available</p>
        )}
      </div>
    </div>
  )
}
