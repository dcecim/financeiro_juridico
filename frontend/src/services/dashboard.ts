import api from '../lib/api';
import { DashboardData } from './types';

interface DashboardParams {
  data_inicio?: string;
  data_fim?: string;
  status_processo?: string;
  centro_custo_id?: string;
}

export const dashboardService = {
  async getAnalytics(params: DashboardParams): Promise<DashboardData> {
    const response = await api.get<DashboardData>('/dashboard/analytics', { params });
    return response.data;
  }
};
