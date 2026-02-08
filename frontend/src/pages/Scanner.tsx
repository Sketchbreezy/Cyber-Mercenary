import { useState } from 'react';
import { Card } from '../components/ui/Card';
import { Input } from '../components/ui/Input';
import { Button } from '../components/ui/Button';
import { Badge } from '../components/ui/Badge';
import { Search } from 'lucide-react';

export default function Scanner() {
    const [address, setAddress] = useState('');
    const [scanning, setScanning] = useState(false);

    const handleScan = () => {
        if (!address) return;
        setScanning(true);
        // Simulate scan
        setTimeout(() => setScanning(false), 2000);
    };

    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold text-white tracking-wider">
                CONTRACT <span className="text-primary">SCANNER</span>
            </h1>

            <Card>
                <div className="flex flex-col md:flex-row gap-4 items-end">
                    <div className="flex-1 w-full space-y-2">
                        <label className="text-sm font-medium text-text-secondary">
                            Contract Address (EVM)
                        </label>
                        <Input
                            placeholder="0x..."
                            value={address}
                            onChange={(e) => setAddress(e.target.value)}
                            className="font-mono"
                        />
                    </div>
                    <Button
                        onClick={handleScan}
                        disabled={scanning}
                        className="w-full md:w-auto"
                    >
                        {scanning ? 'Scanning...' : 'Start Analysis'}
                    </Button>
                </div>
            </Card>

            <div className="mt-8">
                <h3 className="text-xl font-bold mb-4 text-white">Recent Scans</h3>
                <div className="space-y-4">
                    {/* Mock Data */}
                    {[1, 2, 3].map((i) => (
                        <Card key={i} className="flex items-center justify-between p-4">
                            <div className="flex items-center space-x-4">
                                <div className="p-2 rounded-full bg-surface border border-white/10">
                                    <Search className="w-5 h-5 text-primary" />
                                </div>
                                <div>
                                    <p className="font-mono text-sm text-white">0x71C...9B2{i}</p>
                                    <p className="text-xs text-text-muted">2 minutes ago</p>
                                </div>
                            </div>
                            <div className="flex items-center space-x-4">
                                <Badge variant={i === 1 ? 'danger' : 'success'}>
                                    {i === 1 ? 'Critical' : 'Safe'}
                                </Badge>
                                <Button variant="ghost" size="sm">View Report</Button>
                            </div>
                        </Card>
                    ))}
                </div>
            </div>
        </div>
    );
}
