import { createConfig, http } from 'wagmi'
import { mainnet, monad } from 'wagmi/chains'
import { injected, walletConnect } from 'wagmi/connectors'
import { QueryClient } from '@tanstack/react-query'
import { cookieStorage, createStorage, createCookieStorage } from 'wagmi'

const projectId = import.meta.env.VITE_WALLET_CONNECT_PROJECT_ID || 'YOUR_PROJECT_ID'

export const config = createConfig({
  chains: [mainnet, monad],
  connectors: [
    injected(),
    walletConnect({ projectId, showQrModal: true }),
  ],
  transports: {
    [mainnet.id]: http(),
    [monad.id]: http('https://rpc.monad.xyz'),
  },
  ssr: true,
  storage: createStorage({
    storage: typeof window !== 'undefined' ? localStorage : createCookieStorage(),
  }),
})

declare module 'wagmi' {
  interface Register {
    config: typeof config
  }
}

export const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      refetchOnWindowFocus: false,
      retry: 1,
      staleTime: 1000 * 60 * 5,
    },
  },
})
