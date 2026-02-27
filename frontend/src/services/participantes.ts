import api from '../lib/api';
import { Participante } from './types';

export const participantesService = {
  async getAll(): Promise<Participante[]> {
    const response = await api.get<Participante[]>('/participantes/');
    return response.data;
  },

  async getById(id: string): Promise<Participante> {
    const response = await api.get<Participante>(`/participantes/${id}`);
    return response.data;
  },

  async create(data: Omit<Participante, 'id'>): Promise<Participante> {
    const response = await api.post<Participante>('/participantes/', data);
    return response.data;
  },

  async update(id: string, data: Partial<Omit<Participante, 'id'>>): Promise<Participante> {
    const response = await api.put<Participante>(`/participantes/${id}`, data);
    return response.data;
  },

  async delete(id: string): Promise<void> {
    await api.delete(`/participantes/${id}`);
  }
};
