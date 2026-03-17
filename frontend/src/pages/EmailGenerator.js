import { useEffect, useState } from 'react';
import { useSearchParams, Link } from 'react-router-dom';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { Button } from '@/components/ui/button';
import { Textarea } from '@/components/ui/textarea';
import { Mail, Sparkles, Copy, Check, ExternalLink } from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const EmailGenerator = () => {
  const [searchParams] = useSearchParams();
  const [facilities, setFacilities] = useState([]);
  const [selectedFacility, setSelectedFacility] = useState('');
  const [emailContent, setEmailContent] = useState('');
  const [generating, setGenerating] = useState(false);
  const [copied, setCopied] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchFacilities();
  }, []);

  useEffect(() => {
    const facilityParam = searchParams.get('facility');
    if (facilityParam && facilities.length > 0) {
      setSelectedFacility(facilityParam);
      generateEmail(facilityParam);
    }
  }, [searchParams, facilities]);

  const fetchFacilities = async () => {
    try {
      const response = await axios.get(`${API}/facilities?limit=500`);
      setFacilities(response.data.sort((a, b) => b.renewable_opportunity_score - a.renewable_opportunity_score));
    } catch (error) {
      console.error('Error fetching facilities:', error);
      toast.error('Failed to load facilities');
    } finally {
      setLoading(false);
    }
  };

  const generateEmail = async (facilityId = selectedFacility) => {
    if (!facilityId) {
      toast.error('Please select a facility');
      return;
    }

    setGenerating(true);
    try {
      const response = await axios.post(`${API}/email/generate`, {
        facility_id: facilityId
      });
      setEmailContent(response.data.email_content);
      toast.success(`Email generated for ${response.data.facility_name}`);
    } catch (error) {
      console.error('Error generating email:', error);
      toast.error(error.response?.data?.detail || 'Failed to generate email');
    } finally {
      setGenerating(false);
    }
  };

  const copyToClipboard = () => {
    navigator.clipboard.writeText(emailContent);
    setCopied(true);
    toast.success('Email copied to clipboard');
    setTimeout(() => setCopied(false), 2000);
  };

  const selectedFacilityData = facilities.find(f => f.id === selectedFacility);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96" data-testid="email-generator-loading">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="email-generator">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight font-heading text-primary lg:text-5xl">
          AI Email Generator
        </h1>
        <p className="text-muted-foreground mt-2">Generate personalized renewable energy outreach emails</p>
      </div>

      {/* Facility Selection */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-heading">Select Facility</CardTitle>
          <CardDescription>Choose a facility to generate a personalized outreach email</CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <Select value={selectedFacility} onValueChange={setSelectedFacility}>
            <SelectTrigger data-testid="facility-select">
              <SelectValue placeholder="Select a facility..." />
            </SelectTrigger>
            <SelectContent>
              {facilities.map(facility => (
                <SelectItem key={facility.id} value={facility.id}>
                  {facility.company_name} - {facility.city} (Score: {facility.renewable_opportunity_score})
                </SelectItem>
              ))}
            </SelectContent>
          </Select>

          {selectedFacilityData && (
            <div className="p-4 rounded-lg bg-muted/50 border border-border">
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                  <h3 className="font-semibold text-primary mb-1">{selectedFacilityData.company_name}</h3>
                  <p className="text-sm text-muted-foreground mb-3">
                    {selectedFacilityData.industry_type} • {selectedFacilityData.city}, {selectedFacilityData.state}
                  </p>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
                    <div>
                      <p className="text-muted-foreground">Solar Potential</p>
                      <p className="font-semibold text-primary">{selectedFacilityData.estimated_solar_capacity_kw} kW</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Power Demand</p>
                      <p className="font-semibold text-primary">{selectedFacilityData.estimated_power_demand_mw} MW</p>
                    </div>
                    <div>
                      <p className="text-muted-foreground">Opportunity Score</p>
                      <p className="font-semibold text-accent">{selectedFacilityData.renewable_opportunity_score}</p>
                    </div>
                    <div>
                      <Link to={`/facilities/${selectedFacilityData.id}`}>
                        <Button variant="outline" size="sm" className="w-full">
                          <ExternalLink className="mr-2 h-4 w-4" />
                          View Details
                        </Button>
                      </Link>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          <Button
            onClick={() => generateEmail()}
            disabled={!selectedFacility || generating}
            className="w-full gradient-accent text-white"
            size="lg"
            data-testid="generate-email-button"
          >
            {generating ? (
              <>
                <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white mr-2"></div>
                Generating Email...
              </>
            ) : (
              <>
                <Sparkles className="mr-2 h-5 w-5" />
                Generate Email with AI
              </>
            )}
          </Button>
        </CardContent>
      </Card>

      {/* Generated Email */}
      {emailContent && (
        <Card>
          <CardHeader>
            <div className="flex items-center justify-between">
              <div>
                <CardTitle className="text-2xl font-heading">Generated Email</CardTitle>
                <CardDescription>AI-powered personalized outreach email</CardDescription>
              </div>
              <Button
                onClick={copyToClipboard}
                variant="outline"
                size="sm"
                data-testid="copy-email-button"
              >
                {copied ? (
                  <>
                    <Check className="mr-2 h-4 w-4" />
                    Copied!
                  </>
                ) : (
                  <>
                    <Copy className="mr-2 h-4 w-4" />
                    Copy Email
                  </>
                )}
              </Button>
            </div>
          </CardHeader>
          <CardContent>
            <Textarea
              value={emailContent}
              onChange={(e) => setEmailContent(e.target.value)}
              className="min-h-[400px] font-body text-base"
              placeholder="Generated email will appear here..."
              data-testid="email-content-textarea"
            />
            <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <div className="flex items-start gap-2">
                <Mail className="h-5 w-5 text-blue-600 mt-0.5" />
                <div className="flex-1">
                  <p className="text-sm font-medium text-blue-900">Pro Tip</p>
                  <p className="text-sm text-blue-700 mt-1">
                    You can edit the generated email above before copying. The AI has already personalized it with
                    facility-specific data including power demand, solar potential, cost savings, and carbon reduction.
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* How it Works */}
      {!emailContent && (
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-heading">How It Works</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent text-white flex items-center justify-center font-bold">
                  1
                </div>
                <div>
                  <h4 className="font-semibold text-primary mb-1">Select a Facility</h4>
                  <p className="text-sm text-muted-foreground">
                    Choose from our database of industrial facilities with renewable potential
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent text-white flex items-center justify-center font-bold">
                  2
                </div>
                <div>
                  <h4 className="font-semibold text-primary mb-1">AI Analyzes Data</h4>
                  <p className="text-sm text-muted-foreground">
                    Our AI analyzes power demand, solar potential, cost savings, and carbon reduction
                  </p>
                </div>
              </div>
              <div className="flex gap-4">
                <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent text-white flex items-center justify-center font-bold">
                  3
                </div>
                <div>
                  <h4 className="font-semibold text-primary mb-1">Personalized Email Generated</h4>
                  <p className="text-sm text-muted-foreground">
                    Get a compelling, data-driven outreach email ready to send to the facility
                  </p>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default EmailGenerator;
