import { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
import { Switch } from '@/components/ui/switch';
import { Badge } from '@/components/ui/badge';
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from '@/components/ui/dialog';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import {
  Plus,
  Edit,
  Trash2,
  TestTube,
  Database,
  CheckCircle2,
  XCircle,
  AlertCircle
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const SourceManagement = () => {
  const [sources, setSources] = useState([]);
  const [loading, setLoading] = useState(true);
  const [editingSource, setEditingSource] = useState(null);
  const [isDialogOpen, setIsDialogOpen] = useState(false);
  const [testing, setTesting] = useState(null);

  const emptySource = {
    name: '',
    type: 'company_directory',
    url: '',
    selectors: {
      container: '',
      name: '',
      industry: '',
      location: ''
    },
    enabled: false,
    notes: ''
  };

  useEffect(() => {
    fetchSources();
  }, []);

  const fetchSources = async () => {
    try {
      const response = await axios.get(`${API}/discovery/sources`);
      setSources(response.data.sources || []);
    } catch (error) {
      console.error('Error fetching sources:', error);
      toast.error('Failed to load sources');
    } finally {
      setLoading(false);
    }
  };

  const seedProductionSources = async () => {
    try {
      const response = await axios.post(`${API}/discovery/sources/seed-production`);
      toast.success(response.data.message);
      fetchSources();
    } catch (error) {
      console.error('Error seeding sources:', error);
      toast.error(error.response?.data?.detail || 'Failed to seed sources');
    }
  };

  const saveSource = async () => {
    try {
      if (editingSource._id) {
        // Update existing
        await axios.put(`${API}/discovery/sources/${editingSource.name}`, editingSource);
        toast.success('Source updated successfully');
      } else {
        // Create new
        await axios.post(`${API}/discovery/sources`, editingSource);
        toast.success('Source created successfully');
      }
      setIsDialogOpen(false);
      setEditingSource(null);
      fetchSources();
    } catch (error) {
      console.error('Error saving source:', error);
      toast.error(error.response?.data?.detail || 'Failed to save source');
    }
  };

  const deleteSource = async (sourceName) => {
    if (!confirm(`Are you sure you want to delete "${sourceName}"?`)) return;

    try {
      await axios.delete(`${API}/discovery/sources/${sourceName}`);
      toast.success('Source deleted successfully');
      fetchSources();
    } catch (error) {
      console.error('Error deleting source:', error);
      toast.error('Failed to delete source');
    }
  };

  const testSource = async (sourceName) => {
    setTesting(sourceName);
    try {
      const response = await axios.post(`${API}/discovery/sources/${sourceName}/test`);
      toast.success(`Found ${response.data.facilities_found} facilities`);
    } catch (error) {
      console.error('Error testing source:', error);
      toast.error(error.response?.data?.detail || 'Failed to test source');
    } finally {
      setTesting(null);
    }
  };

  const toggleSource = async (sourceName, enabled) => {
    try {
      await axios.put(`${API}/discovery/sources/${sourceName}`, { enabled });
      toast.success(`Source ${enabled ? 'enabled' : 'disabled'}`);
      fetchSources();
    } catch (error) {
      console.error('Error toggling source:', error);
      toast.error('Failed to update source');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
      </div>
    );
  }

  return (
    <div className="space-y-6" data-testid="source-management">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold tracking-tight font-heading text-primary lg:text-5xl">
            Source Management
          </h1>
          <p className="text-muted-foreground mt-2">
            Configure and manage discovery data sources
          </p>
        </div>
        <div className="flex gap-2">
          {sources.length === 0 && (
            <Button onClick={seedProductionSources} variant="outline">
              <Database className="mr-2 h-4 w-4" />
              Load Production Sources
            </Button>
          )}
          <Dialog open={isDialogOpen} onOpenChange={setIsDialogOpen}>
            <DialogTrigger asChild>
              <Button
                onClick={() => {
                  setEditingSource(emptySource);
                  setIsDialogOpen(true);
                }}
                className="gradient-accent text-white"
              >
                <Plus className="mr-2 h-4 w-4" />
                Add Source
              </Button>
            </DialogTrigger>
            <DialogContent className="max-w-2xl max-h-[80vh] overflow-y-auto">
              <DialogHeader>
                <DialogTitle>
                  {editingSource?._id ? 'Edit Source' : 'Add New Source'}
                </DialogTitle>
                <DialogDescription>
                  Configure a new data source for facility discovery
                </DialogDescription>
              </DialogHeader>

              {editingSource && (
                <div className="space-y-4 py-4">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="col-span-2">
                      <Label htmlFor="name">Source Name</Label>
                      <Input
                        id="name"
                        value={editingSource.name}
                        onChange={(e) => setEditingSource({...editingSource, name: e.target.value})}
                        placeholder="e.g., IndiaMART - Textiles"
                      />
                    </div>

                    <div>
                      <Label htmlFor="type">Source Type</Label>
                      <Select
                        value={editingSource.type}
                        onValueChange={(value) => setEditingSource({...editingSource, type: value})}
                      >
                        <SelectTrigger>
                          <SelectValue />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="company_directory">Company Directory</SelectItem>
                          <SelectItem value="estate_listing">Estate Listing</SelectItem>
                          <SelectItem value="cluster_directory">Cluster Directory</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="flex items-center space-x-2">
                      <Label htmlFor="enabled">Enabled</Label>
                      <Switch
                        id="enabled"
                        checked={editingSource.enabled}
                        onCheckedChange={(checked) => setEditingSource({...editingSource, enabled: checked})}
                      />
                    </div>

                    <div className="col-span-2">
                      <Label htmlFor="url">URL</Label>
                      <Input
                        id="url"
                        value={editingSource.url}
                        onChange={(e) => setEditingSource({...editingSource, url: e.target.value})}
                        placeholder="https://example.com/companies"
                      />
                    </div>
                  </div>

                  <div>
                    <Label className="text-base font-semibold">CSS Selectors</Label>
                    <div className="grid grid-cols-2 gap-4 mt-2">
                      <div>
                        <Label htmlFor="container">Container</Label>
                        <Input
                          id="container"
                          value={editingSource.selectors.container}
                          onChange={(e) => setEditingSource({
                            ...editingSource,
                            selectors: {...editingSource.selectors, container: e.target.value}
                          })}
                          placeholder="div.listing-card"
                        />
                      </div>
                      <div>
                        <Label htmlFor="name-selector">Name</Label>
                        <Input
                          id="name-selector"
                          value={editingSource.selectors.name}
                          onChange={(e) => setEditingSource({
                            ...editingSource,
                            selectors: {...editingSource.selectors, name: e.target.value}
                          })}
                          placeholder=".company-name"
                        />
                      </div>
                      <div>
                        <Label htmlFor="industry">Industry</Label>
                        <Input
                          id="industry"
                          value={editingSource.selectors.industry}
                          onChange={(e) => setEditingSource({
                            ...editingSource,
                            selectors: {...editingSource.selectors, industry: e.target.value}
                          })}
                          placeholder=".industry"
                        />
                      </div>
                      <div>
                        <Label htmlFor="location">Location</Label>
                        <Input
                          id="location"
                          value={editingSource.selectors.location}
                          onChange={(e) => setEditingSource({
                            ...editingSource,
                            selectors: {...editingSource.selectors, location: e.target.value}
                          })}
                          placeholder=".location"
                        />
                      </div>
                    </div>
                  </div>

                  <div>
                    <Label htmlFor="notes">Notes</Label>
                    <Input
                      id="notes"
                      value={editingSource.notes}
                      onChange={(e) => setEditingSource({...editingSource, notes: e.target.value})}
                      placeholder="Additional notes or instructions"
                    />
                  </div>
                </div>
              )}

              <DialogFooter>
                <Button variant="outline" onClick={() => setIsDialogOpen(false)}>
                  Cancel
                </Button>
                <Button onClick={saveSource} className="gradient-accent text-white">
                  Save Source
                </Button>
              </DialogFooter>
            </DialogContent>
          </Dialog>
        </div>
      </div>

      {/* Sources List */}
      {sources.length === 0 ? (
        <Card>
          <CardContent className="py-12 text-center">
            <Database className="h-12 w-12 text-muted-foreground mx-auto mb-4" />
            <h3 className="text-lg font-semibold text-primary mb-2">No sources configured</h3>
            <p className="text-sm text-muted-foreground mb-4">
              Add data sources to enable real facility discovery
            </p>
            <Button onClick={seedProductionSources}>
              Load Production Source Templates
            </Button>
          </CardContent>
        </Card>
      ) : (
        <div className="grid grid-cols-1 gap-4">
          {sources.map((source, index) => (
            <Card key={index} className={!source.enabled ? 'opacity-60' : ''}>
              <CardHeader>
                <div className="flex items-start justify-between">
                  <div className="flex-1">
                    <div className="flex items-center gap-3">
                      <CardTitle className="text-xl font-heading">{source.name}</CardTitle>
                      {source.enabled ? (
                        <Badge className="bg-green-100 text-green-700">Enabled</Badge>
                      ) : (
                        <Badge variant="outline">Disabled</Badge>
                      )}
                      <Badge variant="secondary" className="capitalize">
                        {source.type.replace('_', ' ')}
                      </Badge>
                    </div>
                    <CardDescription className="mt-2">{source.url}</CardDescription>
                    {source.notes && (
                      <p className="text-xs text-muted-foreground mt-2">{source.notes}</p>
                    )}
                  </div>
                  <div className="flex gap-2">
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => testSource(source.name)}
                      disabled={testing === source.name}
                      title="Test source"
                    >
                      {testing === source.name ? (
                        <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-primary"></div>
                      ) : (
                        <TestTube className="h-4 w-4" />
                      )}
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => {
                        setEditingSource(source);
                        setIsDialogOpen(true);
                      }}
                      title="Edit source"
                    >
                      <Edit className="h-4 w-4" />
                    </Button>
                    <Button
                      variant="ghost"
                      size="icon"
                      onClick={() => deleteSource(source.name)}
                      title="Delete source"
                    >
                      <Trash2 className="h-4 w-4 text-red-600" />
                    </Button>
                    <Switch
                      checked={source.enabled}
                      onCheckedChange={(checked) => toggleSource(source.name, checked)}
                    />
                  </div>
                </div>
              </CardHeader>
              <CardContent>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
                  <div>
                    <p className="text-muted-foreground">Container</p>
                    <code className="text-xs bg-muted px-2 py-1 rounded">
                      {source.selectors.container}
                    </code>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Name</p>
                    <code className="text-xs bg-muted px-2 py-1 rounded">
                      {source.selectors.name}
                    </code>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Industry</p>
                    <code className="text-xs bg-muted px-2 py-1 rounded">
                      {source.selectors.industry}
                    </code>
                  </div>
                  <div>
                    <p className="text-muted-foreground">Location</p>
                    <code className="text-xs bg-muted px-2 py-1 rounded">
                      {source.selectors.location}
                    </code>
                  </div>
                </div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      {/* Info Card */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg font-heading flex items-center gap-2">
            <AlertCircle className="h-5 w-5 text-amber-600" />
            Important Information
          </CardTitle>
        </CardHeader>
        <CardContent className="space-y-4 text-sm">
          <div>
            <h4 className="font-semibold text-primary mb-2">Before enabling sources:</h4>
            <ul className="list-disc list-inside space-y-1 text-muted-foreground">
              <li>Test CSS selectors on live pages using browser DevTools</li>
              <li>Review website Terms of Service and robots.txt</li>
              <li>Implement appropriate rate limiting</li>
              <li>Monitor for errors and adjust selectors as needed</li>
              <li>Consider requesting official API access when available</li>
            </ul>
          </div>
          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-900">
              <strong>Note:</strong> Production sources require testing and validation before use.
              Start with demo mode to verify the pipeline, then gradually enable real sources.
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
};

export default SourceManagement;
