import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Building2, MapPin, Zap, TrendingUp, Leaf, Mail, ArrowLeft, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FacilityDetail = () => {
  const { id } = useParams();
  const [facility, setFacility] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFacility();
  }, [id]);

  const fetchFacility = async () => {
    try {
      const response = await axios.get(`${API}/facilities/${id}`);
      setFacility(response.data);
    } catch (error) {
      console.error('Error fetching facility:', error);
      toast.error('Failed to load facility details');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96" data-testid="facility-loading">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
      </div>
    );
  }

  if (!facility) {
    return (
      <div className="text-center py-12">
        <h2 className="text-2xl font-bold text-primary">Facility not found</h2>
        <Link to="/facilities">
          <Button className="mt-4">Back to Facilities</Button>
        </Link>
      </div>
    );
  }

  // Calculate potential savings
  const annualGenerationKwh = facility.estimated_solar_capacity_kw * 1400;
  const annualSavings = annualGenerationKwh * 6;
  const carbonReductionTons = (annualGenerationKwh * 0.82) / 1000;

  return (
    <div className="space-y-6" data-testid="facility-detail">
      {/* Header */}
      <div>
        <Link to="/facilities">
          <Button variant="ghost" size="sm" className="mb-4" data-testid="back-to-facilities">
            <ArrowLeft className="mr-2 h-4 w-4" />
            Back to Facilities
          </Button>
        </Link>
        <div className="flex items-start justify-between gap-4">
          <div>
            <h1 className="text-4xl font-bold tracking-tight font-heading text-primary lg:text-5xl">
              {facility.company_name}
            </h1>
            <p className="text-muted-foreground mt-2">{facility.industry_type}</p>
          </div>
          <div className={`px-6 py-3 rounded-lg font-bold text-2xl ${
            facility.renewable_opportunity_score >= 80 ? 'bg-green-100 text-green-700' :
            facility.renewable_opportunity_score >= 60 ? 'bg-amber-100 text-amber-700' :
            'bg-blue-100 text-blue-700'
          }`}>
            {facility.renewable_opportunity_score}
            <div className="text-xs font-normal">Opportunity Score</div>
          </div>
        </div>
      </div>

      {/* Quick Actions */}
      <div className="flex gap-4">
        <Link to={`/email-generator?facility=${facility.id}`}>
          <Button className="gradient-accent text-white" data-testid="generate-email-button">
            <Mail className="mr-2 h-4 w-4" />
            Generate Outreach Email
          </Button>
        </Link>
        {facility.website && (
          <a href={facility.website} target="_blank" rel="noopener noreferrer">
            <Button variant="outline">
              <ExternalLink className="mr-2 h-4 w-4" />
              Visit Website
            </Button>
          </a>
        )}
      </div>

      {/* Main Info Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Solar Potential</CardTitle>
            <Zap className="h-5 w-5 text-amber-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-heading text-primary">
              {facility.estimated_solar_capacity_kw} kW
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Rooftop: {facility.rooftop_area_sqft.toLocaleString()} sq ft
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Power Demand</CardTitle>
            <TrendingUp className="h-5 w-5 text-purple-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-heading text-primary">
              {facility.estimated_power_demand_mw} MW
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Industry avg for {facility.industry_type}
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Annual Savings</CardTitle>
            <TrendingUp className="h-5 w-5 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-heading text-primary">
              ₹{(annualSavings / 100000).toFixed(1)}L
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Estimated at ₹6/kWh
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Carbon Reduction</CardTitle>
            <Leaf className="h-5 w-5 text-green-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-heading text-primary">
              {carbonReductionTons.toFixed(1)} tons
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              CO₂ per year
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="text-2xl font-heading">Facility Information</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div>
                <p className="text-sm font-medium text-muted-foreground">Location</p>
                <div className="flex items-center gap-2 mt-1">
                  <MapPin className="h-4 w-4 text-accent" />
                  <p className="text-primary font-medium">{facility.city}, {facility.state}</p>
                </div>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Industrial Cluster</p>
                <p className="text-primary font-medium mt-1">{facility.industrial_cluster}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Industry Type</p>
                <p className="text-primary font-medium mt-1">{facility.industry_type}</p>
              </div>
              <div>
                <p className="text-sm font-medium text-muted-foreground">Renewable Adoption</p>
                <div className="mt-1">
                  {facility.existing_renewable_adoption ? (
                    <Badge variant="outline" className="text-green-600 border-green-200">
                      <Leaf className="h-3 w-3 mr-1" />
                      Active
                    </Badge>
                  ) : (
                    <Badge variant="outline">Not Yet</Badge>
                  )}
                </div>
              </div>
            </div>

            {(facility.contact_email || facility.website) && (
              <div className="pt-4 border-t border-border">
                <p className="text-sm font-medium text-muted-foreground mb-2">Contact Information</p>
                <div className="space-y-2">
                  {facility.contact_email && (
                    <p className="text-sm text-primary">
                      <span className="font-medium">Email:</span> {facility.contact_email}
                    </p>
                  )}
                  {facility.website && (
                    <p className="text-sm text-primary">
                      <span className="font-medium">Website:</span>{' '}
                      <a href={facility.website} target="_blank" rel="noopener noreferrer" className="text-accent hover:underline">
                        {facility.website}
                      </a>
                    </p>
                  )}
                </div>
              </div>
            )}

            <div className="pt-4 border-t border-border">
              <p className="text-sm font-medium text-muted-foreground mb-2">Data Source</p>
              <p className="text-sm text-primary">{facility.data_source}</p>
              <p className="text-xs text-muted-foreground mt-1">
                Added: {new Date(facility.date_added).toLocaleDateString()}
              </p>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle className="text-xl font-heading">Solar Potential Analysis</CardTitle>
          </CardHeader>
          <CardContent className="space-y-4">
            <div>
              <p className="text-sm font-medium text-muted-foreground">Annual Generation</p>
              <p className="text-2xl font-bold text-primary mt-1">
                {annualGenerationKwh.toLocaleString()} kWh
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Cost Savings (Annual)</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                ₹{annualSavings.toLocaleString()}
              </p>
            </div>
            <div>
              <p className="text-sm font-medium text-muted-foreground">Carbon Offset (Annual)</p>
              <p className="text-2xl font-bold text-green-600 mt-1">
                {carbonReductionTons.toFixed(1)} tons CO₂
              </p>
            </div>
            <div className="pt-4 border-t border-border">
              <p className="text-xs text-muted-foreground">
                Calculations based on 1,400 equivalent sun hours/year and ₹6/kWh industrial electricity rate.
              </p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
};

export default FacilityDetail;