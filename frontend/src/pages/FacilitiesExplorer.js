import { useEffect, useState } from 'react';
import axios from 'axios';
import { Link } from 'react-router-dom';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Search, Filter, Building2, Zap, MapPin, Leaf, X } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const FacilitiesExplorer = () => {
  const [facilities, setFacilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [cityFilter, setCityFilter] = useState('all');
  const [industryFilter, setIndustryFilter] = useState('all');
  const [scoreFilter, setScoreFilter] = useState('all');
  const [cities, setCities] = useState([]);
  const [industries, setIndustries] = useState([]);

  useEffect(() => {
    fetchFacilities();
  }, [cityFilter, industryFilter, scoreFilter]);

  const fetchFacilities = async () => {
    try {
      let url = `${API}/facilities?limit=500`;
      
      if (cityFilter !== 'all') url += `&city=${encodeURIComponent(cityFilter)}`;
      if (industryFilter !== 'all') url += `&industry_type=${encodeURIComponent(industryFilter)}`;
      if (scoreFilter === 'high') url += '&min_score=80';
      if (scoreFilter === 'medium') url += '&min_score=60&max_score=79';
      if (scoreFilter === 'low') url += '&max_score=59';

      const response = await axios.get(url);
      const data = response.data;
      setFacilities(data);

      // Extract unique values for filters
      const allFacilities = await axios.get(`${API}/facilities?limit=500`);
      const uniqueCities = [...new Set(allFacilities.data.map(f => f.city))].sort();
      const uniqueIndustries = [...new Set(allFacilities.data.map(f => f.industry_type))].sort();
      setCities(uniqueCities);
      setIndustries(uniqueIndustries);
    } catch (error) {
      console.error('Error fetching facilities:', error);
      toast.error('Failed to load facilities');
    } finally {
      setLoading(false);
    }
  };

  const filteredFacilities = searchTerm
    ? facilities.filter(f =>
        f.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        f.city.toLowerCase().includes(searchTerm.toLowerCase()) ||
        f.industrial_cluster.toLowerCase().includes(searchTerm.toLowerCase())
      )
    : facilities;

  const clearFilters = () => {
    setSearchTerm('');
    setCityFilter('all');
    setIndustryFilter('all');
    setScoreFilter('all');
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96" data-testid="facilities-loading">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="facilities-explorer">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight font-heading text-primary lg:text-5xl">
          Facilities Explorer
        </h1>
        <p className="text-muted-foreground mt-2">Search and filter industrial facilities</p>
      </div>

      {/* Search and Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="space-y-4">
            <div className="relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search by company name, city, or cluster..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
                data-testid="facilities-search-input"
              />
            </div>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              <Select value={cityFilter} onValueChange={setCityFilter}>
                <SelectTrigger data-testid="facilities-city-filter">
                  <SelectValue placeholder="Filter by city" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Cities</SelectItem>
                  {cities.map(city => (
                    <SelectItem key={city} value={city}>{city}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={industryFilter} onValueChange={setIndustryFilter}>
                <SelectTrigger data-testid="facilities-industry-filter">
                  <SelectValue placeholder="Filter by industry" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Industries</SelectItem>
                  {industries.map(industry => (
                    <SelectItem key={industry} value={industry}>{industry}</SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Select value={scoreFilter} onValueChange={setScoreFilter}>
                <SelectTrigger data-testid="facilities-score-filter">
                  <SelectValue placeholder="Filter by score" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="all">All Scores</SelectItem>
                  <SelectItem value="high">High (80+)</SelectItem>
                  <SelectItem value="medium">Medium (60-79)</SelectItem>
                  <SelectItem value="low">Low (0-59)</SelectItem>
                </SelectContent>
              </Select>
            </div>
            {(searchTerm || cityFilter !== 'all' || industryFilter !== 'all' || scoreFilter !== 'all') && (
              <div className="flex items-center justify-between">
                <span className="text-sm text-muted-foreground">
                  Showing {filteredFacilities.length} facilities
                </span>
                <Button variant="outline" size="sm" onClick={clearFilters} data-testid="clear-all-filters">
                  <X className="mr-2 h-4 w-4" />
                  Clear Filters
                </Button>
              </div>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Facilities Grid */}
      {filteredFacilities.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Building2 className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-primary mb-2">No facilities found</h3>
            <p className="text-sm text-muted-foreground">Try adjusting your filters</p>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredFacilities.map((facility, index) => (
            <Link key={facility.id} to={`/facilities/${facility.id}`} data-testid={`facility-card-${index}`}>
              <Card className="facility-card h-full hover:border-accent">
                <CardHeader>
                  <div className="flex items-start justify-between gap-2">
                    <div className="flex-1">
                      <CardTitle className="text-lg font-heading line-clamp-1">
                        {facility.company_name}
                      </CardTitle>
                      <CardDescription className="mt-1">
                        {facility.industry_type}
                      </CardDescription>
                    </div>
                    <div className={`px-3 py-1 rounded-md font-bold text-sm score-badge ${
                      facility.renewable_opportunity_score >= 80 ? 'bg-green-100 text-green-700' :
                      facility.renewable_opportunity_score >= 60 ? 'bg-amber-100 text-amber-700' :
                      'bg-blue-100 text-blue-700'
                    }`}>
                      {facility.renewable_opportunity_score}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="space-y-3">
                    <div className="flex items-center gap-2 text-sm text-muted-foreground">
                      <MapPin className="h-4 w-4" />
                      <span>{facility.city}, {facility.state}</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Zap className="h-4 w-4 text-amber-500" />
                      <span className="font-medium">{facility.estimated_solar_capacity_kw} kW</span>
                      <span className="text-muted-foreground">solar potential</span>
                    </div>
                    <div className="flex items-center gap-2 text-sm">
                      <Building2 className="h-4 w-4 text-purple-500" />
                      <span className="font-medium">{facility.estimated_power_demand_mw} MW</span>
                      <span className="text-muted-foreground">power demand</span>
                    </div>
                    <div className="pt-2 border-t border-border">
                      <Badge variant="secondary" className="text-xs">
                        {facility.industrial_cluster}
                      </Badge>
                      {facility.existing_renewable_adoption && (
                        <Badge variant="outline" className="ml-2 text-xs text-green-600 border-green-200">
                          <Leaf className="h-3 w-3 mr-1" />
                          Has Renewable
                        </Badge>
                      )}
                    </div>
                  </div>
                </CardContent>
              </Card>
            </Link>
          ))}
        </div>
      )}
    </div>
  );
};

export default FacilitiesExplorer;