import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Plus, Search, Loader2, AlertCircle, MapPin, Warehouse, Building } from 'lucide-react';
import { useLocations } from '../../hooks/api/useLocations';
import { useInventory } from '../../hooks/api/useInventory';

const Locations: React.FC = () => {
  const { locations, loading, error, refetch } = useLocations();
  const { inventory } = useInventory();
  const [searchTerm, setSearchTerm] = useState('');

  // Filter locations based on search term
  const filteredLocations = locations.filter(location =>
    location.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    location.code?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    location.address?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    location.warehouse_type?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  // Calculate inventory stats per location
  const getLocationStats = (locationId: number) => {
    const locationInventory = inventory.filter(item => item.location_id === locationId);
    return {
      totalItems: locationInventory.length,
      totalQuantity: locationInventory.reduce((sum, item) => sum + item.quantity_on_hand, 0),
      availableQuantity: locationInventory.reduce((sum, item) => sum + item.available_quantity, 0),
    };
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin" />
        <span className="ml-2">Loading locations...</span>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Locations</h1>
          <p className="text-muted-foreground">Manage warehouses and storage locations</p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Add Location
        </Button>
      </div>

      {/* Error Display */}
      {error && (
        <Card className="mb-6 border-destructive">
          <CardContent className="p-4">
            <div className="flex items-center">
              <AlertCircle className="w-5 h-5 text-destructive mr-2" />
              <span className="text-destructive">{error}</span>
              <Button variant="outline" size="sm" onClick={refetch} className="ml-auto">
                Retry
              </Button>
            </div>
          </CardContent>
        </Card>
      )}

      {/* Search */}
      <Card className="mb-6">
        <CardContent className="p-4">
          <div className="relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-muted-foreground w-4 h-4" />
            <input
              type="text"
              placeholder="Search locations by name, code, address, or type..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-full">
                <MapPin className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-muted-foreground">Total Locations</p>
                <p className="text-2xl font-bold">{locations.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-full">
                <Building className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-muted-foreground">Active Locations</p>
                <p className="text-2xl font-bold">
                  {locations.filter(l => l.is_active).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-full">
                <Warehouse className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-muted-foreground">Warehouse Types</p>
                <p className="text-2xl font-bold">
                  {new Set(locations.map(l => l.warehouse_type).filter(Boolean)).size}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Locations Grid */}
      {filteredLocations.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="text-muted-foreground">
              {searchTerm ? 'No locations found matching your search.' : 'No locations available.'}
            </div>
            {!searchTerm && (
              <Button className="mt-4">
                <Plus className="w-4 h-4 mr-2" />
                Add Your First Location
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Locations ({filteredLocations.length})</CardTitle>
              <CardDescription>
                Showing {filteredLocations.length} of {locations.length} locations
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filteredLocations.map((location) => {
                  const stats = getLocationStats(location.id);
                  
                  return (
                    <Card key={location.id} className="relative">
                      <CardHeader className="pb-3">
                        <div className="flex items-start justify-between">
                          <div className="flex-1">
                            <CardTitle className="text-lg flex items-center">
                              <MapPin className="w-5 h-5 mr-2 text-muted-foreground" />
                              {location.name}
                            </CardTitle>
                            {location.code && (
                              <p className="text-sm text-muted-foreground font-mono mt-1">
                                {location.code}
                              </p>
                            )}
                            <div className="flex items-center mt-2">
                              <span
                                className={`px-2 py-1 rounded-full text-xs font-medium ${
                                  location.is_active
                                    ? 'bg-green-100 text-green-800'
                                    : 'bg-gray-100 text-gray-800'
                                }`}
                              >
                                {location.is_active ? 'Active' : 'Inactive'}
                              </span>
                              {location.warehouse_type && (
                                <span className="ml-2 px-2 py-1 rounded-full text-xs font-medium bg-blue-100 text-blue-800">
                                  {location.warehouse_type}
                                </span>
                              )}
                            </div>
                          </div>
                          <div className="flex gap-1">
                            <Button variant="ghost" size="sm">
                              Edit
                            </Button>
                            <Button variant="ghost" size="sm">
                              View
                            </Button>
                          </div>
                        </div>
                      </CardHeader>
                      <CardContent className="space-y-4">
                        {location.address && (
                          <div className="flex items-start text-sm">
                            <Building className="w-4 h-4 mr-2 text-muted-foreground mt-0.5" />
                            <span className="text-muted-foreground line-clamp-3">{location.address}</span>
                          </div>
                        )}

                        {/* Inventory Stats */}
                        <div className="pt-3 border-t border-border space-y-2">
                          <h4 className="text-sm font-medium text-muted-foreground">Inventory Summary</h4>
                          
                          <div className="grid grid-cols-3 gap-3 text-center">
                            <div>
                              <p className="text-lg font-bold text-blue-600">{stats.totalItems}</p>
                              <p className="text-xs text-muted-foreground">Items</p>
                            </div>
                            <div>
                              <p className="text-lg font-bold text-green-600">{stats.totalQuantity}</p>
                              <p className="text-xs text-muted-foreground">On Hand</p>
                            </div>
                            <div>
                              <p className="text-lg font-bold text-purple-600">{stats.availableQuantity}</p>
                              <p className="text-xs text-muted-foreground">Available</p>
                            </div>
                          </div>
                        </div>

                        {/* Metadata */}
                        <div className="pt-2 border-t border-border text-xs text-muted-foreground">
                          <p>Created: {new Date(location.created_at).toLocaleDateString()}</p>
                          <p>Updated: {new Date(location.updated_at).toLocaleDateString()}</p>
                        </div>
                      </CardContent>
                    </Card>
                  );
                })}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Locations;