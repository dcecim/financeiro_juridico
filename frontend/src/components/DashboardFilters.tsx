import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Filter, Search, X } from 'lucide-react';
import { centrosCustoService } from '../services/centrosCusto';
import { StatusProcesso } from '../services/types';

interface DashboardFiltersProps {
  initialFilters?: {
    data_inicio?: string;
    data_fim?: string;
    status_processo?: StatusProcesso;
    centro_custo_id?: string;
  };
  onFilterChange: (filters: {
    data_inicio?: string;
    data_fim?: string;
    status_processo?: StatusProcesso;
    centro_custo_id?: string;
  }) => void;
}

export const DashboardFilters = ({ initialFilters, onFilterChange }: DashboardFiltersProps) => {
  const [isOpen, setIsOpen] = useState(false);
  
  const [filters, setFilters] = useState({
    data_inicio: initialFilters?.data_inicio || '',
    data_fim: initialFilters?.data_fim || '',
    status_processo: initialFilters?.status_processo || '' as StatusProcesso | '',
    centro_custo_id: initialFilters?.centro_custo_id || ''
  });

  const { data: centrosCusto } = useQuery({
    queryKey: ['centrosCusto'],
    queryFn: () => centrosCustoService.getAll()
  });

  const handleSearch = () => {
    // Validation: Only search if dates are present
    if (filters.data_inicio && filters.data_fim) {
      onFilterChange({
        data_inicio: filters.data_inicio,
        data_fim: filters.data_fim,
        status_processo: filters.status_processo || undefined,
        centro_custo_id: filters.centro_custo_id || undefined
      });
    }
  };

  const clearFilters = () => {
    // Reset to initial values if provided, or empty
    setFilters({
      data_inicio: initialFilters?.data_inicio || '',
      data_fim: initialFilters?.data_fim || '',
      status_processo: '' as StatusProcesso | '',
      centro_custo_id: ''
    });
  };

  return (
    <div className="bg-[var(--color-bg-paper)] p-4 rounded-lg shadow-sm border border-[var(--color-border)] mb-6 transition-colors duration-300">
      <div className="flex items-center justify-between mb-4">
        <h3 className="font-semibold text-[var(--color-text-main)] flex items-center gap-2">
          <Filter size={20} />
          Filtros de Análise
        </h3>
        <button 
          onClick={() => setIsOpen(!isOpen)}
          className="text-[var(--color-primary)] text-sm hover:underline md:hidden"
        >
          {isOpen ? 'Ocultar' : 'Expandir'}
        </button>
      </div>

      <div className={`grid grid-cols-1 md:grid-cols-5 gap-4 items-end ${isOpen ? 'block' : 'hidden md:grid'}`}>
        <div>
          <label className="block text-sm font-medium text-[var(--color-text-muted)] mb-1">Período (Início)</label>
          <input
            type="date"
            className="w-full rounded-md border-[var(--color-border)] shadow-sm focus:border-[var(--color-primary)] focus:ring-[var(--color-primary)] border p-2 bg-[var(--color-bg-main)] text-[var(--color-text-main)]"
            value={filters.data_inicio}
            onChange={e => setFilters({ ...filters, data_inicio: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--color-text-muted)] mb-1">Período (Fim)</label>
          <input
            type="date"
            className="w-full rounded-md border-[var(--color-border)] shadow-sm focus:border-[var(--color-primary)] focus:ring-[var(--color-primary)] border p-2 bg-[var(--color-bg-main)] text-[var(--color-text-main)]"
            value={filters.data_fim}
            onChange={e => setFilters({ ...filters, data_fim: e.target.value })}
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--color-text-muted)] mb-1">Status do Processo</label>
          <select
            className="w-full rounded-md border-[var(--color-border)] shadow-sm focus:border-[var(--color-primary)] focus:ring-[var(--color-primary)] border p-2 bg-[var(--color-bg-main)] text-[var(--color-text-main)]"
            value={filters.status_processo}
            onChange={e => setFilters({ ...filters, status_processo: e.target.value as StatusProcesso })}
          >
            <option value="">Todos</option>
            <option value={StatusProcesso.ATIVO}>Ativo</option>
            <option value={StatusProcesso.SUSPENSO}>Suspenso</option>
            <option value={StatusProcesso.ENCERRADO}>Encerrado</option>
            <option value={StatusProcesso.TRANSITO_JULGADO}>Trânsito em Julgado</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-[var(--color-text-muted)] mb-1">Centro de Custo</label>
          <select
            className="w-full rounded-md border-[var(--color-border)] shadow-sm focus:border-[var(--color-primary)] focus:ring-[var(--color-primary)] border p-2 bg-[var(--color-bg-main)] text-[var(--color-text-main)]"
            value={filters.centro_custo_id}
            onChange={e => setFilters({ ...filters, centro_custo_id: e.target.value })}
          >
            <option value="">Todos</option>
            {centrosCusto?.map(cc => (
              <option key={cc.id} value={cc.id}>{cc.nome}</option>
            ))}
          </select>
        </div>

        <div className="flex gap-2">
          <button
            onClick={handleSearch}
            className="flex-1 bg-[var(--color-primary)] text-[var(--color-primary-foreground)] px-4 py-2 rounded-md hover:bg-[var(--color-primary-hover)] flex items-center justify-center gap-2 transition-colors"
          >
            <Search size={16} />
            Filtrar
          </button>
          
          <button
            onClick={clearFilters}
            className="px-3 py-2 text-[var(--color-text-muted)] hover:text-[var(--color-text-main)] border border-[var(--color-border)] rounded-md hover:bg-[var(--color-bg-main)] transition-colors"
            title="Limpar Filtros"
          >
            <X size={16} />
          </button>
        </div>
      </div>
    </div>
  );
};

