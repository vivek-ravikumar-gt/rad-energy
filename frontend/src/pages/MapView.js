import { useEffect, useState } from 'react';
import axios from 'axios';
import { MapContainer, TileLayer, Marker, Popup } from 'react-leaflet';
import L from 'leaflet';
import { Card, CardContent } from '@/components/ui/card';
import { Input } from '@/components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Search, X } from 'lucide-react';
import { toast } from 'sonner';
import { Link } from 'react-router-dom';
import 'leaflet/dist/leaflet.css';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

// Fix Leaflet default icon issue
delete L.Icon.Default.prototype._getIconUrl;
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.7.1/images/marker-shadow.png',
});

// Custom marker icons based on score
const createCustomIcon = (score) => {
  const color = score >= 80 ? '#10B981' : score >= 60 ? '#F59E0B' : '#3B82F6';
  return L.divIcon({
    className: 'custom-marker',
    html: `<div style="background-color: ${color}; width: 24px; height: 24px; border-radius: 50%; border: 3px solid white; box-shadow: 0 2px 5px rgba(0,0,0,0.3);"></div>`,
    iconSize: [24, 24],
    iconAnchor: [12, 12],
  });
};

const MapView = () => {
  const [facilities, setFacilities] = useState([]);
  const [filteredFacilities, setFilteredFacilities] = useState([]);
  const [loading, setLoading] = useState(true);
  const [searchTerm, setSearchTerm] = useState('');
  const [cityFilter, setCityFilter] = useState('all');
  const [industryFilter, setIndustryFilter] = useState('all');
  const [cities, setCities] = useState([]);
  const [industries, setIndustries] = useState([]);

  useEffect(() => {
    fetchFacilities();
  }, []);

  useEffect(() => {
    filterFacilities();
  }, [facilities, searchTerm, cityFilter, industryFilter]);

  const fetchFacilities = async () => {
    try {
      const response = await axios.get(`${API}/facilities?limit=500`);
      const data = response.data;
      setFacilities(data);

      // Extract unique cities and industries
      const uniqueCities = [...new Set(data.map(f => f.city))].sort();
      const uniqueIndustries = [...new Set(data.map(f => f.industry_type))].sort();
      setCities(uniqueCities);
      setIndustries(uniqueIndustries);
    } catch (error) {
      console.error('Error fetching facilities:', error);
      toast.error('Failed to load facilities');
    } finally {
      setLoading(false);
    }
  };

  const filterFacilities = () => {
    let filtered = facilities;

    if (searchTerm) {
      filtered = filtered.filter(f =>
        f.company_name.toLowerCase().includes(searchTerm.toLowerCase()) ||
        f.city.toLowerCase().includes(searchTerm.toLowerCase())
      );
    }

    if (cityFilter !== 'all') {
      filtered = filtered.filter(f => f.city === cityFilter);
    }

    if (industryFilter !== 'all') {
      filtered = filtered.filter(f => f.industry_type === industryFilter);
    }

    setFilteredFacilities(filtered);
  };

  const clearFilters = () => {
    setSearchTerm('');
    setCityFilter('all');
    setIndustryFilter('all');
  };

  // Calculate center position
  const center = filteredFacilities.length > 0 && filteredFacilities[0].latitude
    ? [filteredFacilities[0].latitude, filteredFacilities[0].longitude]
    : [12.9716, 77.5946]; // Default to Bangalore

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96" data-testid="map-loading">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="map-view">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight font-heading text-primary lg:text-5xl">
          Geographic Map
        </h1>
        <p className="text-muted-foreground mt-2">Interactive map of industrial facilities</p>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
            <div className="md:col-span-2 relative">
              <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 h-4 w-4 text-muted-foreground" />
              <Input
                placeholder="Search facilities or cities..."
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
                className="pl-10"
                data-testid="map-search-input"
              />
            </div>
            <Select value={cityFilter} onValueChange={setCityFilter}>
              <SelectTrigger data-testid="map-city-filter">
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
              <SelectTrigger data-testid="map-industry-filter">
                <SelectValue placeholder="Filter by industry" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Industries</SelectItem>
                {industries.map(industry => (
                  <SelectItem key={industry} value={industry}>{industry}</SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
          {(searchTerm || cityFilter !== 'all' || industryFilter !== 'all') && (
            <div className="mt-4">
              <Button variant="outline" size="sm" onClick={clearFilters} data-testid="clear-filters">
                <X className="mr-2 h-4 w-4" />
                Clear Filters
              </Button>
              <span className="ml-4 text-sm text-muted-foreground">
                Showing {filteredFacilities.length} of {facilities.length} facilities
              </span>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Map */}
      <Card>
        <CardContent className="p-0">
          <div className="h-[600px] w-full rounded-xl overflow-hidden" data-testid="leaflet-map">
            <MapContainer
              center={center}
              zoom={7}
              style={{ height: '100%', width: '100%' }}
              scrollWheelZoom={true}
            >
              <TileLayer
                attribution='&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a>'
                url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
              />
              {filteredFacilities
                .filter(facility => facility.latitude && facility.longitude)
                .map((facility) => (
                  <Marker
                    key={facility.id}
                    position={[facility.latitude, facility.longitude]}
                    icon={createCustomIcon(facility.renewable_opportunity_score)}
                  >
                    <Popup>
                      <div className="p-2 min-w-[200px]">
                        <h3 className="font-bold text-primary mb-1">{facility.company_name}</h3>
                        <p className="text-sm text-muted-foreground mb-2">{facility.industry_type}</p>
                        <div className="space-y-1 text-xs">
                          <p><span className="font-medium">Location:</span> {facility.city}, {facility.state}</p>
                          <p><span className="font-medium">Power Demand:</span> {facility.estimated_power_demand_mw} MW</p>
                          <p><span className="font-medium">Solar Potential:</span> {facility.estimated_solar_capacity_kw} kW</p>
                          <p>
                            <span className="font-medium">Opportunity Score:</span>
                            <span className={`ml-1 font-bold ${
                              facility.renewable_opportunity_score >= 80 ? 'text-green-600' :
                              facility.renewable_opportunity_score >= 60 ? 'text-amber-600' :
                              'text-blue-600'
                            }`}>
                              {facility.renewable_opportunity_score}
                            </span>
                          </p>
                        </div>
                        <Link to={`/facilities/${facility.id}`}>
                          <Button size="sm" className="w-full mt-3" variant="outline">
                            View Details
                          </Button>
                        </Link>
                      </div>
                    </Popup>
                  </Marker>
                ))}
            </MapContainer>
          </div>
        </CardContent>
      </Card>

      {/* Legend */}
      <Card>
        <CardContent className="pt-6">
          <h3 className="font-semibold text-primary mb-3">Map Legend</h3>
          <div className="flex flex-wrap gap-6">
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-green-500 border-2 border-white shadow"></div>
              <span className="text-sm">High Opportunity (80+)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-amber-500 border-2 border-white shadow"></div>
              <span className="text-sm">Medium Opportunity (60-79)</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-6 h-6 rounded-full bg-blue-500 border-2 border-white shadow"></div>
              <span className="text-sm">Standard Opportunity (0-59)</span>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default MapView;