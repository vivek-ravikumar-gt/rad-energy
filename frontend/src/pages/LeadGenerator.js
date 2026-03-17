import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Button } from '@/components/ui/button';
import { Zap, Building2, TrendingUp, MapPin, Mail, ArrowRight, Leaf } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const LeadGenerator = () => {
  const [prospects, setProspects] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchProspects();
  }, []);

  const fetchProspects = async () => {
    try {
      const response = await axios.get(`${API}/facilities/top/prospects?limit=50`);
      setProspects(response.data);
    } catch (error) {
      console.error('Error fetching prospects:', error);
      toast.error('Failed to load prospects');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96" data-testid="leads-loading">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="lead-generator">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight font-heading text-primary lg:text-5xl">
          Top Renewable Prospects
        </h1>
        <p className="text-muted-foreground mt-2">Facilities ranked by renewable opportunity score</p>
      </div>

      {/* Stats Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">High Priority Leads</CardTitle>
            <Zap className="h-5 w-5 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-heading text-primary">
              {prospects.filter(p => p.renewable_opportunity_score >= 80).length}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Score 80+</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Medium Priority Leads</CardTitle>
            <TrendingUp className="h-5 w-5 text-amber-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-heading text-primary">
              {prospects.filter(p => p.renewable_opportunity_score >= 60 && p.renewable_opportunity_score < 80).length}
            </div>
            <p className="text-xs text-muted-foreground mt-1">Score 60-79</p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Total Solar Potential</CardTitle>
            <Zap className="h-5 w-5 text-amber-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-heading text-primary">
              {prospects.reduce((sum, p) => sum + p.estimated_solar_capacity_kw, 0).toLocaleString()} kW
            </div>
            <p className="text-xs text-muted-foreground mt-1">Across all prospects</p>
          </CardContent>
        </Card>
      </div>

      {/* Prospects List */}
      {prospects.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Zap className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-primary mb-2">No prospects available</h3>
            <p className="text-sm text-muted-foreground">Add facilities to generate leads</p>
          </CardContent>
        </Card>
      ) : (
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-heading">Ranked Prospects</CardTitle>
            <CardDescription>Click on any prospect to view details or generate outreach email</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              {prospects.map((facility, index) => (
                <div
                  key={facility.id}
                  className="flex items-center gap-4 p-4 rounded-lg border border-border hover:border-accent hover:bg-muted/50 transition-all"
                  data-testid={`lead-item-${index}`}
                >
                  {/* Rank Badge */}
                  <div className="flex-shrink-0">
                    <div className={`w-12 h-12 rounded-lg flex items-center justify-center font-bold text-lg ${
                      index < 3 ? 'bg-gradient-to-br from-accent to-blue-500 text-white' :
                      'bg-muted text-muted-foreground'
                    }`}>
                      #{index + 1}
                    </div>
                  </div>

                  {/* Facility Info */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 mb-1">
                      <h3 className="font-semibold text-primary text-lg truncate">{facility.company_name}</h3>
                      {facility.existing_renewable_adoption && (
                        <Badge variant="outline" className="text-green-600 border-green-200 flex-shrink-0">
                          <Leaf className="h-3 w-3 mr-1" />
                          Has Renewable
                        </Badge>
                      )}
                    </div>
                    <p className="text-sm text-muted-foreground mb-2">{facility.industry_type}</p>
                    <div className="flex flex-wrap gap-4 text-sm">
                      <div className="flex items-center gap-1">
                        <MapPin className="h-4 w-4 text-muted-foreground" />
                        <span>{facility.city}, {facility.state}</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <Zap className="h-4 w-4 text-amber-500" />
                        <span className="font-medium">{facility.estimated_solar_capacity_kw} kW</span>
                        <span className="text-muted-foreground">solar</span>
                      </div>
                      <div className="flex items-center gap-1">
                        <TrendingUp className="h-4 w-4 text-purple-500" />
                        <span className="font-medium">{facility.estimated_power_demand_mw} MW</span>
                        <span className="text-muted-foreground">demand</span>
                      </div>
                    </div>
                  </div>

                  {/* Score and Actions */}
                  <div className="flex items-center gap-3 flex-shrink-0">
                    <div className={`px-4 py-2 rounded-md font-bold text-lg ${
                      facility.renewable_opportunity_score >= 80 ? 'bg-green-100 text-green-700' :
                      facility.renewable_opportunity_score >= 60 ? 'bg-amber-100 text-amber-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {facility.renewable_opportunity_score}
                    </div>
                    <div className="flex flex-col gap-2">
                      <Link to={`/facilities/${facility.id}`}>
                        <Button size="sm" variant="outline" data-testid={`view-details-${index}`}>
                          View Details
                        </Button>
                      </Link>
                      <Link to={`/email-generator?facility=${facility.id}`}>
                        <Button size="sm" className="gradient-accent text-white" data-testid={`generate-email-${index}`}>
                          <Mail className="mr-2 h-4 w-4" />
                          Email
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default LeadGenerator;