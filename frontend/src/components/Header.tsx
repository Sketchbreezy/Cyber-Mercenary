import { useAccount, useConnect, useDisconnect, useBalance, useChainId } from 'wagmi'
import { useLocation } from 'react-router-dom'
import { useState, useEffect, useRef } from 'react'
import { motion, AnimatePresence } from 'framer-motion'
import { Wallet, ChevronDown, Copy, ExternalLink, Settings, User, LogOut } from 'lucide-react'
import { Button } from './ui/Button'
import { Card } from './ui/Card'

const pageTitles: Record<string, string> = {
  '/': 'OPERATIONAL OVERVIEW',
  '/scanner': 'CONTRACT SCANNER',
  '/bounties': 'ACTIVE BOUNTIES',
  '/gigs': 'AGENT MARKETPLACE',
  '/settings': 'SYSTEM SETTINGS',
}

export default function Header() {
  const { address, isConnected, chainId } = useAccount()
  const { connect, connectors } = useConnect()
  const { disconnect } = useDisconnect()
  const { data: balance } = useBalance({ address, enabled: !!address })
  const chain = useChainId()
  const location = useLocation()
  const [showDropdown, setShowDropdown] = useState(false)
  const [copied, setCopied] = useState(false)
  const [showSettings, setShowSettings] = useState(false)
  const dropdownRef = useRef<HTMLDivElement>(null)

  const pageTitle = pageTitles[location.pathname] || 'DASHBOARD'

  // Close dropdown when clicking outside
  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false)
      }
    }
    document.addEventListener('mousedown', handleClickOutside)
    return () => document.removeEventListener('mousedown', handleClickOutside)
  }, [])

  const handleConnect = async () => {
    const connector = connectors.find((c) => c.id === 'io.metamask') || connectors[0]
    if (connector) {
      try {
        await connect({ connector })
      } catch (error) {
        console.error('Failed to connect:', error)
      }
    }
  }

  const copyAddress = async () => {
    if (address) {
      try {
        await navigator.clipboard.writeText(address)
        setCopied(true)
        setTimeout(() => setCopied(false), 2000)
      } catch (err) {
        console.error('Failed to copy:', err)
      }
    }
  }

  const openExplorer = () => {
    if (address && chain) {
      const explorers: Record<number, string> = {
        1: 'https://etherscan.io',
        10143: 'https://testnet.monad.xyz',
        8545: 'http://localhost:8545',
      }
      const explorer = explorers[chain] || 'https://etherscan.io'
      window.open(`${explorer}/address/${address}`, '_blank')
    }
  }

  const handleDisconnect = () => {
    try {
      disconnect()
      setShowDropdown(false)
    } catch (err) {
      console.error('Failed to disconnect:', err)
    }
  }

  const formatAddress = (addr: string) => {
    return `${addr.slice(0, 6)}...${addr.slice(-4)}`
  }

  const formatBalance = (bal: typeof balance) => {
    if (!bal) return '0 ETH'
    const formatted = parseFloat(bal.formatted).toFixed(4)
    return `${formatted} ${bal.symbol}`
  }

  const networkName = () => {
    switch (chain) {
      case 1: return 'ETHEREUM'
      case 10143: return 'MONAD'
      case 8545: return 'LOCAL'
      default: return `CHAIN ${chain}`
    }
  }

  return (
    <header className="h-16 border-b border-white/10 bg-surface/50 backdrop-blur-md flex items-center justify-between px-6">
      <div className="flex items-center space-x-4">
        <motion.h2 
          initial={{ opacity: 0, x: -20 }}
          animate={{ opacity: 1, x: 0 }}
          className="text-xl font-bold text-white tracking-wider"
        >
          {pageTitle.split(' ').slice(0, -1).join(' ')} <span className="text-primary">{pageTitle.split(' ').slice(-1)}</span>
        </motion.h2>
      </div>

      <div className="flex items-center space-x-4">
        {/* Network Indicator */}
        <div className="hidden md:flex items-center space-x-2 px-3 py-1.5 bg-surface/50 rounded border border-white/5">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-success animate-pulse' : 'bg-text-muted'}`} />
          <span className="text-xs font-mono text-text-muted">
            {isConnected ? networkName() : 'DISCONNECTED'}
          </span>
        </div>

        {isConnected && address ? (
          <div className="relative" ref={dropdownRef}>
            <motion.button
              whileHover={{ scale: 1.02 }}
              whileTap={{ scale: 0.98 }}
              onClick={() => setShowDropdown(!showDropdown)}
              className="flex items-center space-x-3 px-4 py-2 bg-surface/50 border border-white/10 rounded-lg hover:border-primary/30 transition-all"
            >
              <div className="text-right hidden lg:block">
                <p className="text-sm font-medium text-white">
                  {formatBalance(balance)}
                </p>
                <p className="text-xs font-mono text-text-muted">
                  {formatAddress(address)}
                </p>
              </div>
              <Wallet className="w-5 h-5 text-primary" />
              <ChevronDown className={`w-4 h-4 text-text-muted transition-transform ${showDropdown ? 'rotate-180' : ''}`} />
            </motion.button>

            <AnimatePresence>
              {showDropdown && (
                <>
                  <div className="fixed inset-0 z-40" onClick={() => setShowDropdown(false)} />
                  <motion.div
                    initial={{ opacity: 0, y: 10 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: 10 }}
                    transition={{ duration: 0.15 }}
                    className="absolute right-0 mt-2 w-72 glass-panel-dark z-50 overflow-hidden"
                  >
                    {/* Wallet Header */}
                    <div className="p-4 border-b border-white/10">
                      <p className="text-xs font-mono text-text-muted mb-3">CONNECTED WALLET</p>
                      <div className="flex items-center justify-between">
                        <div className="flex items-center space-x-2">
                          <div className="w-10 h-10 rounded-full bg-primary/20 flex items-center justify-center">
                            <User className="w-5 h-5 text-primary" />
                          </div>
                          <div>
                            <p className="font-mono text-sm text-white">{formatAddress(address)}</p>
                            <p className="text-xs text-success">Active</p>
                          </div>
                        </div>
                      </div>
                    </div>

                    {/* Quick Actions */}
                    <div className="p-2 border-b border-white/10">
                      <div className="grid grid-cols-2 gap-2">
                        <button 
                          onClick={copyAddress}
                          className="flex items-center justify-center space-x-2 p-2 hover:bg-white/5 rounded transition-colors"
                        >
                          {copied ? (
                            <span className="text-success text-xs font-medium">Copied!</span>
                          ) : (
                            <>
                              <Copy className="w-4 h-4 text-text-muted" />
                              <span className="text-xs text-text-secondary">Copy</span>
                            </>
                          )}
                        </button>
                        <button 
                          onClick={openExplorer}
                          className="flex items-center justify-center space-x-2 p-2 hover:bg-white/5 rounded transition-colors"
                        >
                          <ExternalLink className="w-4 h-4 text-text-muted" />
                          <span className="text-xs text-text-secondary">Explorer</span>
                        </button>
                      </div>
                    </div>

                    {/* Menu Items */}
                    <div className="p-2">
                      <button 
                        onClick={() => { setShowDropdown(false); setShowSettings(true); }}
                        className="flex items-center w-full px-3 py-2 space-x-3 hover:bg-white/5 rounded transition-colors"
                      >
                        <Settings className="w-4 h-4 text-text-muted" />
                        <span className="text-sm text-text-secondary">Wallet Settings</span>
                      </button>
                      <button 
                        onClick={handleDisconnect}
                        className="flex items-center w-full px-3 py-2 space-x-3 text-accent hover:bg-accent/10 rounded transition-colors"
                      >
                        <LogOut className="w-4 h-4" />
                        <span className="text-sm">Disconnect</span>
                      </button>
                    </div>
                  </motion.div>
                </>
              )}
            </AnimatePresence>
          </div>
        ) : (
          <Button
            variant="outline"
            className="font-mono text-sm"
            onClick={handleConnect}
          >
            <Wallet className="w-4 h-4 mr-2" />
            Connect Wallet
          </Button>
        )}
      </div>
    </header>
  )
}
