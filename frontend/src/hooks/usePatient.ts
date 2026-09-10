import { useState, useEffect, useCallback } from 'react';
import { DashboardResponse } from '../types';
import { apiService } from '../services/api';

export function usePatient(patientId: string = 'P001') {
  const [data, setData] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);

  const fetchData = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const result = await apiService.getPatientDashboard(patientId);
      setData(result);
    } catch (err: any) {
      setError(err?.message || 'Unable to load patient information.');
      setData(null);
    } finally {
      setLoading(false);
    }
  }, [patientId]);

  useEffect(() => {
    fetchData();
  }, [fetchData]);

  return {
    data,
    loading,
    error,
    refetch: fetchData,
  };
}
