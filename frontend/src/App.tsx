import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { UserProvider } from '@/context/UserContext';
import { Layout } from '@/layouts/Layout';
import { OverviewDashboard } from '@/pages/OverviewDashboard';
import { AskKnowledge } from '@/pages/AskKnowledge';
import { KnowledgeLibrary } from '@/pages/KnowledgeLibrary';
import { DocumentDetails } from '@/pages/DocumentDetails';
import { SavedItems } from '@/pages/SavedItems';
import { RecentActivity } from '@/pages/RecentActivity';
import { EscalationCenter } from '@/pages/EscalationCenter';
import { Analytics } from '@/pages/Analytics';
import { DocumentManagement } from '@/pages/DocumentManagement';
import { Settings } from '@/pages/Settings';

export default function App() {
  return (
    <BrowserRouter>
      <UserProvider>
        <Layout>
          <Routes>
            <Route path="/" element={<OverviewDashboard />} />
            <Route path="/ask" element={<AskKnowledge />} />
            <Route path="/library" element={<KnowledgeLibrary />} />
            <Route path="/library/:id" element={<DocumentDetails />} />
            <Route path="/saved" element={<SavedItems />} />
            <Route path="/activity" element={<RecentActivity />} />
            <Route path="/escalation" element={<EscalationCenter />} />
            <Route path="/analytics" element={<Analytics />} />
            <Route path="/documents" element={<DocumentManagement />} />
            <Route path="/settings" element={<Settings />} />
          </Routes>
        </Layout>
      </UserProvider>
    </BrowserRouter>
  );
}
