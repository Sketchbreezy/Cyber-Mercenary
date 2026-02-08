import { Link, useLocation } from 'react-router-dom';
import {
    ShieldCheck,
    Search,
    Target,
    Briefcase,
    Settings,
    Activity
} from 'lucide-react';
import { cn } from './ui/Button';

const navItems = [
    { name: 'Dashboard', path: '/', icon: Activity },
    { name: 'Scanner', path: '/scanner', icon: Search },
    { name: 'Bounties', path: '/bounties', icon: Target },
    { name: 'Gigs', path: '/gigs', icon: Briefcase },
    { name: 'Settings', path: '/settings', icon: Settings },
];

export default function Sidebar() {
    const location = useLocation();

    return (
        <div className="w-64 border-r border-white/10 bg-surface/50 backdrop-blur-md flex flex-col">
            <div className="h-16 flex items-center px-6 border-b border-white/10">
                <ShieldCheck className="w-8 h-8 text-primary mr-3" />
                <span className="font-mono font-bold text-lg tracking-wider text-white">
                    CYBER<span className="text-primary">MERC</span>
                </span>
            </div>

            <nav className="flex-1 p-4 space-y-2">
                {navItems.map((item) => {
                    const isActive = location.pathname === item.path;
                    return (
                        <Link
                            key={item.path}
                            to={item.path}
                            className={cn(
                                'flex items-center px-4 py-3 rounded-md transition-all group',
                                isActive
                                    ? 'bg-primary/10 text-primary border border-primary/20 shadow-[0_0_10px_rgba(0,240,255,0.1)]'
                                    : 'text-text-secondary hover:text-white hover:bg-white/5'
                            )}
                        >
                            <item.icon className={cn("w-5 h-5 mr-3 transition-colors", isActive ? "text-primary" : "group-hover:text-white")} />
                            <span className="font-medium">{item.name}</span>
                        </Link>
                    );
                })}
            </nav>

            <div className="p-4 border-t border-white/10">
                <div className="flex items-center space-x-3 px-2 py-2">
                    <div className="w-2 h-2 rounded-full bg-success animate-pulse" />
                    <span className="text-xs text-text-muted font-mono">SYSTEM ONLINE</span>
                </div>
            </div>
        </div>
    );
}
