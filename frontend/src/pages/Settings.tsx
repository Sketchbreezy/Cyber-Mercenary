import { Card } from '../components/ui/Card';
import { Button } from '../components/ui/Button';

export default function Settings() {
    return (
        <div className="space-y-6">
            <h1 className="text-3xl font-bold text-white tracking-wider">
                SETTINGS
            </h1>

            <Card>
                <h3 className="text-xl font-bold mb-4">Connection</h3>
                <p className="text-sm text-text-secondary mb-4">
                    Configure RPC endpoints and API keys.
                </p>
                <Button>Save Configuration</Button>
            </Card>
        </div>
    );
}
