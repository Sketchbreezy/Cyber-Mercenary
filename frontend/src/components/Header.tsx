import { Button } from './ui/Button';
import { Wallet } from 'lucide-react';

export default function Header() {
    return (
        <header className="h-16 border-b border-white/10 bg-surface/50 backdrop-blur-md flex items-center justify-between px-6">
            <div className="flex items-center space-x-4">
                {/* Breadcrumbs or Title could go here */}
                <h2 className="text-xl font-bold text-white">Dashboard</h2>
            </div>

            <div className="flex items-center space-x-4">
                {/* Wallet Connect Placeholder - Will be replaced by Wagmi Button later */}
                <Button variant="outline" className="font-mono text-sm">
                    <Wallet className="w-4 h-4 mr-2" />
                    Connect Wallet
                </Button>
            </div>
        </header>
    );
}
