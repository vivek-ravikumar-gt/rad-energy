import '@/App.css';
import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from '@/components/Layout';
import Dashboard from '@/pages/Dashboard';
import FacilitiesExplorer from '@/pages/FacilitiesExplorer';
import MapView from '@/pages/MapView';
import FacilityDetail from '@/pages/FacilityDetail';
import ClusterIntelligence from '@/pages/ClusterIntelligence';
import LeadGenerator from '@/pages/LeadGenerator';
import EmailGenerator from '@/pages/EmailGenerator';
import { Toaster } from '@/components/ui/sonner';

function App() {
  return (
    <div className="App">
      <BrowserRouter>
        <Routes>
          <Route path="/" element={<Layout />}>
            <Route index element={<Dashboard />} />
            <Route path="facilities" element={<FacilitiesExplorer />} />
            <Route path="facilities/:id" element={<FacilityDetail />} />
            <Route path="map" element={<MapView />} />
            <Route path="clusters" element={<ClusterIntelligence />} />
            <Route path="leads" element={<LeadGenerator />} />
            <Route path="email-generator" element={<EmailGenerator />} />
          </Route>
        </Routes>
      </BrowserRouter>
      <Toaster position="top-right" />
    </div>
  );
}

export default App;