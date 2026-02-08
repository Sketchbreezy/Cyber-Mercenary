import { Routes, Route } from 'react-router-dom';
import Layout from './components/Layout';
import Dashboard from './pages/Dashboard';
import Scanner from './pages/Scanner';
import Bounties from './pages/Bounties';
import Gigs from './pages/Gigs';
import Settings from './pages/Settings';

function App() {
  return (
    <Layout>
      <Routes>
        <Route path="/" element={<Dashboard />} />
        <Route path="/bounty-board" element={<Bounties />} />
        <Route path="/agent-control" element={<Gigs />} />
        <Route path="/scanner" element={<Scanner />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  );
}

export default App;
