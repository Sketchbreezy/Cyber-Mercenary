import { useState, useEffect } from 'react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { Globe, Clock } from 'lucide-react'
import { apiClient } from '../lib/api'

interface Gig {
  gig_id: string
  title: string
  reward: string
  status: string
  client: string
  expires_at: string
}

export default function Gigs() {
  const [gigs, setGigs] = useState<Gig[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    async function loadGigs() {
      try {
        const data = await apiClient.getGigs()
        setGigs(data)
      } catch (err) {
        console.error('Failed to load gigs:', err)
      } finally {
        setLoading(false)
      }
    }
    loadGigs()
  }, [])

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold text-white tracking-wider">
          AGENT <span className="text-primary">MARKETPLACE</span>
        </h1>
        <Button variant="outline">Create Gig</Button>
      </div>

      {loading ? (
        <p className="text-text-muted">Loading...</p>
      ) : gigs.length > 0 ? (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {gigs.map((gig) => (
            <Card key={gig.gig_id} className="relative overflow-hidden group hover:border-primary/50 transition-all cursor-pointer">
              <div className="absolute top-0 right-0 p-4">
                <Badge variant={gig.status === 'open' ? 'success' : 'default'}>
                  {gig.status}
                </Badge>
              </div>

              <div className="mb-4">
                <h3 className="text-lg font-bold text-white group-hover:text-primary transition-colors">
                  {gig.title}
                </h3>
                <p className="text-sm text-text-secondary mt-1">Client: {gig.client}</p>
              </div>

              <div className="space-y-2 mb-6">
                <div className="flex items-center text-sm text-text-muted">
                  <Globe className="w-4 h-4 mr-2" />
                  <span>Monad Testnet</span>
                </div>
                <div className="flex items-center text-sm text-text-muted">
                  <Clock className="w-4 h-4 mr-2" />
                  <span>{new Date(gig.expires_at).toLocaleDateString()}</span>
                </div>
              </div>

              <div className="flex items-center justify-between mt-auto pt-4 border-t border-white/5">
                <span className="text-xl font-bold text-success text-shadow-neon">
                  {gig.reward} ETH
                </span>
                <Button size="sm" variant="secondary">View Details</Button>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <div className="flex items-center justify-center h-[50vh]">
          <div className="text-center">
            <h1 className="text-2xl font-bold text-text-muted mb-2">Agent-to-Agent Marketplace</h1>
            <p className="text-text-secondary">Coming Soon...</p>
          </div>
        </div>
      )}
    </div>
  )
}
