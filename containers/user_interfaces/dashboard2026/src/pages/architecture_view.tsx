import { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';
import { Skeleton } from '@/components/ui/skeleton';

interface ArchitectureMetric {
  name: string;
  value: number;
  status: 'ok' | 'warning' | 'error';
  detail?: string;
}

interface OwnershipViolation {
  engine: string;
  domain: string;
  invariant: string;
  file?: string;
  line?: number;
}

interface ArchitectureDrift {
  source: string;
  target: string;
  allowed: boolean;
  reason: string;
}

export function ArchitectureView() {
  const [metrics, setMetrics] = useState<ArchitectureMetric[]>([]);
  const [violations, setViolations] = useState<OwnershipViolation[]>([]);
  const [drifts, setDrifts] = useState<ArchitectureDrift[]>([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetchArchitectureData();
    const interval = setInterval(fetchArchitectureData, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchArchitectureData = async () => {
    setLoading(true);
    try {
      const [metricsRes, violationsRes, driftsRes] = await Promise.all([
        fetch('/api/architecture/metrics'),
        fetch('/api/architecture/violations'),
        fetch('/api/architecture/drift'),
      ]);

      const metricsData = await metricsRes.json();
      const violationsData = await violationsRes.json();
      const driftsData = await driftsRes.json();

      setMetrics(metricsData.metrics || []);
      setViolations(violationsData.violations || []);
      setDrifts(driftsData.drifts || []);
    } catch (error) {
      console.error('Failed to fetch architecture data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'ok': return 'bg-green-500';
      case 'warning': return 'bg-yellow-500';
      case 'error': return 'bg-red-500';
      default: return 'bg-gray-500';
    }
  };

  if (loading) {
    return (
      <div className="space-y-4 p-4">
        <Skeleton className="h-8 w-full" />
        <Skeleton className="h-64 w-full" />
        <Skeleton className="h-64 w-full" />
      </div>
    );
  }

  return (
    <div className="space-y-4 p-4">
      <h1 className="text-2xl font-bold">Architecture Health Dashboard</h1>

      {/* Invariant Compliance */}
      <Card>
        <CardHeader>
          <CardTitle>Invariant Compliance</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            {metrics.map((m) => (
              <div key={m.name} className="flex flex-col items-center">
                <Badge className={getStatusColor(m.status)}>
                  {m.status.toUpperCase()}
                </Badge>
                <span className="text-sm mt-1">{m.name}</span>
                <span className="text-2xl font-mono">{m.value}%</span>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Ownership Violations */}
      <Card>
        <CardHeader>
          <CardTitle>Ownership Violations (INV-DIX-05)</CardTitle>
        </CardHeader>
        <CardContent>
          {violations.length === 0 ? (
            <Alert>
              <AlertDescription>No ownership violations detected</AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-2">
              {violations.map((v, i) => (
                <Alert key={i} variant="destructive">
                  <AlertDescription>
                    {v.engine} → {v.domain}: {v.invariant}
                  </AlertDescription>
                </Alert>
              ))}
            </div>
          )}
        </CardContent>
      </Card>

      {/* Architecture Drift */}
      <Card>
        <CardHeader>
          <CardTitle>Architecture Drift</CardTitle>
        </CardHeader>
        <CardContent>
          {drifts.length === 0 ? (
            <Alert>
              <AlertDescription>No architecture drift detected</AlertDescription>
            </Alert>
          ) : (
            <div className="space-y-2">
              {drifts.map((d, i) => (
                <div key={i} className="flex items-center justify-between p-2 border rounded">
                  <span className="font-mono">{d.source} → {d.target}</span>
                  <Badge variant={d.allowed ? 'outline' : 'destructive'}>
                    {d.allowed ? 'ALLOWED' : 'FORBIDDEN'}
                  </Badge>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}