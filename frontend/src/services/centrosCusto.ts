import api from '../lib/api';
import { CentroCusto } from './types';

export const centrosCustoService = {
  async getAll(tipo?: string): Promise<CentroCusto[]> {
    const params = tipo ? { tipo } : {};
    const response = await api.get<CentroCusto[]>('/centros-custo/', { params });
    return response.data;
  },

  async getById(id: string): Promise<CentroCusto> {
    const response = await api.get<CentroCusto>(`/centros-custo/${id}`);
    return response.data;
  },

  async create(data: Partial<CentroCusto>): Promise<CentroCusto> {
    const response = await api.post<CentroCusto>('/centros-custo/', data);
    return response.data;
  },

  async update(id: string, data: Partial<CentroCusto>): Promise<CentroCusto> {
    const response = await api.put<CentroCusto>(`/centros-custo/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/centros-custo/${id}`);
  },

  async getNextCode(): Promise<string> {
    const response = await api.get<string>('/centros-custo/next-code');
    return response.data;
  }
};
