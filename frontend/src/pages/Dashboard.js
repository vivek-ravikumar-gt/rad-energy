import { useEffect, useState } from 'react';
import axios from 'axios';
import { Building2, Zap, TrendingUp, Leaf, ArrowRight, Map, Mail } from 'lucide-react';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const Dashboard = () => {
  const [stats, setStats] = useState(null);
  const [topProspects, setTopProspects] = useState([]);
  const [clusters, setClusters] = useState([]);
  const [loading, setLoading] = useState(true);
  const [seeding, setSeeding] = useState(false);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const [statsRes, prospectsRes, clustersRes] = await Promise.all([
        axios.get(`${API}/dashboard/stats`),
        axios.get(`${API}/facilities/top/prospects?limit=5`),
        axios.get(`${API}/clusters`)
      ]);

      setStats(statsRes.data);
      setTopProspects(prospectsRes.data);
      setClusters(clustersRes.data.slice(0, 5));
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      if (error.response?.status !== 404) {
        toast.error('Failed to load dashboard data');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleSeedData = async () => {
    setSeeding(true);
    try {
      const response = await axios.post(`${API}/seed-data`);
      toast.success(response.data.message);
      fetchDashboardData();
    } catch (error) {
      console.error('Error seeding data:', error);
      toast.error('Failed to seed data');
    } finally {
      setSeeding(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96" data-testid="dashboard-loading">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
      </div>
    );
  }

  if (!stats || stats.total_facilities === 0) {
    return (
      <div className="flex flex-col items-center justify-center h-96 gap-6" data-testid="empty-state">
        <div className="text-center space-y-2">
          <h2 className="text-3xl font-bold font-heading text-primary">Welcome to RAD</h2>
          <p className="text-muted-foreground">Renewable Acquisition & Discovery Platform</p>
          <p className="text-sm text-muted-foreground max-w-md mx-auto mt-4">
            Get started by seeding the database with sample industrial facilities from major clusters.
          </p>
        </div>
        <Button
          onClick={handleSeedData}
          disabled={seeding}
          size="lg"
          className="gradient-accent text-white"
          data-testid="seed-data-button"
        >
          {seeding ? 'Seeding Data...' : 'Seed Sample Data'}
        </Button>
      </div>
    );
  }

  const statCards = [
    {
      title: 'Total Facilities',
      value: stats.total_facilities,
      icon: Building2,
      color: 'text-blue-600',
      bgColor: 'bg-blue-50',
      testId: 'stat-total-facilities'
    },
    {
      title: 'Solar Potential',
      value: `${stats.total_solar_potential_kw.toLocaleString()} kW`,
      icon: Zap,
      color: 'text-amber-600',
      bgColor: 'bg-amber-50',
      testId: 'stat-solar-potential'
    },
    {
      title: 'Power Demand',
      value: `${stats.total_power_demand_mw.toFixed(1)} MW`,
      icon: TrendingUp,
      color: 'text-purple-600',
      bgColor: 'bg-purple-50',
      testId: 'stat-power-demand'
    },
    {
      title: 'Avg Opportunity Score',
      value: stats.avg_opportunity_score,
      icon: Leaf,
      color: 'text-green-600',
      bgColor: 'bg-green-50',
      testId: 'stat-avg-score'
    },
  ];

  return (
    <div className="space-y-8" data-testid="dashboard">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight font-heading text-primary lg:text-5xl">
          Dashboard
        </h1>
        <p className="text-muted-foreground mt-2">Overview of renewable energy opportunities</p>
      </div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        {statCards.map((stat) => {
          const Icon = stat.icon;
          return (
            <Card key={stat.title} className="stat-card" data-testid={stat.testId}>
              <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
                <CardTitle className="text-sm font-medium text-muted-foreground">
                  {stat.title}
                </CardTitle>
                <div className={`${stat.bgColor} ${stat.color} p-2 rounded-md`}>
                  <Icon className="h-4 w-4" strokeWidth={2} />
                </div>
              </CardHeader>
              <CardContent>
                <div className="text-2xl font-bold font-heading text-primary">{stat.value}</div>
              </CardContent>
            </Card>
          );
        })}
      </div>

      {/* Main Content Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Top Prospects */}
        <Card className="lg:col-span-2" data-testid="top-prospects-card">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl font-heading">Top Renewable Prospects</CardTitle>
                <CardDescription>Facilities ranked by opportunity score</CardDescription>
              </div>
              <Link to="/leads">
                <Button variant="ghost" size="sm" data-testid="view-all-leads">
                  View All
                  <ArrowRight className="ml-2 h-4 w-4" />
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {topProspects.map((facility, index) => (
                <Link
                  key={facility.id}
                  to={`/facilities/${facility.id}`}
                  className="block"
                  data-testid={`prospect-${index}`}
                >
                  <div className="flex items-center justify-between p-4 rounded-lg border border-border hover:border-accent hover:bg-muted/50 transition-all">
                    <div className="flex-1">
                      <h4 className="font-semibold text-primary">{facility.company_name}</h4>
                      <p className="text-sm text-muted-foreground">
                        {facility.city}, {facility.state} • {facility.industry_type}
                      </p>
                    </div>
                    <div className="flex items-center gap-4">
                      <div className="text-right">
                        <p className="text-sm font-medium text-muted-foreground">Solar Potential</p>
                        <p className="text-lg font-semibold text-accent">{facility.estimated_solar_capacity_kw} kW</p>
                      </div>
                      <div className={`px-4 py-2 rounded-md font-bold ${
                        facility.renewable_opportunity_score >= 80 ? 'bg-green-100 text-green-700' :
                        facility.renewable_opportunity_score >= 60 ? 'bg-amber-100 text-amber-700' :
                        'bg-blue-100 text-blue-700'
                      }`}>
                        {facility.renewable_opportunity_score}
                      </div>
                    </div>
                  </div>
                </Link>
              ))}
            </div>
          </CardContent>
        </Card>

        {/* Top Clusters */}
        <Card data-testid="top-clusters-card">
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-xl font-heading">Industrial Clusters</CardTitle>
                <CardDescription>By power demand</CardDescription>
              </div>
              <Link to="/clusters">
                <Button variant="ghost" size="sm" data-testid="view-all-clusters">
                  View All
                </Button>
              </Link>
            </div>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {clusters.map((cluster, index) => (
                <div key={index} className="space-y-2" data-testid={`cluster-${index}`}>
                  <div className="flex items-center justify-between">
                    <div className="flex-1">
                      <h4 className="font-semibold text-sm text-primary">{cluster.cluster_name}</h4>
                      <p className="text-xs text-muted-foreground">
                        {cluster.city} • {cluster.company_count} facilities
                      </p>
                    </div>
                    <div className="text-right">
                      <p className="text-sm font-bold text-primary">{cluster.total_power_demand_mw.toFixed(1)} MW</p>
                    </div>
                  </div>
                  {index < clusters.length - 1 && <div className="border-b border-border"></div>}
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Quick Actions */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <Map className="h-8 w-8 text-accent mb-2" strokeWidth={1.5} />
            <CardTitle className="font-heading">Geographic View</CardTitle>
            <CardDescription>Visualize facilities on an interactive map</CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/map">
              <Button className="w-full" variant="outline" data-testid="goto-map">
                Open Map View
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <Building2 className="h-8 w-8 text-accent mb-2" strokeWidth={1.5} />
            <CardTitle className="font-heading">Explore Facilities</CardTitle>
            <CardDescription>Search and filter industrial facilities</CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/facilities">
              <Button className="w-full" variant="outline" data-testid="goto-facilities">
                Browse Facilities
              </Button>
            </Link>
          </CardContent>
        </Card>

        <Card className="hover:shadow-lg transition-shadow">
          <CardHeader>
            <Mail className="h-8 w-8 text-accent mb-2" strokeWidth={1.5} />
            <CardTitle className="font-heading">AI Email Generator</CardTitle>
            <CardDescription>Create personalized outreach emails</CardDescription>
          </CardHeader>
          <CardContent>
            <Link to="/email-generator">
              <Button className="w-full gradient-accent text-white" data-testid="goto-email">
                Generate Emails
              </Button>
            </Link>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default Dashboard;