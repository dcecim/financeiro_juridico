import { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { financeiroService } from '../services/financeiro';
import { participantesService } from '../services/participantes';
import { processosService } from '../services/processos';
import { centrosCustoService } from '../services/centrosCusto';
import { 
  Lancamento, 
  LancamentoCreate, 
  TipoLancamento, 
  NaturezaLancamento, 
  StatusLancamento,
  ConciliacaoResult
} from '../services/types';
import { 
  Plus, 
  Search, 
  Edit, 
  Trash2, 
  Upload, 
  DollarSign, 
  ArrowUpCircle, 
  ArrowDownCircle,
  FileSpreadsheet,
  X,
  Check
} from 'lucide-react';

export const Financeiro = () => {
  const [activeTab, setActiveTab] = useState<'lancamentos' | 'conciliacao'>('lancamentos');
  const [searchTerm, setSearchTerm] = useState('');
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [isCreatingCC, setIsCreatingCC] = useState(false);
  const [newCCName, setNewCCName] = useState('');
  const [nextCode, setNextCode] = useState('');
  const [editingLancamento, setEditingLancamento] = useState<Lancamento | null>(null);

  useEffect(() => {
    if (isCreatingCC) {
      centrosCustoService.getNextCode().then(setNextCode).catch(() => setNextCode('??????'));
    }
  }, [isCreatingCC]);
  const [ofxFile, setOfxFile] = useState<File | null>(null);
  const [uploadingOfx, setUploadingOfx] = useState(false);
  const [conciliacaoResults, setConciliacaoResults] = useState<ConciliacaoResult[]>([]);

  const queryClient = useQueryClient();

  // Queries
  const { data: lancamentos, isLoading, error } = useQuery({
    queryKey: ['lancamentos'],
    queryFn: () => financeiroService.getLancamentos()
  });

  const { data: participantes } = useQuery({
    queryKey: ['participantes'],
    queryFn: participantesService.getAll
  });

  const { data: processos } = useQuery({
    queryKey: ['processos'],
    queryFn: processosService.getAll
  });

  const { data: centrosCusto } = useQuery({
    queryKey: ['centrosCusto'],
    queryFn: () => centrosCustoService.getAll()
  });

  // Mutations
  const createMutation = useMutation({
    mutationFn: financeiroService.createLancamento,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lancamentos'] });
      setIsModalOpen(false);
      resetForm();
    }
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<LancamentoCreate> }) => 
      financeiroService.updateLancamento(id, data),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lancamentos'] });
      setIsModalOpen(false);
      resetForm();
    }
  });

  const deleteMutation = useMutation({
    mutationFn: financeiroService.deleteLancamento,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['lancamentos'] });
    }
  });

  const createCCMutation = useMutation({
    mutationFn: (nome: string) => centrosCustoService.create({ nome, tipo: formData.tipo }),
    onSuccess: (newCC) => {
      queryClient.invalidateQueries({ queryKey: ['centrosCusto'] });
      setFormData({...formData, centro_custo_id: newCC.id});
      setIsCreatingCC(false);
      setNewCCName('');
    }
  });

  // Form
  const [formData, setFormData] = useState<LancamentoCreate>({
    descricao: '',
    valor: 0,
    tipo: TipoLancamento.DESPESA,
    natureza: NaturezaLancamento.PONTUAL,
    status: StatusLancamento.PENDENTE,
    participante_id: '',
    processo_id: undefined,
    centro_custo_id: '',
    data_vencimento: new Date().toISOString().split('T')[0],
    reembolsavel: false
  });

  const resetForm = () => {
    setFormData({
      descricao: '',
      valor: 0,
      tipo: TipoLancamento.DESPESA,
      natureza: NaturezaLancamento.PONTUAL,
      status: StatusLancamento.PENDENTE,
      participante_id: '',
      processo_id: undefined,
      centro_custo_id: '',
      data_vencimento: new Date().toISOString().split('T')[0],
      reembolsavel: false
    });
    setEditingLancamento(null);
  };

  const handleEdit = (lancamento: Lancamento) => {
    setEditingLancamento(lancamento);
    setFormData({
      descricao: lancamento.descricao,
      valor: lancamento.valor,
      tipo: lancamento.tipo,
      natureza: lancamento.natureza,
      status: lancamento.status,
      participante_id: lancamento.participante_id,
      processo_id: lancamento.processo_id,
      centro_custo_id: lancamento.centro_custo_id,
      data_vencimento: lancamento.data_vencimento,
      data_pagamento: lancamento.data_pagamento,
      reembolsavel: lancamento.reembolsavel
    });
    setIsModalOpen(true);
  };

  const handleDelete = (id: string) => {
    if (confirm('Tem certeza que deseja excluir este lançamento?')) {
      deleteMutation.mutate(id);
    }
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (editingLancamento) {
      updateMutation.mutate({ id: editingLancamento.id, data: formData });
    } else {
      createMutation.mutate(formData);
    }
  };

  const handleOfxUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!ofxFile) return;

    setUploadingOfx(true);
    try {
      const results = await financeiroService.uploadOfx(ofxFile);
      setConciliacaoResults(results);
      queryClient.invalidateQueries({ queryKey: ['lancamentos'] });
    } catch (error) {
      console.error(error);
      alert('Erro ao processar arquivo OFX');
    } finally {
      setUploadingOfx(false);
    }
  };

  const filteredLancamentos = lancamentos?.filter(l => 
    l.descricao.toLowerCase().includes(searchTerm.toLowerCase()) ||
    l.participante?.nome.toLowerCase().includes(searchTerm.toLowerCase())
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Financeiro</h1>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('lancamentos')}
            className={`px-4 py-2 rounded-lg transition-colors ${activeTab === 'lancamentos' ? 'bg-blue-100 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'}`}
          >
            Lançamentos
          </button>
          <button
            onClick={() => setActiveTab('conciliacao')}
            className={`px-4 py-2 rounded-lg transition-colors ${activeTab === 'conciliacao' ? 'bg-blue-100 text-blue-700 font-medium' : 'text-gray-600 hover:bg-gray-100'}`}
          >
            Conciliação OFX
          </button>
        </div>
      </div>

      {activeTab === 'lancamentos' ? (
        <>
          <div className="flex justify-between items-center">
            <div className="flex-1 max-w-lg relative">
              <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
              <input
                type="text"
                placeholder="Buscar lançamentos..."
                className="w-full pl-10 pr-4 py-2 border rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-500"
                value={searchTerm}
                onChange={(e) => setSearchTerm(e.target.value)}
              />
            </div>
            <button
              onClick={() => { resetForm(); setIsModalOpen(true); }}
              className="bg-blue-600 text-white px-4 py-2 rounded-lg flex items-center gap-2 hover:bg-blue-700 ml-4"
            >
              <Plus size={20} />
              Novo Lançamento
            </button>
          </div>

          {isLoading ? (
            <div className="text-center py-8">Carregando...</div>
          ) : error ? (
            <div className="text-center py-8 text-red-600">Erro: {(error as any).message}</div>
          ) : (
            <div className="bg-white rounded-lg shadow overflow-hidden">
              <table className="min-w-full divide-y divide-gray-200">
                <thead className="bg-gray-50">
                  <tr>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Data</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Descrição</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Participante</th>
                    <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Status</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Valor</th>
                    <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">Ações</th>
                  </tr>
                </thead>
                <tbody className="bg-white divide-y divide-gray-200">
                  {filteredLancamentos?.map((lancamento) => (
                    <tr key={lancamento.id} className="hover:bg-gray-50">
                      <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">
                        {new Date(lancamento.data_vencimento || '').toLocaleDateString()}
                      </td>
                      <td className="px-6 py-4">
                        <div className="text-sm font-medium text-gray-900">{lancamento.descricao}</div>
                        <div className="text-xs text-gray-500">{lancamento.natureza} - {lancamento.processo?.numero}</div>
                      </td>
                      <td className="px-6 py-4 text-sm text-gray-500">
                        {lancamento.participante?.nome}
                      </td>
                      <td className="px-6 py-4">
                        <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                          ${lancamento.status === StatusLancamento.PAGO ? 'bg-green-100 text-green-800' : 
                            lancamento.status === StatusLancamento.PENDENTE ? 'bg-yellow-100 text-yellow-800' : 
                            'bg-red-100 text-red-800'}`}>
                          {lancamento.status}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right text-sm font-medium">
                        <span className={lancamento.tipo === TipoLancamento.RECEITA ? 'text-green-600' : 'text-red-600'}>
                          {lancamento.tipo === TipoLancamento.RECEITA ? '+' : '-'} R$ {Number(lancamento.valor).toFixed(2)}
                        </span>
                      </td>
                      <td className="px-6 py-4 text-right text-sm font-medium">
                        <button onClick={() => handleEdit(lancamento)} className="text-blue-600 hover:text-blue-900 mr-4">
                          <Edit size={18} />
                        </button>
                        <button onClick={() => handleDelete(lancamento.id)} className="text-red-600 hover:text-red-900">
                          <Trash2 size={18} />
                        </button>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </>
      ) : (
        <div className="bg-white p-6 rounded-lg shadow">
          <h2 className="text-lg font-medium mb-4 flex items-center gap-2">
            <Upload size={20} />
            Importar Arquivo OFX
          </h2>
          <form onSubmit={handleOfxUpload} className="mb-8">
            <div className="flex gap-4 items-end">
              <div className="flex-1">
                <label className="block text-sm font-medium text-gray-700 mb-2">Selecione o arquivo .ofx</label>
                <input
                  type="file"
                  accept=".ofx"
                  onChange={(e) => setOfxFile(e.target.files?.[0] || null)}
                  className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"
                />
              </div>
              <button
                type="submit"
                disabled={!ofxFile || uploadingOfx}
                className="bg-green-600 text-white px-6 py-2 rounded-lg hover:bg-green-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {uploadingOfx ? 'Processando...' : 'Importar e Conciliar'}
              </button>
            </div>
          </form>

          {conciliacaoResults.length > 0 && (
            <div className="space-y-4">
              <h3 className="text-lg font-medium">Resultados da Conciliação</h3>
              <div className="bg-gray-50 rounded-lg overflow-hidden border">
                <table className="min-w-full divide-y divide-gray-200">
                  <thead className="bg-gray-100">
                    <tr>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">OFX ID</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Match</th>
                      <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Mensagem</th>
                    </tr>
                  </thead>
                  <tbody className="bg-white divide-y divide-gray-200">
                    {conciliacaoResults.map((result, idx) => (
                      <tr key={idx}>
                        <td className="px-6 py-4 text-sm text-gray-500">{result.ofx_id}</td>
                        <td className="px-6 py-4">
                          <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                            ${result.tipo_match === 'EXACT' ? 'bg-green-100 text-green-800' : 
                              result.tipo_match === 'PARTIAL' ? 'bg-yellow-100 text-yellow-800' : 
                              'bg-gray-100 text-gray-800'}`}>
                            {result.tipo_match}
                          </span>
                        </td>
                        <td className="px-6 py-4 text-sm text-gray-900">{result.mensagem}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}

      {/* Modal Lançamento */}
      {isModalOpen && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center p-4 z-50">
          <div className="bg-white rounded-lg shadow-xl w-full max-w-2xl max-h-[90vh] overflow-y-auto">
            <div className="p-6 border-b">
              <h2 className="text-xl font-bold">{editingLancamento ? 'Editar Lançamento' : 'Novo Lançamento'}</h2>
            </div>
            <form onSubmit={handleSubmit} className="p-6 space-y-4">
              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Descrição</label>
                  <input
                    type="text"
                    required
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                    value={formData.descricao}
                    onChange={e => setFormData({...formData, descricao: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Valor (R$)</label>
                  <input
                    type="number"
                    step="0.01"
                    required
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                    value={formData.valor}
                    onChange={e => setFormData({...formData, valor: parseFloat(e.target.value)})}
                  />
                </div>
              </div>

              <div className="grid grid-cols-3 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Tipo</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                    value={formData.tipo}
                    onChange={e => setFormData({...formData, tipo: e.target.value as TipoLancamento})}
                  >
                    {Object.values(TipoLancamento).map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Natureza</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                    value={formData.natureza}
                    onChange={e => setFormData({...formData, natureza: e.target.value as NaturezaLancamento})}
                  >
                    {Object.values(NaturezaLancamento).map(n => (
                      <option key={n} value={n}>{n}</option>
                    ))}
                  </select>
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Status</label>
                  <select
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                    value={formData.status}
                    onChange={e => setFormData({...formData, status: e.target.value as StatusLancamento})}
                  >
                    {Object.values(StatusLancamento).map(s => (
                      <option key={s} value={s}>{s}</option>
                    ))}
                  </select>
                </div>
              </div>

              <div className="grid grid-cols-2 gap-4">
                <div>
                  <label className="block text-sm font-medium text-gray-700">Data Vencimento</label>
                  <input
                    type="date"
                    required
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                    value={formData.data_vencimento ? new Date(formData.data_vencimento).toISOString().split('T')[0] : ''}
                    onChange={e => setFormData({...formData, data_vencimento: e.target.value})}
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700">Data Pagamento</label>
                  <input
                    type="date"
                    className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                    value={formData.data_pagamento ? new Date(formData.data_pagamento).toISOString().split('T')[0] : ''}
                    onChange={e => setFormData({...formData, data_pagamento: e.target.value || undefined})}
                  />
                </div>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Participante</label>
                <select
                  required
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                  value={formData.participante_id}
                  onChange={e => setFormData({...formData, participante_id: e.target.value})}
                >
                  <option value="">Selecione...</option>
                  {participantes?.map(p => (
                    <option key={p.id} value={p.id}>{p.nome}</option>
                  ))}
                </select>
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Centro de Custo</label>
                {isCreatingCC ? (
                  <div className="flex gap-2 mt-1 items-center">
                    <div className="flex items-center justify-center bg-gray-100 border border-gray-300 rounded px-3 py-2 text-gray-500 font-mono text-sm whitespace-nowrap" title="Código Automático">
                       {nextCode || '...'}
                    </div>
                    <input
                      type="text"
                      autoFocus
                      placeholder="Nome do novo centro de custo"
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                      value={newCCName}
                      onChange={e => setNewCCName(e.target.value)}
                      onKeyDown={e => {
                        if (e.key === 'Enter') {
                          e.preventDefault();
                          if (newCCName.trim()) createCCMutation.mutate(newCCName);
                        }
                      }}
                    />
                    <button
                      type="button"
                      onClick={() => { if(newCCName.trim()) createCCMutation.mutate(newCCName); }}
                      className="p-2 bg-green-100 text-green-700 rounded hover:bg-green-200"
                      title="Salvar"
                    >
                      <Check size={20} />
                    </button>
                    <button
                      type="button"
                      onClick={() => setIsCreatingCC(false)}
                      className="p-2 bg-red-100 text-red-700 rounded hover:bg-red-200"
                      title="Cancelar"
                    >
                      <X size={20} />
                    </button>
                  </div>
                ) : (
                  <div className="flex gap-2 mt-1">
                    <select
                      required
                      className="block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                      value={formData.centro_custo_id}
                      onChange={e => {
                        if (e.target.value === 'NEW') {
                          setIsCreatingCC(true);
                          setNewCCName('');
                        } else {
                          setFormData({...formData, centro_custo_id: e.target.value});
                        }
                      }}
                    >
                      <option value="">Selecione...</option>
                      <option value="NEW" className="font-semibold text-blue-600">+ Novo Centro de Custo</option>
                      {centrosCusto?.filter(cc => cc.tipo === formData.tipo).map(cc => (
                        <option key={cc.id} value={cc.id}>{cc.codigo ? `${cc.codigo} - ` : ''}{cc.nome}</option>
                      ))}
                    </select>
                    <button
                      type="button"
                      onClick={() => setIsCreatingCC(true)}
                      className="p-2 bg-gray-100 text-gray-600 rounded hover:bg-gray-200"
                      title="Criar novo"
                    >
                      <Plus size={20} />
                    </button>
                  </div>
                )}
              </div>

              <div>
                <label className="block text-sm font-medium text-gray-700">Processo (Opcional)</label>
                <select
                  className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 border p-2"
                  value={formData.processo_id || ''}
                  onChange={e => setFormData({...formData, processo_id: e.target.value || undefined})}
                >
                  <option value="">Nenhum</option>
                  {processos?.map(p => (
                    <option key={p.id} value={p.id}>{p.numero} - {p.titulo_causa}</option>
                  ))}
                </select>
              </div>

              <div className="flex items-center">
                <input
                  type="checkbox"
                  id="reembolsavel"
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  checked={formData.reembolsavel}
                  onChange={e => setFormData({...formData, reembolsavel: e.target.checked})}
                />
                <label htmlFor="reembolsavel" className="ml-2 block text-sm text-gray-900">
                  Reembolsável
                </label>
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
