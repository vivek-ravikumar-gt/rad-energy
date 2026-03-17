import { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Network, Building2, Zap, TrendingUp } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const ClusterIntelligence = () => {
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchClusters();
  }, []);

  const fetchClusters = async () => {
    try {
      const response = await axios.get(`${API}/clusters`);
      setClusters(response.data);
    } catch (error) {
      console.error('Error fetching clusters:', error);
      toast.error('Failed to load cluster data');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96" data-testid="clusters-loading">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="cluster-intelligence">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight font-heading text-primary lg:text-5xl">
          Industrial Cluster Intelligence
        </h1>
        <p className="text-muted-foreground mt-2">Aggregated insights by industrial clusters</p>
      </div>

      {/* Clusters Grid */}
      {clusters.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Network className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-primary mb-2">No cluster data available</h3>
            <p className="text-sm text-muted-foreground">Add facilities to see cluster intelligence</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {clusters.map((cluster, index) => (
            <Card key={index} className="cluster-card" data-testid={`cluster-card-${index}`}>
              <CardHeader>
                <div className="flex items-start justify-between gap-2">
                  <div className="flex-1">
                    <CardTitle className="text-xl font-heading">
                      {cluster.cluster_name}
                    </CardTitle>
                    <CardDescription className="mt-1">
                      {cluster.city}, {cluster.state}
                    </CardDescription>
                  </div>
                  <div className="w-12 h-12 rounded-lg bg-accent/10 flex items-center justify-center">
                    <Network className="h-6 w-6 text-accent" strokeWidth={2} />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="space-y-4">
                  {/* Companies Count */}
                  <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Building2 className="h-5 w-5 text-blue-600" />
                      <span className="text-sm font-medium text-muted-foreground">Companies</span>
                    </div>
                    <span className="text-lg font-bold text-primary">{cluster.company_count}</span>
                  </div>

                  {/* Total Power Demand */}
                  <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <TrendingUp className="h-5 w-5 text-purple-600" />
                      <span className="text-sm font-medium text-muted-foreground">Power Demand</span>
                    </div>
                    <span className="text-lg font-bold text-primary">{cluster.total_power_demand_mw} MW</span>
                  </div>

                  {/* Total Solar Potential */}
                  <div className="flex items-center justify-between p-3 bg-muted/50 rounded-lg">
                    <div className="flex items-center gap-2">
                      <Zap className="h-5 w-5 text-amber-600" />
                      <span className="text-sm font-medium text-muted-foreground">Solar Potential</span>
                    </div>
                    <span className="text-lg font-bold text-primary">{cluster.total_solar_potential_kw} kW</span>
                  </div>

                  {/* Avg Opportunity Score */}
                  <div className="pt-3 border-t border-border">
                    <div className="flex items-center justify-between">
                      <span className="text-sm font-medium text-muted-foreground">Avg Opportunity Score</span>
                      <div className={`px-3 py-1 rounded-md font-bold ${
                        cluster.avg_opportunity_score >= 80 ? 'bg-green-100 text-green-700' :
                        cluster.avg_opportunity_score >= 60 ? 'bg-amber-100 text-amber-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {cluster.avg_opportunity_score}
                      </div>
                    </div>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Summary Stats */}
      {clusters.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-heading">Cluster Summary</CardTitle>
            <CardDescription>Aggregated statistics across all clusters</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Clusters</p>
                <p className="text-3xl font-bold text-primary mt-1">{clusters.length}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Companies</p>
                <p className="text-3xl font-bold text-primary mt-1">
                  {clusters.reduce((sum, c) => sum + c.company_count, 0)}
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Power Demand</p>
                <p className="text-3xl font-bold text-primary mt-1">
                  {clusters.reduce((sum, c) => sum + c.total_power_demand_mw, 0).toFixed(1)} MW
                </p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Total Solar Potential</p>
                <p className="text-3xl font-bold text-primary mt-1">
                  {clusters.reduce((sum, c) => sum + c.total_solar_potential_kw, 0).toFixed(0)} kW
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ClusterIntelligence;