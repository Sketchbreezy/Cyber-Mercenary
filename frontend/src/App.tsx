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
        <Route path="/scanner" element={<Scanner />} />
        <Route path="/bounties" element={<Bounties />} />
        <Route path="/gigs" element={<Gigs />} />
        <Route path="/settings" element={<Settings />} />
      </Routes>
    </Layout>
  );
}

export default App;
