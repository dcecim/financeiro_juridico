import { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { participantesService } from '../services/participantes';
import { Participante } from '../services/types';
import { Plus, Search, Edit, Trash2, Users, Mail, Phone, FileText } from 'lucide-react';

export const Participantes = () => {
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingParticipante, setEditingParticipante] = useState<Participante | null>(null);

  const queryClient = useQueryClient();

  const { data: participantes, isLoading } = useQuery({
    queryKey: ['participantes'],
    queryFn: participantesService.getAll
  });

  const createMutation = useMutation({
    mutationFn: participantesService.create,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['participantes'] });
      setIsModalOpen(false);
      resetForm();
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<Participante> }) => 
      participantesService.update(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['participantes'] });
      setIsModalOpen(false);
      resetForm();
    }
  });

  const deleteMutation = useMutation({
    mutationFn: participantesService.delete,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['participantes'] });
    }
  });

  const [formData, setFormData] = useState<Omit<Participante, 'id'>>({
    nome: '',
    documento: '',
    email: '',
    telefone: '',
    tipo: 'CLIENTE'
  });

  const resetForm = () => {
    setFormData({
      nome: '',
      documento: '',
      email: '',
      telefone: '',
      tipo: 'CLIENTE'
    });
    setEditingParticipante(null);
  };

  const handleEdit = (participante: Participante) => {
    setEditingParticipante(participante);
    setFormData({
      nome: participante.nome,
      documento: participante.documento || '',
      email: participante.email || '',
      telefone: participante.telefone || '',
      tipo: participante.tipo
    });
    setIsModalOpen(true);
  };

  const handleDelete = (id: string) => {
    if (confirm('Tem certeza que deseja excluir este participante?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingParticipante) {
      updateMutation.mutate({ id: editingParticipante.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const filteredParticipantes = participantes?.filter(p => 
    p.nome.toLowerCase().includes(searchTerm.toLowerCase()) ||
    p.documento?.includes(searchTerm) ||
    p.email?.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center gap-2">
          <Users className="text-blue-600" />
          Participantes
        </h1>
        <button
          onClick={() => { resetForm(); setIsModalOpen(true); }}
          className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700"
        >
          <Plus size={20} />
          Novo Participante
        </button>
      </div>

      <div className="relative">
        <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
        <input
          type="text"
          placeholder="Buscar por nome, documento ou email..."
          className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
          value={searchTerm}
          onChange={(e) => setSearchTerm(e.target.value)}
        />
      </div>

      {isLoading ? (
        <div className="text-center py-8">Carregando...</div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredParticipantes?.map((participante) => (
            <div key={participante.id} className="bg-white rounded-lg shadow p-6 hover:shadow-md transition-shadow">
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-lg font-semibold text-gray-900">{participante.nome}</h3>
                  <span className={`text-xs px-2 py-1 rounded-full font-medium
                    ${participante.tipo === 'CLIENTE' ? 'bg-green-100 text-green-800' : 
                      participante.tipo === 'FORNECEDOR' ? 'bg-purple-100 text-purple-800' : 
                      'bg-blue-100 text-blue-800'}`}>
                    {participante.tipo}
                  </span>
                </div>
                <div className="flex gap-2">
                  <button onClick={() => handleEdit(participante)} className="text-gray-400 hover:text-blue-600">
                    <Edit size={18} />
                  </button>
                  <button onClick={() => handleDelete(participante.id)} className="text-gray-400 hover:text-red-600">
                    <Trash2 size={18} />
                  </button>
                </div>
              </div>
              
              <div className="space-y-2 text-sm text-gray-600">
                {participante.documento && (
                  <div className="flex items-center gap-2">
                    <FileText size={16} />
                    <span>{participante.documento}</span>
                  </div>
                )}
                {participante.email && (
                  <div className="flex items-center gap-2">
                    <Mail size={16} />
                    <a href={`mailto:${participante.email}`} className="hover:text-blue-600">
                      {participante.email}
                    </a>
                  </div>
                )}
                {participante.telefone && (
                  <div className="flex items-center gap-2">
                    <Phone size={16} />
                    <span>{participante.telefone}</span>
                  </div>
                )}
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Modal */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-md">
            <div className="p-6 border-b">
              <h2 className="text-xl font-bold">{editingParticipante ? 'Editar Participante' : 'Novo Participante'}</h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div>
                <label className="block text-sm font-medium text-gray-700">Nome</label>
                <input
                  type="text"
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                  value={formData.nome}
                  onChange={e => setFormData({...formData, nome: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Documento (CPF/CNPJ)</label>
                <input
                  type="text"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                  value={formData.documento}
                  onChange={e => setFormData({...formData, documento: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Email</label>
                <input
                  type="email"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                  value={formData.email}
                  onChange={e => setFormData({...formData, email: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Telefone</label>
                <input
                  type="tel"
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                  value={formData.telefone}
                  onChange={e => setFormData({...formData, telefone: e.target.value})}
                />
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Tipo</label>
                <select
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
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
    </div>
  );
};
