import { Card } from '../components/ui/Card';
import { ShieldCheck, Bug, DollarSign } from 'lucide-react';

const stats = [
    { name: 'Contracts Scanned', value: '1,234', icon: ShieldCheck, color: 'text-primary' },
    { name: 'Vulnerabilities Found', value: '56', icon: Bug, color: 'text-accent' },
    { name: 'Active Bounties', value: '12', icon: Target, color: 'text-warning' }, // Target is imported below
    { name: 'Total Earned', value: '45.2 ETH', icon: DollarSign, color: 'text-success' },
];

import { Target } from 'lucide-react'; // Fix missing import

export default function Dashboard() {
    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold text-white tracking-wider">
                OPERATIONAL <span className="text-primary">OVERVIEW</span>
            </h1>

            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                {stats.map((stat) => (
                    <Card key={stat.name} className="flex items-center space-x-4">
                        <div className={`p-3 rounded-full bg-surface ${stat.color} bg-opacity-10`}>
                            <stat.icon className={`w-6 h-6 ${stat.color}`} />
                        </div>
                        <div>
                            <p className="text-sm font-medium text-text-muted">{stat.name}</p>
                            <p className="text-2xl font-bold text-white">{stat.value}</p>
                        </div>
                    </Card>
                ))}
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                <Card className="h-96">
                    <h3 className="text-xl font-bold mb-4">Recent Activity</h3>
                    <div className="space-y-4">
                        {/* Placeholder for activity feed */}
                        <div className="flex items-center text-sm text-text-secondary">
                            <span className="w-2 h-2 rounded-full bg-success mr-2" />
                            Scan completed for 0x123...abc
                        </div>
                        <div className="flex items-center text-sm text-text-secondary">
                            <span className="w-2 h-2 rounded-full bg-warning mr-2" />
                            New bounty available: DefiProtocol V2
                        </div>
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
                            <span className="text-success">SYNCED (Block 192834)</span>
                        </div>
                    </div>
                </Card>
            </div>
        </div>
    );
}
