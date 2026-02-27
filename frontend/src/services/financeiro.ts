import api from '../lib/api';
import { 
  Lancamento, 
  LancamentoCreate, 
  LancamentoUpdate, 
  ConciliacaoResult 
} from './types';

export const financeiroService = {
  async getLancamentos(params?: any): Promise<Lancamento[]> {
    const response = await api.get<Lancamento[]>('/lancamentos/', { params });
    return response.data;
  },

  async getLancamentoById(id: string): Promise<Lancamento> {
    const response = await api.get<Lancamento>(`/lancamentos/${id}`);
    return response.data;
  },

  async createLancamento(data: LancamentoCreate): Promise<Lancamento> {
    const response = await api.post<Lancamento>('/lancamentos/', data);
    return response.data;
  },

  async updateLancamento(id: string, data: LancamentoUpdate): Promise<Lancamento> {
    const response = await api.put<Lancamento>(`/lancamentos/${id}`, data);
    return response.data;
  },

  async deleteLancamento(id: string): Promise<void> {
    await api.delete(`/lancamentos/${id}`);
  },

  async uploadOfx(file: File): Promise<ConciliacaoResult[]> {
    const formData = new FormData();
    formData.append('file', file);
    
    const response = await api.post<ConciliacaoResult[]>('/conciliacao/upload', formData, {
      headers: {
        'Content-Type': 'multipart/form-data',
      },
    });
    return response.data;
  }
};
