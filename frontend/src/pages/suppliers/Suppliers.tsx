import React, { useState } from 'react';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../../components/ui/card';
import { Button } from '../../components/ui/button';
import { Plus, Search, Loader2, AlertCircle, User, Phone, Mail, MapPin, Star } from 'lucide-react';
import { useSuppliers } from '../../hooks/api/useSuppliers';

const Suppliers: React.FC = () => {
  const { suppliers, loading, error, refetch } = useSuppliers();
  const [searchTerm, setSearchTerm] = useState('');

  // Filter suppliers based on search term
  const filteredSuppliers = suppliers.filter(supplier =>
    supplier.name.toLowerCase().includes(searchTerm.toLowerCase()) ||
    supplier.contact_person?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    supplier.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const renderRating = (rating?: number) => {
    if (!rating) return <span className="text-muted-foreground">No rating</span>;
    
    return (
      <div className="flex items-center">
        {[1, 2, 3, 4, 5].map((star) => (
          <Star
            key={star}
            className={`w-4 h-4 ${
              star <= rating 
                ? 'text-yellow-400 fill-yellow-400' 
                : 'text-gray-300'
            }`}
          />
        ))}
        <span className="ml-1 text-sm text-muted-foreground">({rating}/5)</span>
      </div>
    );
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center h-64">
        <Loader2 className="w-8 h-8 animate-spin" />
        <span className="ml-2">Loading suppliers...</span>
      </div>
    );
  }

  return (
    <div>
      {/* Header */}
      <div className="flex justify-between items-center mb-6">
        <div>
          <h1 className="text-3xl font-bold">Suppliers</h1>
          <p className="text-muted-foreground">Manage your supplier relationships</p>
        </div>
        <Button>
          <Plus className="w-4 h-4 mr-2" />
          Add Supplier
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
              placeholder="Search suppliers by name, contact person, or email..."
              value={searchTerm}
              onChange={(e) => setSearchTerm(e.target.value)}
              className="pl-10 pr-4 py-2 w-full border border-input rounded-md focus:outline-none focus:ring-2 focus:ring-ring"
            />
          </div>
        </CardContent>
      </Card>

      {/* Summary Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-6">
        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-blue-100 rounded-full">
                <User className="w-6 h-6 text-blue-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-muted-foreground">Total Suppliers</p>
                <p className="text-2xl font-bold">{suppliers.length}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-green-100 rounded-full">
                <User className="w-6 h-6 text-green-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-muted-foreground">Active Suppliers</p>
                <p className="text-2xl font-bold">
                  {suppliers.filter(s => s.is_active).length}
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-yellow-100 rounded-full">
                <Star className="w-6 h-6 text-yellow-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-muted-foreground">Avg Rating</p>
                <p className="text-2xl font-bold">
                  {suppliers.length > 0 
                    ? (suppliers.reduce((sum, s) => sum + (s.performance_rating || 0), 0) / suppliers.length).toFixed(1)
                    : '0.0'
                  }
                </p>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardContent className="p-6">
            <div className="flex items-center">
              <div className="p-2 bg-purple-100 rounded-full">
                <MapPin className="w-6 h-6 text-purple-600" />
              </div>
              <div className="ml-4">
                <p className="text-sm text-muted-foreground">Avg Lead Time</p>
                <p className="text-2xl font-bold">
                  {suppliers.length > 0 
                    ? Math.round(suppliers.reduce((sum, s) => sum + s.lead_time_days, 0) / suppliers.length)
                    : 0
                  } days
                </p>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>

      {/* Suppliers Grid */}
      {filteredSuppliers.length === 0 ? (
        <Card>
          <CardContent className="p-8 text-center">
            <div className="text-muted-foreground">
              {searchTerm ? 'No suppliers found matching your search.' : 'No suppliers available.'}
            </div>
            {!searchTerm && (
              <Button className="mt-4">
                <Plus className="w-4 h-4 mr-2" />
                Add Your First Supplier
              </Button>
            )}
          </CardContent>
        </Card>
      ) : (
        <div className="grid gap-6">
          <Card>
            <CardHeader>
              <CardTitle>Suppliers ({filteredSuppliers.length})</CardTitle>
              <CardDescription>
                Showing {filteredSuppliers.length} of {suppliers.length} suppliers
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
                {filteredSuppliers.map((supplier) => (
                  <Card key={supplier.id} className="relative">
                    <CardHeader className="pb-3">
                      <div className="flex items-start justify-between">
                        <div>
                          <CardTitle className="text-lg">{supplier.name}</CardTitle>
                          <div className="flex items-center mt-1">
                            <span
                              className={`px-2 py-1 rounded-full text-xs font-medium ${
                                supplier.is_active
                                  ? 'bg-green-100 text-green-800'
                                  : 'bg-gray-100 text-gray-800'
                              }`}
                            >
                              {supplier.is_active ? 'Active' : 'Inactive'}
                            </span>
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
                    <CardContent className="space-y-3">
                      {supplier.contact_person && (
                        <div className="flex items-center text-sm">
                          <User className="w-4 h-4 mr-2 text-muted-foreground" />
                          <span>{supplier.contact_person}</span>
                        </div>
                      )}
                      
                      {supplier.email && (
                        <div className="flex items-center text-sm">
                          <Mail className="w-4 h-4 mr-2 text-muted-foreground" />
                          <span className="truncate">{supplier.email}</span>
                        </div>
                      )}
                      
                      {supplier.phone && (
                        <div className="flex items-center text-sm">
                          <Phone className="w-4 h-4 mr-2 text-muted-foreground" />
                          <span>{supplier.phone}</span>
                        </div>
                      )}
                      
                      {supplier.address && (
                        <div className="flex items-start text-sm">
                          <MapPin className="w-4 h-4 mr-2 text-muted-foreground mt-0.5" />
                          <span className="text-muted-foreground line-clamp-2">{supplier.address}</span>
                        </div>
                      )}

                      <div className="pt-2 border-t border-border">
                        <div className="flex justify-between items-center text-sm mb-2">
                          <span className="text-muted-foreground">Lead Time:</span>
                          <span className="font-medium">{supplier.lead_time_days} days</span>
                        </div>
                        
                        <div className="flex justify-between items-center text-sm mb-2">
                          <span className="text-muted-foreground">Min Order:</span>
                          <span className="font-medium">{supplier.minimum_order_qty}</span>
                        </div>
                        
                        {supplier.payment_terms && (
                          <div className="flex justify-between items-center text-sm mb-2">
                            <span className="text-muted-foreground">Payment:</span>
                            <span className="font-medium truncate">{supplier.payment_terms}</span>
                          </div>
                        )}

                        <div className="flex justify-between items-center text-sm">
                          <span className="text-muted-foreground">Rating:</span>
                          {renderRating(supplier.performance_rating)}
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                ))}
              </div>
            </CardContent>
          </Card>
        </div>
      )}
    </div>
  );
};

export default Suppliers;