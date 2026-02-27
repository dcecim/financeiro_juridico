import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { processosService } from '../services/processos';
import { participantesService } from '../services/participantes';
import { Processo, ProcessoCreate, StatusProcesso, Participante } from '../services/types';
import { Plus, Search, Edit, Trash2, FileText, DollarSign } from 'lucide-react';
import { ParticipanteModal } from '../components/ParticipanteModal';

export const Processos = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isParticipanteModalOpen, setIsParticipanteModalOpen] = useState(false);
  const [editingProcesso, setEditingProcesso] = useState<Processo | null>(null);
  
  const queryClient = useQueryClient();

  const { data: processos, isLoading, error } = useQuery({
    queryKey: ['processos'],
    queryFn: processosService.getAll
  });

  const { data: participantes } = useQuery({
    queryKey: ['participantes'],
    queryFn: participantesService.getAll
  });

  if (error) {
    console.error("Error fetching processos:", error);
  }
  if (processos) {
    console.log("Processos loaded:", processos);
  }

  const createMutation = useMutation({
    mutationFn: processosService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['processos'] });
      setIsModalOpen(false);
      resetForm();
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<ProcessoCreate> }) => 
      processosService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['processos'] });
      setIsModalOpen(false);
      resetForm();
    }
  });

  const deleteMutation = useMutation({
    mutationFn: processosService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['processos'] });
    }
  });

  // Form state
  const [formData, setFormData] = useState<ProcessoCreate>({
    numero: '',
    titulo_causa: '',
    descricao: '',
    status: StatusProcesso.ATIVO,
    cliente_id: '',
    valor_causa_estimado: 0,
    percentual_exito: 0,
    valor_pro_labore: 0
  });

  const resetForm = () => {
    setFormData({
      numero: '',
      titulo_causa: '',
      descricao: '',
      status: StatusProcesso.ATIVO,
      cliente_id: '',
      valor_causa_estimado: 0,
      percentual_exito: 0,
      valor_pro_labore: 0
    });
    setEditingProcesso(null);
  };

  const handleEdit = (processo: Processo) => {
    setEditingProcesso(processo);
    setFormData({
      numero: processo.numero,
      titulo_causa: processo.titulo_causa || '',
      descricao: processo.descricao || '',
      status: processo.status,
      cliente_id: processo.cliente_id,
      valor_causa_estimado: processo.valor_causa_estimado || 0,
      percentual_exito: processo.percentual_exito || 0,
      valor_pro_labore: processo.valor_pro_labore || 0
    });
    setIsModalOpen(true);
  };

  const handleDelete = (id: string) => {
    if (confirm('Tem certeza que deseja excluir este processo?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingProcesso) {
      updateMutation.mutate({ id: editingProcesso.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const filteredProcessos = processos?.filter(p => 
    p.numero.includes(searchTerm) || 
    p.titulo_causa?.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.cliente?.nome.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Processos</h1>
        <button
          onClick={() => { resetForm(); setIsModalOpen(true); }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
        >
          <Plus size={20} />
          Novo Processo
        </button>
      </div>

      <div className="bg-white p-4 rounded-lg shadow flex gap-4">
        <div className="flex-1 relative">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
          <input
            type="text"
            placeholder="Buscar por número, título ou cliente..."
            className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
          />
        </div>
      </div>

      {isLoading ? (
        <div className="text-center py-8">Carregando...</div>
      ) : error ? (
        <div className="text-center py-8 text-red-600">Erro ao carregar processos: {(error as any).message}</div>
      ) : (
        <div className="bg-white rounded-lg shadow overflow-hidden">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Número / Título</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Cliente</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Valores</th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {filteredProcessos?.map((processo) => (
                <tr key={processo.id} className="hover:bg-gray-50">
                  <td className="px-6 py-4">
                    <div className="text-sm font-medium text-gray-900">{processo.numero}</div>
                    <div className="text-sm text-gray-500">{processo.titulo_causa}</div>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    {processo.cliente?.nome || 'N/A'}
                  </td>
                  <td className="px-6 py-4">
                    <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                      ${processo.status === StatusProcesso.ATIVO ? 'bg-green-100 text-green-800' : 
                        processo.status === StatusProcesso.ENCERRADO ? 'bg-gray-100 text-gray-800' : 
                        'bg-yellow-100 text-yellow-800'}`}>
                      {processo.status}
                    </span>
                  </td>
                  <td className="px-6 py-4 text-sm text-gray-500">
                    <div>Estimado: R$ {Number(processo.valor_causa_estimado || 0).toFixed(2)}</div>
                    <div>Êxito: {Number(processo.percentual_exito || 0).toFixed(2)}%</div>
                  </td>
                  <td className="px-6 py-4 text-right text-sm font-medium">
                    <button onClick={() => handleEdit(processo)} className="text-blue-600 hover:text-blue-900 mr-4">
                      <Edit size={18} />
                    </button>
                    <button onClick={() => handleDelete(processo.id)} className="text-red-600 hover:text-red-900">
                      <Trash2 size={18} />
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h2 className="text-xl font-bold">{editingProcesso ? 'Editar Processo' : 'Novo Processo'}</h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Número do Processo</label>
                  <input
                    type="text"
                    required
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                    value={formData.numero}
                    onChange={e => setFormData({...formData, numero: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Título da Causa</label>
                  <input
                    type="text"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                    value={formData.titulo_causa || ''}
                    onChange={e => setFormData({...formData, titulo_causa: e.target.value})}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Cliente</label>
                <div className="flex gap-2">
                  <select
                    required
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                    value={formData.cliente_id}
                    onChange={e => setFormData({...formData, cliente_id: e.target.value})}
                  >
                    <option value="">Selecione um cliente...</option>
                    {participantes?.filter(p => p.tipo === 'CLIENTE' || p.tipo === 'AMBOS').map(p => (
                      <option key={p.id} value={p.id}>{p.nome}</option>
                    ))}
                  </select>
                  <button
                    type="button"
                    onClick={() => setIsParticipanteModalOpen(true)}
                    className="mt-1 px-3 bg-green-600 text-white rounded-md hover:bg-green-700 flex items-center justify-center"
                    title="Novo Cliente"
                  >
                    <Plus size={20} />
                  </button>
                </div>
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

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Valor Estimado (R$)</label>
                  <input
                    type="number"
                    step="0.01"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                    value={formData.valor_causa_estimado || 0}
                    onChange={e => setFormData({...formData, valor_causa_estimado: parseFloat(e.target.value)})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">% Êxito</label>
                  <input
                    type="number"
                    step="0.1"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                    value={formData.percentual_exito || 0}
                    onChange={e => setFormData({...formData, percentual_exito: parseFloat(e.target.value)})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Status</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                    value={formData.status}
                    onChange={e => setFormData({...formData, status: e.target.value as StatusProcesso})}
                  >
                    {Object.values(StatusProcesso).map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="flex justify-end gap-4 mt-6">
                <button
                  type="button"
                  onClick={() => setIsModalOpen(false)}
                  className="px-4 py-2 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-50"
                >
                  Cancelar
                </button>
                <button
                  type="submit"
                  className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700"
                  disabled={createMutation.isPending || updateMutation.isPending}
                >
                  {createMutation.isPending || updateMutation.isPending ? 'Salvando...' : 'Salvar'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      <ParticipanteModal 
        isOpen={isParticipanteModalOpen}
        onClose={() => setIsParticipanteModalOpen(false)}
        onSuccess={(novoParticipante) => {
          setFormData(prev => ({...prev, cliente_id: novoParticipante.id}));
        }}
      />
    </div>
  );
};
