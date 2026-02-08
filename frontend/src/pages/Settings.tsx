import { useState } from 'react'
import { motion } from 'framer-motion'
import { useAccount, useChainId, useSwitchChain } from 'wagmi'
import { Settings as SettingsIcon, Wallet, Bell, Shield, Globe, Palette, RefreshCw, Copy, ExternalLink, Check, ChevronRight } from 'lucide-react'
import { Card } from '../components/ui/Card'
import { Button } from '../components/ui/Button'
import { Input } from '../components/ui/Input'
import { Badge } from '../components/ui/Badge'

export default function Settings() {
  const { address, isConnected, chainId } = useAccount()
  const { switchChain } = useSwitchChain()
  const [copied, setCopied] = useState(false)
  const [activeTab, setActiveTab] = useState('wallet')
  const [notifications, setNotifications] = useState({
    scans: true,
    bounties: true,
    earnings: false,
    updates: true,
  })
  const [rpcUrl, setRpcUrl] = useState('https://rpc.monad.xyz')

  const copyAddress = async () => {
    if (address) {
      await navigator.clipboard.writeText(address)
      setCopied(true)
      setTimeout(() => setCopied(false), 2000)
    }
  }

  const formatAddress = (addr: string) => {
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`
  }

  const networks = [
    { id: 1, name: 'Ethereum', rpc: 'https://eth.drpc.org', explorer: 'https://etherscan.io' },
    { id: 10143, name: 'Monad Testnet', rpc: 'https://rpc.monad.xyz', explorer: 'https://testnet.monad.xyz' },
    { id: 8545, name: 'Local', rpc: 'http://localhost:8545', explorer: 'http://localhost:8545' },
  ]

  const tabs = [
    { id: 'wallet', label: 'Wallet', icon: Wallet },
    { id: 'network', label: 'Network', icon: Globe },
    { id: 'notifications', label: 'Notifications', icon: Bell },
    { id: 'security', label: 'Security', icon: Shield },
  ]

  return (
    <div className="space-y-6">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
      >
        <h1 className="text-3xl font-bold text-white tracking-wider flex items-center space-x-3">
          <SettingsIcon className="w-8 h-8 text-primary" />
          <span>SYSTEM <span className="text-primary">SETTINGS</span></span>
        </h1>
        <p className="text-text-secondary mt-2">
          Manage your wallet connections, preferences, and security settings
        </p>
      </motion.div>

      <div className="flex flex-col lg:flex-row gap-6">
        {/* Sidebar Tabs */}
        <motion.div
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="lg:w-64 flex-shrink-0"
        >
          <Card className="p-2">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`w-full flex items-center space-x-3 px-4 py-3 rounded-md transition-all ${
                  activeTab === tab.id
                    ? 'bg-primary/10 text-primary border border-primary/20'
                    : 'text-text-secondary hover:text-white hover:bg-white/5'
                }`}
              >
                <tab.icon className="w-5 h-5" />
                <span className="font-medium">{tab.label}</span>
                {activeTab === tab.id && (
                  <ChevronRight className="w-4 h-4 ml-auto" />
                )}
              </button>
            ))}
          </Card>
        </motion.div>

        {/* Content Area */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.1 }}
          className="flex-1"
        >
          {/* Wallet Settings */}
          {activeTab === 'wallet' && (
            <div className="space-y-6">
              <Card>
                <h3 className="text-lg font-bold text-white mb-4">Connected Wallet</h3>
                {isConnected && address ? (
                  <div className="space-y-4">
                    <div className="flex items-center justify-between p-4 bg-surface/50 rounded border border-white/10">
                      <div className="flex items-center space-x-4">
                        <div className="w-12 h-12 rounded-full bg-primary/20 flex items-center justify-center">
                          <Wallet className="w-6 h-6 text-primary" />
                        </div>
                        <div>
                          <p className="font-mono text-lg text-white">{formatAddress(address)}</p>
                          <p className="text-sm text-text-muted">Connected</p>
                        </div>
                      </div>
                      <div className="flex items-center space-x-2">
                        <button
                          onClick={copyAddress}
                          className="p-2 hover:bg-white/10 rounded transition-colors"
                          title="Copy address"
                        >
                          {copied ? <Check className="w-5 h-5 text-success" /> : <Copy className="w-5 h-5 text-text-muted" />}
                        </button>
                        <a
                          href={`https://testnet.monad.xyz/address/${address}`}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="p-2 hover:bg-white/10 rounded transition-colors"
                        >
                          <ExternalLink className="w-5 h-5 text-text-muted" />
                        </a>
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-4 bg-surface/30 rounded border border-white/5">
                        <p className="text-xs text-text-muted mb-1">Network</p>
                        <Badge variant="success">{chainId === 10143 ? 'Monad Testnet' : 'Ethereum'}</Badge>
                      </div>
                      <div className="p-4 bg-surface/30 rounded border border-white/5">
                        <p className="text-xs text-text-muted mb-1">Status</p>
                        <Badge variant="success">Active</Badge>
                      </div>
                    </div>
                  </div>
                ) : (
                  <div className="text-center py-8">
                    <Wallet className="w-12 h-12 text-text-muted mx-auto mb-4 opacity-50" />
                    <p className="text-text-secondary mb-4">No wallet connected</p>
                    <Button>Connect Wallet</Button>
                  </div>
                )}
              </Card>

              <Card>
                <h3 className="text-lg font-bold text-white mb-4">Wallet Preferences</h3>
                <div className="space-y-4">
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-white font-medium">Auto-connect</p>
                      <p className="text-sm text-text-muted">Automatically connect on page load</p>
                    </div>
                    <input type="checkbox" defaultChecked className="toggle" />
                  </div>
                  <div className="flex items-center justify-between">
                    <div>
                      <p className="text-white font-medium">Request signatures</p>
                      <p className="text-sm text-text-muted">Ask before signing transactions</p>
                    </div>
                    <input type="checkbox" defaultChecked className="toggle" />
                  </div>
                </div>
              </Card>
            </div>
          )}

          {/* Network Settings */}
          {activeTab === 'network' && (
            <div className="space-y-6">
              <Card>
                <h3 className="text-lg font-bold text-white mb-4 flex items-center space-x-2">
                  <Globe className="w-5 h-5 text-primary" />
                  <span>Network Configuration</span>
                </h3>
                <div className="space-y-3">
                  {networks.map((network) => (
                    <div
                      key={network.id}
                      className={`p-4 rounded border cursor-pointer transition-all ${
                        chainId === network.id
                          ? 'bg-primary/10 border-primary/30'
                          : 'bg-surface/30 border-white/10 hover:border-white/20'
                      }`}
                      onClick={() => switchChain?.({ chainId: network.id })}
                    >
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-3">
                          <div className={`w-3 h-3 rounded-full ${chainId === network.id ? 'bg-primary' : 'bg-text-muted'}`} />
                          <div>
                            <p className="text-white font-medium">{network.name}</p>
                            <p className="text-xs text-text-muted font-mono">{network.rpc}</p>
                          </div>
                        </div>
                        {chainId === network.id && <Badge variant="success">Active</Badge>}
                      </div>
                    </div>
                  ))}
                </div>
              </Card>

              <Card>
                <h3 className="text-lg font-bold text-white mb-4">Custom RPC</h3>
                <div className="space-y-4">
                  <div>
                    <label className="text-sm text-text-muted mb-2 block">RPC URL</label>
                    <Input
                      value={rpcUrl}
                      onChange={(e) => setRpcUrl(e.target.value)}
                      placeholder="https://..."
                      className="font-mono"
                    />
                  </div>
                  <Button variant="outline">Test Connection</Button>
                </div>
              </Card>
            </div>
          )}

          {/* Notification Settings */}
          {activeTab === 'notifications' && (
            <Card>
              <h3 className="text-lg font-bold text-white mb-4 flex items-center space-x-2">
                <Bell className="w-5 h-5 text-primary" />
                <span>Notification Preferences</span>
              </h3>
              <div className="space-y-4">
                {[
                  { key: 'scans', label: 'Scan completions', desc: 'Get notified when scans finish' },
                  { key: 'bounties', label: 'New bounties', desc: 'Alerts for new vulnerability bounties' },
                  { key: 'earnings', label: 'Earnings', desc: 'Notifications for claimed rewards' },
                  { key: 'updates', label: 'System updates', desc: 'Important platform announcements' },
                ].map((item) => (
                  <div key={item.key} className="flex items-center justify-between p-4 bg-surface/30 rounded border border-white/5">
                    <div>
                      <p className="text-white font-medium">{item.label}</p>
                      <p className="text-sm text-text-muted">{item.desc}</p>
                    </div>
                    <button
                      onClick={() => setNotifications({ ...notifications, [item.key]: !notifications[item.key as keyof typeof notifications] })}
                      className={`w-12 h-6 rounded-full transition-colors relative ${
                        notifications[item.key as keyof typeof notifications] ? 'bg-primary' : 'bg-white/20'
                      }`}
                    >
                      <div className={`absolute top-1 w-4 h-4 rounded-full bg-white transition-transform ${
                        notifications[item.key as keyof typeof notifications] ? 'translate-x-7' : 'translate-x-1'
                      }`} />
                    </button>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {/* Security Settings */}
          {activeTab === 'security' && (
            <div className="space-y-6">
              <Card>
                <h3 className="text-lg font-bold text-white mb-4 flex items-center space-x-2">
                  <Shield className="w-5 h-5 text-primary" />
                  <span>Security Settings</span>
                </h3>
                <div className="space-y-4">
                  <div className="p-4 bg-surface/30 rounded border border-white/5">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-white font-medium">Two-Factor Authentication</p>
                      <Badge variant="warning">Coming Soon</Badge>
                    </div>
                    <p className="text-sm text-text-muted">Add an extra layer of security to your account</p>
                  </div>
                  <div className="p-4 bg-surface/30 rounded border border-white/5">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-white font-medium">Session Management</p>
                      <Button variant="ghost" size="sm">View Sessions</Button>
                    </div>
                    <p className="text-sm text-text-muted">Manage your active sessions and devices</p>
                  </div>
                  <div className="p-4 bg-surface/30 rounded border border-white/5">
                    <div className="flex items-center justify-between mb-2">
                      <p className="text-white font-medium">API Keys</p>
                      <Button variant="ghost" size="sm">Manage</Button>
                    </div>
                    <p className="text-sm text-text-muted">Control programmatic access to your account</p>
                  </div>
                </div>
              </Card>
            </div>
          )}
        </motion.div>
      </div>
    </div>
  )
}
