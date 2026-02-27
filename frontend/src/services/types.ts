export interface User {
  id: string;
  email: string;
  role: 'ADMIN' | 'ANALISTA' | 'ADVOGADO';
  is_2fa_enabled: boolean;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  requires_2fa?: boolean;
  temp_token?: string; // If 2FA is required
}

export interface UserProfile extends User {}

export enum StatusProcesso {
  ATIVO = 'ATIVO',
  SUSPENSO = 'SUSPENSO',
  ENCERRADO = 'ENCERRADO',
  TRANSITO_JULGADO = 'TRANSITO_JULGADO',
}

export interface Participante {
  id: string;
  nome: string;
  documento?: string;
  email?: string;
  tipo: 'CLIENTE' | 'FORNECEDOR' | 'AMBOS';
  telefone?: string;
}

export interface Processo {
  id: string;
  numero: string;
  numero_cnj?: string;
  titulo_causa?: string;
  descricao?: string;
  percentual_exito?: number | string;
  valor_pro_labore?: number | string;
  valor_causa_atualizado?: number | string;
  valor_causa_estimado?: number | string;
  status: StatusProcesso;
  cliente_id: string;
  cliente?: Participante;
}

export interface ProcessoCreate extends Omit<Processo, 'id' | 'cliente'> {
  // id is not present on creation
}

export interface ProcessoUpdate extends Partial<ProcessoCreate> {}

export enum TipoLancamento {
  RECEITA = 'RECEITA',
  DESPESA = 'DESPESA',
}

export enum NaturezaLancamento {
  FIXO = 'FIXO',
  PONTUAL = 'PONTUAL',
  EXITO = 'EXITO',
}

export enum StatusLancamento {
  PENDENTE = 'PENDENTE',
  PAGO = 'PAGO',
  AGUARDANDO_TRANSITO = 'AGUARDANDO_TRANSITO',
  CANCELADO = 'CANCELADO',
}

export interface CentroCusto {
  id: string;
  nome: string;
  codigo?: string;
  descricao?: string;
  tipo?: TipoLancamento;
  parent_id?: string;
  children?: CentroCusto[];
}

export interface DashboardCards {
  saldo_atual: number;
  burn_rate: number;
  ticket_medio_exito: number;
  pipeline_recebiveis: number;
}

export interface CashFlowPoint {
  date: string;
  entradas: number;
  saidas: number;
}

export interface ProjectedFlowPoint {
  date: string;
  realizado: number;
  projetado: number;
}

export interface ExpenseCategory {
  name: string;
  value: number;
}

export interface DashboardData {
  cards: DashboardCards;
  cash_flow: CashFlowPoint[];
  projected_flow: ProjectedFlowPoint[];
  expenses_by_category: ExpenseCategory[];
}

export interface CartaoCredito {
  id: string;
  nome: string;
  final_cartao?: string;
}

export interface Lancamento {
  id: string;
  descricao: string;
  valor: number | string;
  valor_realizado?: number | string;
  valor_previsto?: number | string;
  data_vencimento?: string;
  data_pagamento?: string;
  tipo: TipoLancamento;
  natureza: NaturezaLancamento;
  status: StatusLancamento;
  participante_id: string;
  participante?: Participante;
  processo_id?: string;
  processo?: Processo;
  cartao_id?: string;
  cartao?: CartaoCredito;
  centro_custo_id: string;
  centro_custo?: CentroCusto;
  reembolsavel: boolean;
  lancamento_pai_id?: string;
}

export interface LancamentoCreate extends Omit<Lancamento, 'id' | 'participante' | 'processo' | 'cartao' | 'centro_custo'> {}

export interface LancamentoUpdate extends Partial<LancamentoCreate> {}

export interface OfxTransaction {
  id: string;
  data: string;
  valor: number;
  descricao: string;
}

export interface ConciliacaoResult {
  ofx_id: string;
  lancamento_id?: string;
  tipo_match: string;
  valor_taxa_sugerida?: number;
  mensagem: string;
}


