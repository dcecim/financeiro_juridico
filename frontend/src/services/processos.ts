import api from '../lib/api';
import { Processo, ProcessoCreate, ProcessoUpdate } from './types';

export const processosService = {
  async getAll(): Promise<Processo[]> {
    const response = await api.get<Processo[]>('/processos/');
    return response.data;
  },

  async getById(id: string): Promise<Processo> {
    const response = await api.get<Processo>(`/processos/${id}`);
    return response.data;
  },

  async create(data: ProcessoCreate): Promise<Processo> {
    const response = await api.post<Processo>('/processos/', data);
    return response.data;
  },

  async update(id: string, data: ProcessoUpdate): Promise<Processo> {
    const response = await api.put<Processo>(`/processos/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/processos/${id}`);
  }
};
