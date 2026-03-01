import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { participantesService } from '../services/participantes';
import { Participante } from '../services/types';

interface ParticipanteModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (participante: Participante) => void;
  initialData?: Participante | null;
}

export const ParticipanteModal = ({ isOpen, onClose, onSuccess, initialData }: ParticipanteModalProps) => {
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState<Omit<Participante, 'id'>>({
    nome: '',
    documento: '',
    email: '',
    telefone: '',
    tipo: 'CLIENTE'
  });

  useEffect(() => {
    if (initialData) {
      setFormData({
        nome: initialData.nome,
        documento: initialData.documento || '',
        email: initialData.email || '',
        telefone: initialData.telefone || '',
        tipo: initialData.tipo
      });
    } else {
      setFormData({
        nome: '',
        documento: '',
        email: '',
        telefone: '',
        tipo: 'CLIENTE'
      });
    }
  }, [initialData, isOpen]);

  const createMutation = useMutation({
    mutationFn: participantesService.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['participantes'] });
      if (onSuccess) {
        onSuccess(data);
      }
      onClose();
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Participante> }) => 
      participantesService.update(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['participantes'] });
      if (onSuccess) {
        onSuccess(data);
      }
      onClose();
    }
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (initialData) {
      updateMutation.mutate({ id: initialData.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-[60]">
      <div className="bg-[var(--color-bg-paper)] rounded-lg shadow-xl w-full max-w-md border border-[var(--color-border)]">
        <div className="p-6 border-b border-[var(--color-border)]">
          <h2 className="text-xl font-bold text-[var(--color-text-main)]">{initialData ? 'Editar Participante' : 'Novo Participante'}</h2>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div>
            <label className="block text-sm font-medium text-[var(--color-text-muted)]">Nome</label>
            <input
              type="text"
              required
              className="mt-1 block w-full rounded-md border-[var(--color-border)] shadow-sm focus:border-[var(--color-primary)] focus:ring-[var(--color-primary)] border p-2 bg-[var(--color-bg-main)] text-[var(--color-text-main)]"
              value={formData.nome}
              onChange={e => setFormData({...formData, nome: e.target.value})}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--color-text-muted)]">Documento (CPF/CNPJ)</label>
            <input
              type="text"
              className="mt-1 block w-full rounded-md border-[var(--color-border)] shadow-sm focus:border-[var(--color-primary)] focus:ring-[var(--color-primary)] border p-2 bg-[var(--color-bg-main)] text-[var(--color-text-main)]"
              value={formData.documento}
              onChange={e => setFormData({...formData, documento: e.target.value})}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--color-text-muted)]">Email</label>
            <input
              type="email"
              className="mt-1 block w-full rounded-md border-[var(--color-border)] shadow-sm focus:border-[var(--color-primary)] focus:ring-[var(--color-primary)] border p-2 bg-[var(--color-bg-main)] text-[var(--color-text-main)]"
              value={formData.email}
              onChange={e => setFormData({...formData, email: e.target.value})}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--color-text-muted)]">Telefone</label>
            <input
              type="tel"
              className="mt-1 block w-full rounded-md border-[var(--color-border)] shadow-sm focus:border-[var(--color-primary)] focus:ring-[var(--color-primary)] border p-2 bg-[var(--color-bg-main)] text-[var(--color-text-main)]"
              value={formData.telefone}
              onChange={e => setFormData({...formData, telefone: e.target.value})}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-[var(--color-text-muted)]">Tipo</label>
            <select
              className="mt-1 block w-full rounded-md border-[var(--color-border)] shadow-sm focus:border-[var(--color-primary)] focus:ring-[var(--color-primary)] border p-2 bg-[var(--color-bg-main)] text-[var(--color-text-main)]"
              value={formData.tipo}
              onChange={e => setFormData({...formData, tipo: e.target.value as any})}
            >
              <option value="CLIENTE">Cliente</option>
              <option value="FORNECEDOR">Fornecedor</option>
              <option value="AMBOS">Ambos</option>
            </select>
          </div>

          <div className="flex justify-end gap-4 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-[var(--color-border)] rounded-md text-[var(--color-text-muted)] hover:bg-[var(--color-bg-main)] hover:text-[var(--color-text-main)] transition-colors"
            >
              Cancelar
            </button>
            <button
              type="submit"
              className="px-4 py-2 bg-[var(--color-primary)] text-[var(--color-primary-foreground)] rounded-md hover:bg-[var(--color-primary-hover)] transition-colors"
              disabled={createMutation.isPending || updateMutation.isPending}
            >
              {createMutation.isPending || updateMutation.isPending ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
