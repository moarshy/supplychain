import React from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Package, AlertTriangle, Activity, Loader2 } from 'lucide-react';
import { useSystemStats } from '../../hooks/api/useSystemStats';

const Dashboard: React.FC = () => {
  const { stats, loading, error } = useSystemStats();

  const StatCard = ({ 
    icon: Icon, 
    title, 
    value, 
    iconColor, 
    bgColor 
  }: {
    icon: React.ElementType;
    title: string;
    value: string | number;
    iconColor: string;
    bgColor: string;
  }) => (
    <Card>
      <CardContent className="p-6">
        <div className="flex items-center">
          <div className={`p-2 ${bgColor} rounded-full`}>
            <Icon className={`w-6 h-6 ${iconColor}`} />
          </div>
          <div className="ml-4">
            <p className="text-sm text-muted-foreground">{title}</p>
            <p className="text-2xl font-bold">
              {loading ? (
                <Loader2 className="w-6 h-6 animate-spin" />
              ) : error ? (
                "Error"
              ) : (
                value
              )}
            </p>
          </div>
        </div>
      </CardContent>
    </Card>
  );

  return (
    <div>
      <h1 className="text-3xl font-bold mb-6">Dashboard</h1>
      
      {error && (
        <Card className="mb-6 border-destructive">
          <CardContent className="p-4">
            <p className="text-destructive">Failed to load dashboard data: {error}</p>
          </CardContent>
        </Card>
      )}
      
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        <StatCard
          icon={Package}
          title="Total Products"
          value={stats?.products?.total || 0}
          iconColor="text-blue-600"
          bgColor="bg-blue-100"
        />

        <StatCard
          icon={Package}
          title="Active Products"
          value={stats?.products?.active || 0}
          iconColor="text-green-600"
          bgColor="bg-green-100"
        />

        <StatCard
          icon={AlertTriangle}
          title="Low Stock Items"
          value="0" // TODO: Add low stock API
          iconColor="text-yellow-600"
          bgColor="bg-yellow-100"
        />

        <StatCard
          icon={Activity}
          title="Total Transactions"
          value={stats?.transactions?.total || 0}
          iconColor="text-red-600"
          bgColor="bg-red-100"
        />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Recent Activity */}
        <Card>
          <CardHeader>
            <CardTitle>Recent Activity</CardTitle>
            <CardDescription>Latest inventory movements and updates</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              {loading ? (
                <div className="flex items-center justify-center py-4">
                  <Loader2 className="w-6 h-6 animate-spin" />
                  <span className="ml-2">Loading recent transactions...</span>
                </div>
              ) : (
                <div className="text-center py-4 text-muted-foreground">
                  No recent activity to display
                </div>
              )}
            </div>
          </CardContent>
        </Card>

        {/* Quick Actions */}
        <Card>
          <CardHeader>
            <CardTitle>Quick Actions</CardTitle>
            <CardDescription>Common tasks and operations</CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-3">
              <Button className="w-full" variant="default">
                Add New Product
              </Button>
              <Button className="w-full" variant="secondary">
                Record Transaction
              </Button>
              <Button className="w-full" variant="outline">
                Add Supplier
              </Button>
              <Button className="w-full" variant="ghost">
                View Reports
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* System Info */}
      {stats && (
        <Card className="mt-6">
          <CardHeader>
            <CardTitle>System Information</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
              <div>
                <p className="text-muted-foreground">Version</p>
                <p className="font-medium">{stats.system.version}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Database</p>
                <p className="font-medium">{stats.system.database_type}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Negative Inventory</p>
                <p className="font-medium">{stats.system.allow_negative_inventory ? 'Allowed' : 'Not Allowed'}</p>
              </div>
              <div>
                <p className="text-muted-foreground">Status</p>
                <p className="font-medium text-green-600">Online</p>
              </div>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default Dashboard;