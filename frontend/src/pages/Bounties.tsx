import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Globe, Clock } from 'lucide-react';

const bounties = [
    {
        id: 1,
        title: 'Arbitrage Loop in DEX Pool',
        reward: '5.0 ETH',
        severity: 'High',
        status: 'Open',
        protocol: 'Sienna Swap'
    },
    {
        id: 2,
        title: 'Reentrancy in Staking Contract',
        reward: '12.5 ETH',
        severity: 'Critical',
        status: 'Open',
        protocol: 'YieldMaster'
    },
    {
        id: 3,
        title: 'Gas Optimization for Router',
        reward: '1.0 ETH',
        severity: 'Low',
        status: 'Open',
        protocol: 'FastRoute'
    },
];

export default function Bounties() {
    return (
        <div className="space-y-6">
            <div className="flex justify-between items-center">
                <h1 className="text-3xl font-bold text-white tracking-wider">
                    ACTIVE <span className="text-primary">BOUNTIES</span>
                </h1>
                <Button variant="outline">Post Bounty</Button>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {bounties.map((bounty) => (
                    <Card key={bounty.id} className="relative overflow-hidden group hover:border-primary/50 transition-all cursor-pointer">
                        <div className="absolute top-0 right-0 p-4">
                            <Badge variant={
                                bounty.severity === 'Critical' ? 'danger' :
                                    bounty.severity === 'High' ? 'warning' : 'default'
                            }>
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
                                {bounty.reward}
                            </span>
                            <Button size="sm" variant="secondary">View Details</Button>
                        </div>
                    </Card>
                ))}
            </div>
        </div>
    );
}
