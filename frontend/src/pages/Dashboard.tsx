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
import { useAuth } from '../contexts/AuthContext';
import { StatusProcesso } from '../services/types';

const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884d8'];

interface FilterState {
  data_inicio?: string;
  data_fim?: string;
  status_processo?: StatusProcesso;
  centro_custo_id?: string;
}

// Move Card outside to prevent re-creation on render
const Card = ({ title, value, icon: Icon, color, subtext }: any) => (
  <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
    <div className="flex justify-between items-start">
      <div>
        <p className="text-gray-500 text-sm font-medium">{title}</p>
        <h3 className={`text-2xl font-bold mt-2 ${color}`}>{value}</h3>
        {subtext && <p className="text-xs text-gray-400 mt-1">{subtext}</p>}
      </div>
      <div className={`p-3 rounded-lg bg-gray-50`}>
        <Icon className="w-6 h-6 text-gray-600" />
      </div>
    </div>
  </div>
);

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
  const { user } = useAuth();
  
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
          <h1 className="text-2xl font-bold text-gray-800">Dashboard Financeiro</h1>
          <p className="text-gray-500">Visão geral e indicadores de performance</p>
        </div>
        <div className="text-right text-sm text-gray-500">
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
        <div className="p-12 text-center text-gray-500">
          Atualizando dados...
        </div>
      ) : error ? (
        <div className="p-12 text-center text-red-500">
          Erro ao carregar dados. Tente novamente.
        </div>
      ) : isEmpty ? (
        <div className="p-12 text-center text-gray-500 bg-white rounded-lg shadow-sm">
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
              color="text-blue-600"
            />
            <Card 
              title="Burn Rate (Mensal)" 
              value={formatCurrency(dashboardData?.cards.burn_rate || 0)} 
              icon={TrendingDown} 
              color="text-red-600"
              subtext="Média de gastos fixos"
            />
            <Card 
              title="Ticket Médio de Êxito" 
              value={formatCurrency(dashboardData?.cards.ticket_medio_exito || 0)} 
              icon={TrendingUp} 
              color="text-green-600"
            />
            <Card 
              title="Pipeline de Recebíveis" 
              value={formatCurrency(dashboardData?.cards.pipeline_recebiveis || 0)} 
              icon={DollarSign} 
              color="text-purple-600"
              subtext="Estimado (Probabilidade > 70%)"
            />
          </div>

          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {/* Fluxo de Caixa (Barras Empilhadas) */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
              <h3 className="font-semibold text-gray-700 mb-4">Fluxo de Caixa (Entradas vs Saídas)</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <BarChart data={dashboardData?.cash_flow}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                    <Legend />
                    <Bar dataKey="entradas" name="Entradas" fill="#10B981" stackId="a" />
                    <Bar dataKey="saidas" name="Saídas" fill="#EF4444" stackId="a" />
                  </BarChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Fluxo Projetado (Linha) */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
              <h3 className="font-semibold text-gray-700 mb-4">Fluxo de Caixa Projetado vs Realizado</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart data={dashboardData?.projected_flow}>
                    <CartesianGrid strokeDasharray="3 3" />
                    <XAxis dataKey="date" />
                    <YAxis />
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                    <Legend />
                    <Line type="monotone" dataKey="realizado" name="Realizado" stroke="#3B82F6" strokeWidth={2} />
                    <Line type="monotone" dataKey="projetado" name="Projetado (Oportunidade)" stroke="#8B5CF6" strokeDasharray="5 5" strokeWidth={2} />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Despesas por Categoria (Rosca) */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100">
              <h3 className="font-semibold text-gray-700 mb-4">Composição de Despesas</h3>
              <div className="h-80">
                <ResponsiveContainer width="100%" height="100%">
                  <PieChart>
                    <Pie
                      data={dashboardData?.expenses_by_category}
                      cx="50%"
                      cy="50%"
                      labelLine={false}
                      label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                      outerRadius={80}
                      fill="#8884d8"
                      dataKey="value"
                    >
                      {dashboardData?.expenses_by_category?.map((entry: any, index: number) => (
                        <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                      ))}
                    </Pie>
                    <Tooltip formatter={(value: number) => formatCurrency(value)} />
                  </PieChart>
                </ResponsiveContainer>
              </div>
            </div>

            {/* Empty placeholder for symmetry or another chart */}
            <div className="bg-white p-6 rounded-lg shadow-sm border border-gray-100 flex items-center justify-center">
              <div className="text-center text-gray-400">
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
