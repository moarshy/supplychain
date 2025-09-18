import { useState, useEffect } from 'react';
import { api } from '../../services/api';
import type { Location } from '../../services/api';

export function useLocations() {
  const [locations, setLocations] = useState<Location[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchLocations = async () => {
    try {
      setLoading(true);
      setError(null);
      const data = await api.locations.getAll();
      setLocations(data);
    } catch (err) {
      console.error('Failed to fetch locations:', err);
      setError(err instanceof Error ? err.message : 'Failed to fetch locations');
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLocations();
  }, []);

  const createLocation = async (location: Partial<Location>): Promise<Location | null> => {
    try {
      setError(null);
      const newLocation = await api.locations.create(location);
      setLocations(prev => [...prev, newLocation]);
      return newLocation;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to create location');
      return null;
    }
  };

  const updateLocation = async (id: number, location: Partial<Location>): Promise<Location | null> => {
    try {
      setError(null);
      const updatedLocation = await api.locations.update(id, location);
      setLocations(prev => prev.map(l => l.id === id ? updatedLocation : l));
      return updatedLocation;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to update location');
      return null;
    }
  };

  const deleteLocation = async (id: number): Promise<boolean> => {
    try {
      setError(null);
      await api.locations.delete(id);
      setLocations(prev => prev.filter(l => l.id !== id));
      return true;
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to delete location');
      return false;
    }
  };

  return {
    locations,
    loading,
    error,
    refetch: fetchLocations,
    createLocation,
    updateLocation,
    deleteLocation,
  };
}