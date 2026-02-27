import { useState, useEffect } from 'react';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { centrosCustoService } from '../services/centrosCusto';
import { CentroCusto, TipoLancamento } from '../services/types';

interface CentroCustoModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSuccess?: (centroCusto: CentroCusto) => void;
  initialData?: CentroCusto | null;
  parentOptions?: CentroCusto[]; // For parent selection
}

export const CentroCustoModal = ({ isOpen, onClose, onSuccess, initialData, parentOptions = [] }: CentroCustoModalProps) => {
  const queryClient = useQueryClient();
  
  const [formData, setFormData] = useState<Omit<CentroCusto, 'id' | 'children'>>({
    nome: '',
    codigo: '',
    descricao: '',
    tipo: TipoLancamento.DESPESA,
    parent_id: undefined
  });

  useEffect(() => {
    if (isOpen) {
      if (initialData) {
        setFormData({
          nome: initialData.nome,
          codigo: initialData.codigo || '',
          descricao: initialData.descricao || '',
          tipo: initialData.tipo || TipoLancamento.DESPESA,
          parent_id: initialData.parent_id
        });
      } else {
        // Fetch next code for new items
        centrosCustoService.getNextCode()
          .then(code => {
            setFormData({
              nome: '',
              codigo: code,
              descricao: '',
              tipo: TipoLancamento.DESPESA,
              parent_id: undefined
            });
          })
          .catch(() => {
            // Fallback
            setFormData({
              nome: '',
              codigo: '',
              descricao: '',
              tipo: TipoLancamento.DESPESA,
              parent_id: undefined
            });
          });
      }
    }
  }, [initialData, isOpen]);

  const createMutation = useMutation({
    mutationFn: centrosCustoService.create,
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['centrosCusto'] });
      if (onSuccess) {
        onSuccess(data);
      }
      onClose();
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<CentroCusto> }) => 
      centrosCustoService.update(id, data),
    onSuccess: (data) => {
      queryClient.invalidateQueries({ queryKey: ['centrosCusto'] });
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
      <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
        <div className="p-6 border-b">
          <h2 className="text-xl font-bold">{initialData ? 'Editar Centro de Custo' : 'Novo Centro de Custo'}</h2>
        </div>
        <form onSubmit={handleSubmit} className="p-6 space-y-4">
          <div className="flex gap-4">
            <div className="w-1/3">
              <label className="block text-sm font-medium text-gray-700">Código</label>
              <input
                type="text"
                readOnly
                className="mt-1 block w-full rounded-md border-gray-300 bg-gray-100 shadow-sm border p-2 cursor-not-allowed"
                value={formData.codigo || ''}
              />
            </div>
            <div className="w-2/3">
              <label className="block text-sm font-medium text-gray-700">Nome</label>
              <input
                type="text"
                required
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                value={formData.nome}
                onChange={e => setFormData({...formData, nome: e.target.value})}
              />
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Código</label>
            <input
              type="text"
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
              value={formData.codigo || ''}
              onChange={e => setFormData({...formData, codigo: e.target.value})}
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700">Descrição</label>
            <textarea
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
              rows={3}
              value={formData.descricao || ''}
              onChange={e => setFormData({...formData, descricao: e.target.value})}
            />
          </div>

          <div className="grid grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700">Tipo</label>
              <select
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                value={formData.tipo}
                onChange={e => setFormData({...formData, tipo: e.target.value as TipoLancamento})}
              >
                <option value={TipoLancamento.RECEITA}>Receita</option>
                <option value={TipoLancamento.DESPESA}>Despesa</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700">Pai (Superior)</label>
              <select
                className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                value={formData.parent_id || ''}
                onChange={e => setFormData({...formData, parent_id: e.target.value || undefined})}
              >
                <option value="">Nenhum (Raiz)</option>
                {parentOptions.filter(p => p.id !== initialData?.id).map(p => (
                  <option key={p.id} value={p.id}>{p.nome}</option>
                ))}
              </select>
            </div>
          </div>

          <div className="flex justify-end gap-3 mt-6">
            <button
              type="button"
              onClick={onClose}
              className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
            >
              Cancelar
            </button>
            <button
              type="submit"
              disabled={createMutation.isPending || updateMutation.isPending}
              className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 disabled:opacity-50"
            >
              {createMutation.isPending || updateMutation.isPending ? 'Salvando...' : 'Salvar'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};
