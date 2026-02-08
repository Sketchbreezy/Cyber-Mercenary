import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import { Card } from '../components/ui/Card'
import { Input } from '../components/ui/Input'
import { Button } from '../components/ui/Button'
import { Badge } from '../components/ui/Badge'
import { Search, ScanLine, AlertTriangle, CheckCircle, Clock, ExternalLink, Loader2 } from 'lucide-react'
import { apiClient } from '../lib/api'

interface ScanResult {
  scan_id: string
  contract_address: string
  status: string
  timestamp: string
  result?: {
    severity?: string
    findings?: string[]
  }
}

export default function Scanner() {
  const [address, setAddress] = useState('')
  const [scanning, setScanning] = useState(false)
  const [scans, setScans] = useState<ScanResult[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [scanSuccess, setScanSuccess] = useState(false)

  useEffect(() => {
    loadScans()
  }, [])

  async function loadScans() {
    try {
      const data = await apiClient.getRecentScans()
      setScans(data || [])
    } catch (err: any) {
      console.error('Failed to load scans:', err)
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  async function handleScan() {
    if (!address) return

    // Validate address format
    if (!address.startsWith('0x') || address.length !== 42) {
      setError('Invalid Ethereum address format')
      return
    }

    setScanning(true)
    setError(null)
    setScanSuccess(false)

    try {
      const result = await apiClient.scan(address)
      setScanSuccess(true)
      setAddress('')
      await loadScans()
      
      // Auto-hide success message after 3 seconds
      setTimeout(() => setScanSuccess(false), 3000)
    } catch (err: any) {
      setError(err.message || 'Scan failed. Please try again.')
      console.error('Scan error:', err)
    } finally {
      setScanning(false)
    }
  }

  const getStatusIcon = (status: string) => {
    switch (status.toLowerCase()) {
      case 'completed':
        return <CheckCircle className="w-4 h-4 text-success" />
      case 'failed':
        return <AlertTriangle className="w-4 h-4 text-accent" />
      case 'scanning':
        return <Loader2 className="w-4 h-4 text-warning animate-spin" />
      default:
        return <Clock className="w-4 h-4 text-text-muted" />
    }
  }

  const getStatusVariant = (status: string): 'success' | 'danger' | 'warning' | 'default' => {
    switch (status.toLowerCase()) {
      case 'completed':
        return 'success'
      case 'failed':
        return 'danger'
      case 'scanning':
        return 'warning'
      default:
        return 'default'
    }
  }

  const formatAddress = (addr: string) => {
    if (!addr) return 'Unknown'
    return `${addr.slice(0, 8)}...${addr.slice(-4)}`
  }

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-white tracking-wider">
          CONTRACT <span className="text-primary">SCANNER</span>
        </h1>
        <p className="text-text-secondary mt-2">
          Analyze smart contracts for vulnerabilities using AI-powered security scanning
        </p>
      </motion.div>

      {/* Scan Input Card */}
      <Card className="relative overflow-hidden">
        {scanSuccess && (
          <motion.div
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="absolute top-0 left-0 right-0 bg-success/10 border-b border-success/20 px-4 py-2 flex items-center justify-center space-x-2"
          >
            <CheckCircle className="w-4 h-4 text-success" />
            <span className="text-sm text-success">Scan submitted successfully!</span>
          </motion.div>
        )}

        <div className={`flex flex-col md:flex-row gap-4 items-end pt-${scanSuccess ? 8 : ''}`}>
          <div className="flex-1 w-full space-y-2">
            <label className="text-sm font-medium text-text-secondary flex items-center space-x-2">
              <ScanLine className="w-4 h-4" />
              <span>Contract Address (EVM)</span>
            </label>
            <Input
              placeholder="0x..."
              value={address}
              onChange={(e) => {
                setAddress(e.target.value)
                if (error) setError(null)
              }}
              className="font-mono"
              disabled={scanning}
            />
          </div>
          <Button
            onClick={handleScan}
            disabled={scanning || !address}
            className="w-full md:w-auto min-w-[140px]"
          >
            {scanning ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Scanning...
              </>
            ) : (
              <>
                <Search className="w-4 h-4 mr-2" />
                Start Analysis
              </>
            )}
          </Button>
        </div>
        
        {error && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="mt-4 p-3 bg-accent/10 border border-accent/20 rounded flex items-center space-x-2"
          >
            <AlertTriangle className="w-4 h-4 text-accent flex-shrink-0" />
            <span className="text-sm text-accent">{error}</span>
          </motion.div>
        )}
      </Card>

      {/* Recent Scans */}
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ delay: 0.1 }}
      >
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-xl font-bold text-white flex items-center space-x-2">
            <Clock className="w-5 h-5 text-primary" />
            <span>Recent Scans</span>
          </h3>
          <Button variant="ghost" size="sm" onClick={loadScans}>
            Refresh
          </Button>
        </div>

        {loading ? (
          <Card className="flex items-center justify-center py-12">
            <Loader2 className="w-8 h-8 text-primary animate-spin" />
            <span className="ml-3 text-text-muted">Loading scans...</span>
          </Card>
        ) : scans.length > 0 ? (
          <div className="space-y-3">
            {scans.map((scan, index) => (
              <motion.div
                key={scan.scan_id}
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.05 }}
              >
                <Card className="flex flex-col md:flex-row md:items-center justify-between p-4 hover:border-primary/30 transition-colors">
                  <div className="flex items-center space-x-4">
                    <div className={`p-3 rounded-full ${
                      scan.status === 'completed' ? 'bg-success/10' : 
                      scan.status === 'failed' ? 'bg-accent/10' : 'bg-warning/10'
                    }`}>
                      {getStatusIcon(scan.status)}
                    </div>
                    <div>
                      <p className="font-mono text-sm text-white flex items-center space-x-2">
                        <span>{formatAddress(scan.contract_address)}</span>
                        <button 
                          onClick={() => navigator.clipboard.writeText(scan.contract_address)}
                          className="p-1 hover:bg-white/10 rounded transition-colors"
                          title="Copy address"
                        >
                          <Copy className="w-3 h-3 text-text-muted" />
                        </button>
                        <a 
                          href={`https://testnet.monad.xyz/address/${scan.contract_address}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-1 hover:bg-white/10 rounded transition-colors"
                        >
                          <ExternalLink className="w-3 h-3 text-text-muted" />
                        </a>
                      </p>
                      <p className="text-xs text-text-muted mt-1">
                        {new Date(scan.timestamp).toLocaleString()}
                      </p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-3 mt-4 md:mt-0">
                    <Badge variant={getStatusVariant(scan.status)}>
                      {scan.status}
                    </Badge>
                    <Button variant="ghost" size="sm">
                      View Report
                    </Button>
                  </div>
                </Card>
              </motion.div>
            ))}
          </div>
        ) : (
          <Card className="flex flex-col items-center justify-center py-12 text-center">
            <Search className="w-12 h-12 text-text-muted mb-4 opacity-50" />
            <h3 className="text-lg font-medium text-white mb-2">No scans yet</h3>
            <p className="text-text-secondary text-sm max-w-md">
              Enter a contract address above to start your first security analysis
            </p>
          </Card>
        )}
      </motion.div>
    </div>
  )
}
