import { useEffect, useState } from 'react';
import axios from 'axios';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select';
import { 
  Play, 
  StopCircle, 
  RefreshCw, 
  Database, 
  Calendar,
  CheckCircle2,
  XCircle,
  Clock,
  Search,
  Trash2
} from 'lucide-react';
import { toast } from 'sonner';

const BACKEND_URL = process.env.REACT_APP_BACKEND_URL;
const API = `${BACKEND_URL}/api`;

const DiscoveryDashboard = () => {
  const [status, setStatus] = useState(null);
  const [logs, setLogs] = useState([]);
  const [sources, setSources] = useState([]);
  const [sourceHealth, setSourceHealth] = useState([]);
  const [overallHealth, setOverallHealth] = useState(null);
  const [cleanupPreview, setCleanupPreview] = useState(null);
  const [loading, setLoading] = useState(true);
  const [running, setRunning] = useState(false);
  const [cleaning, setCleaning] = useState(false);

  useEffect(() => {
    fetchDiscoveryData();
  }, []);

  const fetchDiscoveryData = async () => {
    try {
      const [statusRes, logsRes, sourcesRes, healthRes, overallHealthRes] = await Promise.all([
        axios.get(`${API}/discovery/status`),
        axios.get(`${API}/discovery/logs?limit=10`),
        axios.get(`${API}/discovery/sources`),
        axios.get(`${API}/discovery/health/sources?days=7`),
        axios.get(`${API}/discovery/health/overall`)
      ]);

      setStatus(statusRes.data);
      setLogs(logsRes.data);
      setSources(sourcesRes.data.sources || []);
      setSourceHealth(healthRes.data.sources || []);
      setOverallHealth(overallHealthRes.data);
    } catch (error) {
      console.error('Error fetching discovery data:', error);
      toast.error('Failed to load discovery data');
    } finally {
      setLoading(false);
    }
  };

  const runDiscovery = async () => {
    setRunning(true);
    try {
      const response = await axios.post(`${API}/discovery/run`);
      toast.success(response.data.message);
      
      // Refresh data after a delay
      setTimeout(() => {
        fetchDiscoveryData();
        setRunning(false);
      }, 5000);
    } catch (error) {
      console.error('Error running discovery:', error);
      toast.error(error.response?.data?.detail || 'Failed to start discovery');
      setRunning(false);
    }
  };

  const previewCleanup = async () => {
    try {
      const response = await axios.get(`${API}/cleanup/preview`);
      setCleanupPreview(response.data);
    } catch (error) {
      console.error('Error previewing cleanup:', error);
      toast.error('Failed to preview cleanup');
    }
  };

  const executeCleanup = async () => {
    if (!confirm(`This will remove ${cleanupPreview?.would_remove || 0} entries. Continue?`)) {
      return;
    }

    setCleaning(true);
    try {
      const response = await axios.post(`${API}/cleanup/execute`);
      toast.success(`Cleanup complete: ${response.data.total_removed} entries removed`);
      setCleanupPreview(null);
      fetchDiscoveryData();
    } catch (error) {
      console.error('Error executing cleanup:', error);
      toast.error('Failed to execute cleanup');
    } finally {
      setCleaning(false);
    }
  };

  const startScheduler = async (schedule) => {
    try {
      await axios.post(`${API}/discovery/scheduler/start?schedule=${schedule}`);
      toast.success(`Scheduler started with ${schedule} schedule`);
      fetchDiscoveryData();
    } catch (error) {
      console.error('Error starting scheduler:', error);
      toast.error('Failed to start scheduler');
    }
  };

  const stopScheduler = async () => {
    try {
      await axios.post(`${API}/discovery/scheduler/stop`);
      toast.success('Scheduler stopped');
      fetchDiscoveryData();
    } catch (error) {
      console.error('Error stopping scheduler:', error);
      toast.error('Failed to stop scheduler');
    }
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96" data-testid="discovery-loading">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-accent"></div>
      </div>
    );
  }

  const lastRun = status?.last_run;

  return (
    <div className="space-y-6" data-testid="discovery-dashboard">
      {/* Header */}
      <div>
        <h1 className="text-4xl font-bold tracking-tight font-heading text-primary lg:text-5xl">
          Automated Discovery
        </h1>
        <p className="text-muted-foreground mt-2">
          Automated facility discovery pipeline with web crawlers
        </p>
      </div>

      {/* Status Overview */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Scheduler Status
            </CardTitle>
            <Calendar className="h-5 w-5 text-accent" />
          </CardHeader>
          <CardContent>
            <div className="flex items-center gap-2">
              {status?.scheduler_running ? (
                <Badge className="bg-green-100 text-green-700">Running</Badge>
              ) : (
                <Badge variant="outline">Stopped</Badge>
              )}
            </div>
            {status?.next_run && (
              <p className="text-xs text-muted-foreground mt-2">
                Next run: {new Date(status.next_run).toLocaleString()}
              </p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Last Discovery
            </CardTitle>
            <Clock className="h-5 w-5 text-blue-600" />
          </CardHeader>
          <CardContent>
            {lastRun ? (
              <>
                <div className="text-2xl font-bold font-heading text-primary">
                  {lastRun.facilities_inserted}
                </div>
                <p className="text-xs text-muted-foreground mt-1">
                  {new Date(lastRun.start_time).toLocaleDateString()}
                </p>
              </>
            ) : (
              <p className="text-sm text-muted-foreground">No runs yet</p>
            )}
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">
              Active Sources
            </CardTitle>
            <Database className="h-5 w-5 text-purple-600" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold font-heading text-primary">
              {sources.length}
            </div>
            <p className="text-xs text-muted-foreground mt-1">
              Discovery sources configured
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Manual Discovery */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-heading">Manual Discovery</CardTitle>
          <CardDescription>
            Run the discovery pipeline to find new facilities from enabled sources
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <Button
              onClick={runDiscovery}
              disabled={running}
              className="gradient-accent text-white flex-1"
              size="lg"
              data-testid="run-discovery-button"
            >
              {running ? (
                <>
                  <RefreshCw className="mr-2 h-5 w-5 animate-spin" />
                  Running Discovery...
                </>
              ) : (
                <>
                  <Play className="mr-2 h-5 w-5" />
                  Run Discovery Now
                </>
              )}
            </Button>
          </div>

          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <p className="text-sm text-blue-900">
              <strong>Production Mode:</strong> Discovers real facilities from enabled sources only.
              Make sure you have enabled at least one source in Source Management.
            </p>
          </div>
        </CardContent>
      </Card>

      {/* Database Cleanup */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-heading">Database Cleanup</CardTitle>
          <CardDescription>
            Remove generic and invalid company entries from the database
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            <Button
              onClick={previewCleanup}
              variant="outline"
              data-testid="preview-cleanup-button"
            >
              <Database className="mr-2 h-4 w-4" />
              Preview Cleanup
            </Button>
            {cleanupPreview && (
              <Button
                onClick={executeCleanup}
                disabled={cleaning}
                variant="destructive"
                data-testid="execute-cleanup-button"
              >
                {cleaning ? (
                  <>
                    <RefreshCw className="mr-2 h-4 w-4 animate-spin" />
                    Cleaning...
                  </>
                ) : (
                  <>
                    <Trash2 className="mr-2 h-4 w-4" />
                    Execute Cleanup
                  </>
                )}
              </Button>
            )}
          </div>

          {cleanupPreview && (
            <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
              <h4 className="font-semibold text-amber-900 mb-2">Cleanup Preview</h4>
              <div className="grid grid-cols-3 gap-4 mb-3">
                <div>
                  <p className="text-sm text-amber-700">Total Facilities</p>
                  <p className="text-2xl font-bold text-amber-900">{cleanupPreview.total_facilities}</p>
                </div>
                <div>
                  <p className="text-sm text-amber-700">Generic Entries</p>
                  <p className="text-2xl font-bold text-red-600">{cleanupPreview.generic_count}</p>
                </div>
                <div>
                  <p className="text-sm text-amber-700">Will Remove</p>
                  <p className="text-2xl font-bold text-red-600">{cleanupPreview.would_remove}</p>
                </div>
              </div>
              {cleanupPreview.generic_examples.length > 0 && (
                <div>
                  <p className="text-sm text-amber-700 mb-1">Examples to be removed:</p>
                  <ul className="list-disc list-inside text-xs text-amber-800">
                    {cleanupPreview.generic_examples.slice(0, 5).map((name, idx) => (
                      <li key={idx}>{name}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Scheduler Control */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-heading">Automated Scheduler</CardTitle>
          <CardDescription>
            Schedule automatic discovery runs to keep your database updated
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="flex items-center gap-4">
            {!status?.scheduler_running ? (
              <>
                <Button
                  onClick={() => startScheduler('daily')}
                  variant="outline"
                  data-testid="start-daily-button"
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  Start Daily
                </Button>
                <Button
                  onClick={() => startScheduler('weekly')}
                  variant="outline"
                  data-testid="start-weekly-button"
                >
                  <Calendar className="mr-2 h-4 w-4" />
                  Start Weekly
                </Button>
              </>
            ) : (
              <Button
                onClick={stopScheduler}
                variant="destructive"
                data-testid="stop-scheduler-button"
              >
                <StopCircle className="mr-2 h-4 w-4" />
                Stop Scheduler
              </Button>
            )}
          </div>
        </CardContent>
      </Card>

      {/* Discovery Sources */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-heading">Discovery Sources</CardTitle>
          <CardDescription>Configured data sources for facility discovery</CardDescription>
        </CardHeader>
        <CardContent>
          {sources.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No sources configured. Using demo sources.
            </p>
          ) : (
            <div className="space-y-3">
              {sources.map((source, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 rounded-lg border border-border"
                  data-testid={`source-${index}`}
                >
                  <div className="flex items-center gap-3">
                    <Search className="h-5 w-5 text-accent" />
                    <div>
                      <h4 className="font-semibold text-primary">{source.name}</h4>
                      <p className="text-sm text-muted-foreground capitalize">{source.type}</p>
                    </div>
                  </div>
                  <Badge variant="secondary">{source.max_facilities || 'N/A'} facilities</Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Source Health */}
      {sourceHealth.length > 0 && (
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-heading">Source Health (Last 7 Days)</CardTitle>
            <CardDescription>Performance metrics per discovery source</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {sourceHealth.map((source, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 rounded-lg border border-border"
                  data-testid={`source-health-${index}`}
                >
                  <div className="flex-1">
                    <h4 className="font-semibold text-primary">{source.source_name}</h4>
                    <p className="text-sm text-muted-foreground mt-1">
                      Last crawl: {source.last_crawl ? new Date(source.last_crawl).toLocaleString() : 'Never'}
                    </p>
                  </div>
                  <div className="grid grid-cols-4 gap-6 text-center">
                    <div>
                      <p className="text-xs text-muted-foreground">Success Rate</p>
                      <p className={`text-lg font-bold ${
                        source.success_rate >= 80 ? 'text-green-600' :
                        source.success_rate >= 50 ? 'text-amber-600' :
                        'text-red-600'
                      }`}>
                        {source.success_rate.toFixed(0)}%
                      </p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Attempts</p>
                      <p className="text-lg font-bold text-primary">{source.total_attempts}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Discovered</p>
                      <p className="text-lg font-bold text-primary">{source.total_facilities_found}</p>
                    </div>
                    <div>
                      <p className="text-xs text-muted-foreground">Inserted</p>
                      <p className="text-lg font-bold text-accent">{source.total_facilities_inserted}</p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </CardContent>
        </Card>
      )}

      {/* Overall Health */}
      {overallHealth && (
        <Card>
          <CardHeader>
            <CardTitle className="text-2xl font-heading">System Health (Last 24 Hours)</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-6">
              <div>
                <p className="text-sm text-muted-foreground">Total Attempts</p>
                <p className="text-3xl font-bold text-primary mt-1">{overallHealth.total_attempts}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Success Rate</p>
                <p className={`text-3xl font-bold mt-1 ${
                  overallHealth.success_rate >= 80 ? 'text-green-600' :
                  overallHealth.success_rate >= 50 ? 'text-amber-600' :
                  'text-red-600'
                }`}>
                  {overallHealth.success_rate.toFixed(0)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Facilities Discovered</p>
                <p className="text-3xl font-bold text-primary mt-1">{overallHealth.facilities_discovered}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Successful Crawls</p>
                <p className="text-3xl font-bold text-green-600 mt-1">{overallHealth.successful_attempts}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Failed Crawls</p>
                <p className="text-3xl font-bold text-red-600 mt-1">{overallHealth.failed_attempts}</p>
              </div>
              <div>
                <p className="text-sm text-muted-foreground">Facilities Inserted</p>
                <p className="text-3xl font-bold text-accent mt-1">{overallHealth.facilities_inserted}</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Discovery Logs */}
      <Card>
        <CardHeader>
          <CardTitle className="text-2xl font-heading">Discovery History</CardTitle>
          <CardDescription>Recent discovery pipeline runs</CardDescription>
        </CardHeader>
        <CardContent>
          {logs.length === 0 ? (
            <p className="text-sm text-muted-foreground text-center py-8">
              No discovery runs yet. Click "Run Discovery" to start.
            </p>
          ) : (
            <div className="space-y-3">
              {logs.map((log, index) => (
                <div
                  key={index}
                  className="flex items-center justify-between p-4 rounded-lg border border-border"
                  data-testid={`log-${index}`}
                >
                  <div className="flex items-center gap-4">
                    {log.status === 'success' ? (
                      <CheckCircle2 className="h-5 w-5 text-green-600" />
                    ) : (
                      <XCircle className="h-5 w-5 text-red-600" />
                    )}
                    <div>
                      <div className="flex items-center gap-2">
                        <p className="font-semibold text-primary">
                          {log.facilities_inserted} facilities added
                        </p>
                        <Badge variant="outline" className="text-xs">
                          {log.mode}
                        </Badge>
                      </div>
                      <p className="text-sm text-muted-foreground">
                        {new Date(log.start_time).toLocaleString()} • {log.duration_seconds.toFixed(1)}s
                      </p>
                      {log.duplicates_skipped > 0 && (
                        <p className="text-xs text-muted-foreground mt-1">
                          {log.duplicates_skipped} duplicates skipped
                          {log.invalid_rejected > 0 && `, ${log.invalid_rejected} invalid rejected`}
                        </p>
                      )}
                      {!log.duplicates_skipped && log.invalid_rejected > 0 && (
                        <p className="text-xs text-muted-foreground mt-1">
                          {log.invalid_rejected} invalid rejected
                        </p>
                      )}
                    </div>
                  </div>
                  <div className="text-right">
                    <p className="text-sm font-medium text-muted-foreground">
                      {log.sources_crawled} sources
                    </p>
                    <p className="text-sm text-muted-foreground">
                      {log.facilities_discovered} discovered
                    </p>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
};

export default DiscoveryDashboard;
