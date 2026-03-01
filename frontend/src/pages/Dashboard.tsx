import { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { 
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer,
  LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import { 
  Wallet, TrendingDown, TrendingUp, AlertCircle, DollarSign
} from 'lucide-react';
import { dashboardService } from '../services/dashboard';
import { DashboardFilters } from '../components/DashboardFilters';
import { StatusProcesso } from '../services/types';

const COLORS = [
  'var(--color-primary)', 
  'var(--color-success)', 
  'var(--color-warning)', 
  'var(--color-danger)', 
  'var(--color-text-muted)'
];

interface FilterState {
  data_inicio?: string;
  data_fim?: string;
  status_processo?: StatusProcesso;
  centro_custo_id?: string;
}

// Move Card outside to prevent re-creation on render
const Card = ({ title, value, icon: Icon, color, subtext }: any) => {
  // Map legacy color classes to theme variables if possible, or use them as is if they are specific
  // For better theme adaptation, we override specific text colors with theme variables where appropriate
  // or rely on the theme system's primary/danger/success colors.
  
  // Helper to determine icon background opacity
  const iconBgClass = "bg-[var(--color-bg-main)]"; 
  
  return (
    <div className="bg-[var(--color-bg-paper)] p-6 rounded-lg shadow-sm border border-[var(--color-border)] transition-colors duration-300">
      <div className="flex justify-between items-start">
        <div>
          <p className="text-[var(--color-text-muted)] text-sm font-medium">{title}</p>
          <h3 className={`text-2xl font-bold mt-2 text-[var(--color-text-main)]`}>{value}</h3>
          {subtext && <p className="text-xs text-[var(--color-text-muted)] mt-1">{subtext}</p>}
        </div>
        <div className={`p-3 rounded-lg ${iconBgClass}`}>
          {/* We keep the color prop for the icon itself but ensure it works with the theme */}
          <Icon className={`w-6 h-6 ${color}`} />
        </div>
      </div>
    </div>
  );
};

// Function separate from component as requested
const fetchDashboardData = async (filters: FilterState) => {
  // Ensure dates are YYYY-MM-DD (sanity check)
  const cleanFilters = {
    ...filters,
    data_inicio: filters.data_inicio?.split('T')[0],
    data_fim: filters.data_fim?.split('T')[0]
  };
  
  console.log('fetchDashboardData called with:', cleanFilters);
  return dashboardService.getAnalytics(cleanFilters);
};

export const Dashboard = () => {
  // Initialize with default dates (Last 30 days) - Runs once on mount
  const [filters, setFilters] = useState<FilterState>(() => {
    const end = new Date();
    const start = new Date();
    start.setDate(end.getDate() - 30);
    return {
      data_inicio: start.toISOString().split('T')[0],
      data_fim: end.toISOString().split('T')[0]
    };
  });

  const { data: dashboardData, isLoading, error } = useQuery({
    queryKey: ['dashboard', filters],
    queryFn: () => fetchDashboardData(filters),
    enabled: !!filters.data_inicio && !!filters.data_fim // Only fetch if dates are valid
  });

  const formatCurrency = (value: number) => {
    return new Intl.NumberFormat('pt-BR', {
      style: 'currency',
      currency: 'BRL'
    }).format(value);
  };

  // Check for empty data
  const isEmpty = !isLoading && dashboardData && (
    (!dashboardData.cash_flow || dashboardData.cash_flow.length === 0) &&
    (!dashboardData.projected_flow || dashboardData.projected_flow.length === 0)
  );

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <div>
          <h1 className="text-2xl font-bold text-[var(--color-text-main)]">Dashboard Financeiro</h1>
          <p className="text-[var(--color-text-muted)]">Visão geral e indicadores de performance</p>
        </div>
        <div className="text-right text-sm text-[var(--color-text-muted)]">
          {new Date().toLocaleDateString('pt-BR', { weekday: 'long', year: 'numeric', month: 'long', day: 'numeric' })}
        </div>
      </div>

      <DashboardFilters 
        initialFilters={filters}
        onFilterChange={(newFilters) => {
          console.log('Filters updated:', newFilters);
          setFilters(newFilters);
        }} 
      />

      {isLoading ? (
        <div className="p-12 text-center text-[var(--color-text-muted)]">
          Atualizando dados...
        </div>
      ) : error ? (
        <div className="p-12 text-center text-[var(--color-danger)]">
          Erro ao carregar dados. Tente novamente.
        </div>
      ) : isEmpty ? (
        <div className="p-12 text-center text-[var(--color-text-muted)] bg-[var(--color-bg-paper)] rounded-lg shadow-sm border border-[var(--color-border)]">
           <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
           <p>Sem dados no período selecionado</p>
        </div>
      ) : (
        <>
          {/* Snapshot Widgets */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
            <Card 
              title="Saldo em Conta" 
              value={formatCurrency(dashboardData?.cards.saldo_atual || 0)} 
              icon={Wallet} 
              color="text-[var(--color-primary)]"
            />
            <Card 
              title="Burn Rate (Mensal)" 
              value={formatCurrency(dashboardData?.cards.burn_rate || 0)} 
              icon={TrendingDown} 
              color="text-[var(--color-danger)]"
              subtext="Média de gastos fixos"
            />
            <Card 
              title="Ticket Médio de Êxito" 
              value={formatCurrency(dashboardData?.cards.ticket_medio_exito || 0)} 
              icon={TrendingUp} 
              color="text-[var(--color-success)]"
            />
            <Card 
              title="Pipeline de Recebíveis" 
              value={formatCurrency(dashboardData?.cards.pipeline_recebiveis || 0)} 
              icon={DollarSign} 
              color="text-[var(--color-warning)]"
              subtext="Estimado (Probabilidade > 70%)"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Fluxo de Caixa (Barras Empilhadas) */}
            <div className="bg-[var(--color-bg-paper)] p-6 rounded-lg shadow-sm border border-[var(--color-border)] transition-colors duration-300">
              <h3 className="font-semibold text-[var(--color-text-main)] mb-4">Fluxo de Caixa (Entradas vs Saídas)</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dashboardData?.cash_flow}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="date" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip 
                      formatter={(value?: number) => [formatCurrency(value || 0), '']}
                      contentStyle={{ 
                        backgroundColor: 'var(--color-bg-paper)', 
                        borderColor: 'var(--color-border)', 
                        color: 'var(--color-text-main)' 
                      }}
                      itemStyle={{ color: 'var(--color-text-main)' }}
                      cursor={{ fill: 'var(--color-bg-main)', opacity: 0.5 }}
                    />
                    <Legend wrapperStyle={{ color: 'var(--color-text-muted)' }} />
                    <Bar dataKey="entradas" name="Entradas" fill="var(--color-success)" stackId="a" />
                    <Bar dataKey="saidas" name="Saídas" fill="var(--color-danger)" stackId="a" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Fluxo Projetado (Linha) */}
            <div className="bg-[var(--color-bg-paper)] p-6 rounded-lg shadow-sm border border-[var(--color-border)] transition-colors duration-300">
              <h3 className="font-semibold text-[var(--color-text-main)] mb-4">Fluxo de Caixa Projetado vs Realizado</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={dashboardData?.projected_flow}>
                    <CartesianGrid strokeDasharray="3 3" stroke="var(--color-border)" />
                    <XAxis dataKey="date" stroke="var(--color-text-muted)" />
                    <YAxis stroke="var(--color-text-muted)" />
                    <Tooltip 
                      formatter={(value?: number) => [formatCurrency(value || 0), '']}
                      contentStyle={{ 
                        backgroundColor: 'var(--color-bg-paper)', 
                        borderColor: 'var(--color-border)', 
                        color: 'var(--color-text-main)' 
                      }}
                      itemStyle={{ color: 'var(--color-text-main)' }}
                    />
                    <Legend />
                    <Line type="monotone" dataKey="realizado" name="Realizado" stroke="var(--color-primary)" strokeWidth={2} dot={{ fill: 'var(--color-primary)' }} />
                    <Line type="monotone" dataKey="projetado" name="Projetado (Oportunidade)" stroke="var(--color-text-muted)" strokeDasharray="5 5" strokeWidth={2} dot={{ fill: 'var(--color-text-muted)' }} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Despesas por Categoria (Rosca) */}
            <div className="bg-[var(--color-bg-paper)] p-6 rounded-lg shadow-sm border border-[var(--color-border)] transition-colors duration-300">
              <h3 className="font-semibold text-[var(--color-text-main)] mb-4">Composição de Despesas</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={dashboardData?.expenses_by_category}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }: { name?: string; percent?: number }) => `${name || ''} ${((percent || 0) * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="var(--color-primary)"
                      dataKey="value"
                      style={{ outline: 'none' }}
                    >
                      {dashboardData?.expenses_by_category?.map((_: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} stroke="var(--color-bg-paper)" />
                      ))}
                    </Pie>
                    <Tooltip 
                      formatter={(value?: number) => [formatCurrency(value || 0), '']}
                      contentStyle={{ 
                        backgroundColor: 'var(--color-bg-paper)', 
                        borderColor: 'var(--color-border)', 
                        color: 'var(--color-text-main)' 
                      }}
                      itemStyle={{ color: 'var(--color-text-main)' }}
                    />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Empty placeholder for symmetry or another chart */}
            <div className="bg-[var(--color-bg-paper)] p-6 rounded-lg shadow-sm border border-[var(--color-border)] flex items-center justify-center transition-colors duration-300">
              <div className="text-center text-[var(--color-text-muted)]">
                <AlertCircle className="w-12 h-12 mx-auto mb-2 opacity-50" />
                <p>Mais indicadores em breve</p>
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  );
};
