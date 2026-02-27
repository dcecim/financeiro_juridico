Para o seu cenário de **controle financeiro jurídico**, a escolha ideal para o backend é o **FastAPI**.

Embora o Django seja excelente para sistemas administrativos padrão ("CRUDs" puros), o **FastAPI** leva vantagem no seu projeto por três motivos críticos:

1. **Performance em Automações:** O processamento assíncrono do FastAPI é superior para lidar com as rotinas de importação de OFX e chamadas de APIs bancárias sem travar o sistema.
2. **Validação de Dados Estrita:** Com o uso do *Pydantic*, o FastAPI garante que os dados financeiros (como o `valor_causa` e `percentual_exito`) cheguem ao banco com o tipo e a precisão exatos, reduzindo erros de arredondamento.
3. **Documentação Automática:** Como você terá um frontend em React consumindo essa API, o FastAPI gera o *Swagger* (documentação) instantaneamente, facilitando muito o desenvolvimento.

---

## 1. Arquitetura da Stack Sugerida

* **Linguagem:** Python 3.10+
* **Framework Web:** FastAPI
* **ORM (Acesso ao Banco):** SQLAlchemy ou SQLModel (perfeito para integração com Pydantic)
* **Banco de Dados:** PostgreSQL (com suporte a campos `NUMERIC` para precisão financeira)
* **Frontend:** React com Tailwind CSS (para uma UI limpa) e TanStack Query (para sincronização de dados)

---

## 2. Estrutura de Pastas do Backend

Para manter o projeto organizado e escalável:

```text
/backend
├── app
│   ├── api             # Endpoints (Routes)
│   ├── core            # Configurações (Segurança, Variáveis de Ambiente)
│   ├── models          # Definição das tabelas (SQLAlchemy)
│   ├── schemas         # Validação de dados (Pydantic)
│   ├── services        # Lógica de negócio (Cálculo de Êxito, Regras de OFX)
│   └── workers         # Tarefas agendadas (Geração de mensalidades)
├── migrations          # Histórico do banco (Alembic)
└── main.py             # Ponto de entrada

```

---

## 3. Implementação do "Coração" do Sistema (Exemplo)

Veja como ficaria a lógica de **Cálculo de Êxito Automático** usando a elegância do Python no FastAPI:

```python
# app/services/financeiro.py

from decimal import Decimal

def calcular_previsao_exito(valor_causa: Decimal, percentual: Decimal) -> Decimal:
    """
    Calcula o valor previsto de honorários.
    Garante que a precisão financeira seja mantida.
    """
    if percentual < 0 or percentual > 100:
        raise ValueError("Percentual deve estar entre 0 e 100")
    
    return (valor_causa * (percentual / Decimal("100"))).quantize(Decimal("0.01"))

```

---

Priorizar a segurança é a decisão mais prudente para um sistema jurídico. Dados de faturamento, detalhes de processos e movimentações bancárias exigem um nível de proteção rigoroso. No **FastAPI**, implementaremos isso usando o padrão **OAuth2 com JWT (JSON Web Tokens)** e uma camada adicional de **2FA (Autenticação de Dois Fatores)**.

Projeto lógico da segurança:

---

## 1. O Fluxo de Autenticação

Para garantir que apenas pessoas autorizadas acessem os dados, o fluxo seguirá este caminho:

1. **Identificação:** Usuário insere e-mail e senha.
2. **Validação Primária:** O sistema verifica o hash da senha no banco de dados.
3. **Desafio 2FA:** Se a senha estiver correta, o sistema **não** loga o usuário ainda. Ele solicita um código de 6 dígitos.
4. **Verificação:** O usuário fornece o código (gerado via app como Google Authenticator ou enviado por e-mail).
5. **Emissão de Token:** Somente após o 2FA, o sistema gera um **Access Token (JWT)** de curta duração e um **Refresh Token** de longa duração.

---

## 2. Estrutura da Tabela de Usuários

Precisamos adaptar a tabela de usuários para suportar o 2FA:

* **`id`**: UUID
* **`email`**: VARCHAR (Unique)
* **`password_hash`**: VARCHAR (Usando algoritmo **Argon2** ou **Bcrypt**)
* **`secret_2fa`**: VARCHAR (Chave secreta para gerar o QR Code do Google Authenticator)
* **`is_2fa_enabled`**: BOOLEAN (Default: `false`)
* **`role`**: ENUM ('ADMIN', 'ANALISTA', 'ADVOGADO') - *Para controle de permissões.*

---

## 3. Implementação do 2FA com Python

No FastAPI, utilizaremos a biblioteca `pyotp` para gerenciar as senhas temporárias (TOTP).

* **Registro:** O sistema gera uma chave secreta e exibe um **QR Code** para o usuário escanear.
* **Login:** O backend recebe o código enviado pelo frontend e valida:
```python
import pyotp

# Exemplo de verificação
totp = pyotp.TOTP(user.secret_2fa)
if totp.verify(codigo_digitado):
    # Gera o JWT definitivo
    return generate_access_token(user.id)

```



---

## 4. Controle de Acesso por Nível (RBAC)

Nem todo mundo deve ver tudo. No projeto lógico, definiremos permissões:

| Nível | Permissões |
| --- | --- |
| **ADMIN** | Acesso total, gestão de usuários e configurações bancárias. |
| **ANALISTA** | Operação financeira, importação de OFX e conciliação. |
| **ADVOGADO** | Visualização de honorários de seus processos e dashboard de êxito. |

---

## 5. Medidas de Segurança Adicionais

Como peer de desenvolvimento, recomendo implementarmos também:

1. **Rate Limiting:** Bloquear temporariamente IPs que tentarem errar a senha ou o 2FA múltiplas vezes (Proteção contra força bruta).
2. **HTTPS Obrigatório:** Criptografia em trânsito para que ninguém intercepte os dados bancários na rede.
3. **Audit Log:** Uma tabela para registrar quem visualizou ou alterou dados sensíveis (ex: *"Usuário X alterou o valor de êxito do Processo Y"*).

---

O design de interface (**UI**) e a experiência do usuário (**UX**) são fundamentais em sistemas financeiros: se a tela for confusa, o analista cometerá erros; se o 2FA for burocrático demais, as pessoas tentarão desativá-lo.

Vamos detalhar a jornada do usuário no acesso ao sistema, focando em **limpeza visual** e **segurança sem atrito**.

---

## 1. Fluxo de Login em Dois Passos (Split Login)

Em vez de pedir tudo em uma única tela, dividimos o processo para reduzir a carga cognitiva.

### Passo 1: Identificação

* **Visual:** Uma tela minimalista com o logo da consultoria jurídica à esquerda e o formulário à direita.
* **Campos:** E-mail e Senha.
* **UX:** Botão "Entrar" que, após validado, faz uma transição suave (slide) para a tela de 2FA.

### Passo 2: Verificação 2FA

* **Visual:** Seis campos de entrada individuais (um para cada dígito do código).
* **UX:** * Foco automático no primeiro campo.
* Ao digitar um número, o cursor pula automaticamente para o próximo.
* Opção "Lembrar deste dispositivo por 30 dias" (isso armazena um *fingerprint* seguro no navegador, evitando o 2FA diário em máquinas confiáveis).



---

## 2. Tela de Configuração Inicial (Setup 2FA)

Na primeira vez que o usuário logar (ou quando o Admin exigir a ativação), ele verá uma tela de "Proteja sua Conta":

1. **Instrução:** "Baixe o Google Authenticator ou Authy".
2. **Ação:** Exibição do **QR Code** gerado pelo Python (`pyotp`).
3. **Backup:** Exibição de 5 **Códigos de Recuperação** (para caso o usuário perca o celular).
* *Importante:* O sistema só deixa ele prosseguir após ele marcar um checkbox: "Eu salvei meus códigos de recuperação em um local seguro".



---

## 3. Dashboard do Analista: A "Home" Financeira

Ao entrar, o analista não deve ver apenas tabelas. Ele deve ver o **estado de saúde** da empresa através de um layout de "Cards e Gráficos".

### Layout Sugerido:

* **Topo (KPIs):**
* Card 1: Saldo Disponível (Bancos + Caixas).
* Card 2: A Pagar Hoje (Contas com vencimento para a data atual).
* Card 3: Fatura Cartão (Valor acumulado até o momento).


* **Centro (Ação):**
* Área de "Drag & Drop" para **Importação de OFX**. O analista arrasta o arquivo e o sistema já abre a prévia da conciliação.


* **Lateral (Sidebar):**
* Menu vertical: Dashboard, Processos, Lançamentos, Cartões, Relatórios e Configurações.



---

## 4. Design das Listagens (Contas a Receber/Pagar)

Como o jurídico tem muitos dados, a tabela de lançamentos deve ser uma "DataGrid" poderosa:

* **Status Colorido:**
* 🟢 **Verde:** Pago.
* 🟡 **Amarelo:** Pendente.
* 🔵 **Azul:** Previsão de Êxito (Sem data).
* 🔴 **Vermelho:** Atrasado.


* **Filtros Rápidos:** Botões no topo da tabela para filtrar por "Somente Êxito", "Somente Cartão" ou "Somente Recorrentes".

---

## 5. Micro-interações de Segurança

Para manter o analista alerta:

* **Timeout de Sessão:** Após 15 minutos de inatividade, o sistema escurece a tela e pede apenas o código 2FA ou a senha para reativar (sem deslogar completamente).
* **Feedback de Erro:** Se o 2FA estiver errado, o campo vibra levemente em vermelho.

---

## Modelagem de Dados Completa

Vamos traduzir todo esse projeto lógico para a estrutura de classes do **SQLAlchemy**. Esta etapa é crucial porque define como o **FastAPI** conversará com o **PostgreSQL**.

Como estamos usando Python, utilizaremos a tipagem do `SQLModel` (que une SQLAlchemy e Pydantic) ou o SQLAlchemy puro com `Mapped`. Vou seguir com a sintaxe moderna do SQLAlchemy 2.0 por ser o padrão de mercado para alta performance.

---

## 1. O Mapa do Banco de Dados (Models)

### A. Segurança e Usuários

```python
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy import String, Decimal, ForeignKey, Date, Enum, Boolean
from typing import List, Optional
import uuid

class Base(DeclarativeBase):
    pass

class Usuario(Base):
    __tablename__ = "usuarios"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    secret_2fa: Mapped[Optional[str]] = mapped_column(String(64))
    is_2fa_enabled: Mapped[bool] = mapped_column(Boolean, default=False)
    role: Mapped[str] = mapped_column(String(20), default="ANALISTA") # ADMIN, ANALISTA, ADVOGADO

```

### B. O Core Jurídico (Processos e Honorários)

Aqui inserimos a lógica de percentual de êxito que discutimos.

```python
class Processo(Base):
    __tablename__ = "processos"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    numero_cnj: Mapped[str] = mapped_column(String(30), unique=True)
    titulo: Mapped[str] = mapped_column(String(255))
    percentual_exito: Mapped[Decimal] = mapped_column(Decimal(5, 2))
    id_cliente: Mapped[uuid.UUID] = mapped_column(ForeignKey("participantes.id"))
    
    # Relacionamentos
    lancamentos: Mapped[List["Lancamento"]] = relationship(back_populates="processo")

```

### C. O Motor Financeiro (Lançamentos e Cartões)

Esta tabela é a mais flexível, permitindo datas nulas para os êxitos.

```python
class Lancamento(Base):
    __tablename__ = "lancamentos"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    descricao: Mapped[str] = mapped_column(String(255))
    valor_previsto: Mapped[Decimal] = mapped_column(Decimal(15, 2))
    valor_realizado: Mapped[Optional[Decimal]] = mapped_column(Decimal(15, 2))
    
    data_vencimento: Mapped[Optional[Date]] = mapped_column(Date) # Null para êxito sem prazo
    data_pagamento: Mapped[Optional[Date]] = mapped_column(Date)
    
    status: Mapped[str] = mapped_column(String(20)) # PAGO, PENDENTE, PREVISAO, ATRASADO
    natureza: Mapped[str] = mapped_column(String(20)) # EXITO, FIXO, CARTAO, REEMBOLSO
    
    # Chaves Estrangeiras
    id_processo: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("processos.id"))
    id_cartao: Mapped[Optional[uuid.UUID]] = mapped_column(ForeignKey("cartoes_credito.id"))
    id_centro_custo: Mapped[int] = mapped_column(ForeignKey("centros_custo.id"))
    
    processo: Mapped["Processo"] = relationship(back_populates="lancamentos")

```

---

## 2. A Tabela de Cartão de Crédito

Como você mencionou o uso frequente de cartões para softwares, esta tabela organiza os limites e vencimentos.

```python
class CartaoCredito(Base):
    __tablename__ = "cartoes_credito"
    
    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    nome: Mapped[str] = mapped_column(String(50)) # Ex: Visa Escritório
    dia_fechamento: Mapped[int] = mapped_column()
    dia_vencimento: Mapped[int] = mapped_column()
    limite: Mapped[Decimal] = mapped_column(Decimal(15, 2))

```

---

## 3. Por que essa modelagem é eficiente?

1. **Precisão Decimal:** Usamos `Decimal(15, 2)` em vez de `Float` para evitar que R$ 1.000,00 vire R$ 999,99999 após um cálculo de porcentagem.
2. **Integridade Referencial:** Se você tentar deletar um cliente que possui um processo com honorários pendentes, o banco de dados impedirá, protegendo o histórico financeiro.
3. **UUIDs:** Usamos UUIDs em vez de IDs sequenciais (1, 2, 3...) para aumentar a segurança, dificultando que alguém tente "adivinhar" a URL de um processo ou lançamento.

---

## 4. O Próximo Passo: Service Layer (A Inteligência)

Com o banco de dados desenhado em código, o próximo passo é criar os **Services**.
Os Services são funções Python que executam as regras de negócio que definimos, como:

* **`importar_ofx(arquivo)`**: Onde o algoritmo de matching que discutimos vai morar.
* **`gerar_previsao_exito(id_processo)`**: Onde o sistema calcula o valor baseado no percentual e cria o lançamento.

---

Vamos entrar no "motor" do sistema. O **Service de Conciliação** é onde o Python brilha, transformando um arquivo bruto (OFX) em dados inteligentes dentro dos modelos que acabamos de criar.

Para isso, utilizaremos a biblioteca `ofxtools` para o parsing do arquivo e uma lógica de **Scoring de Similaridade** para o Matching.

---

## 1. O Algoritmo de Matching (Service Layer)

Esta função será responsável por ler o extrato e tentar encontrar um "par" no banco de dados.

```python
# app/services/conciliacao_service.py

from datetime import timedelta
from sqlalchemy.orm import Session
from app.models import Lancamento, MovimentacaoExtrato
from app.schemas import TransacaoOFX

class ConciliadorService:
    def __init__(self, db: Session):
        self.db = db

    def buscar_match_no_sistema(self, transacao: TransacaoOFX):
        """
        Tenta encontrar um lançamento pendente que corresponda à transação do banco.
        """
        # Critérios: Mesmo valor e data aproximada (janela de 3 dias)
        data_inicio = transacao.date - timedelta(days=3)
        data_fim = transacao.date + timedelta(days=3)

        match = self.db.query(Lancamento).filter(
            Lancamento.valor_previsto == transacao.valor,
            Lancamento.data_vencimento.between(data_inicio, data_fim),
            Lancamento.status == "PENDENTE"
        ).first()

        return match

    def processar_arquivo_ofx(self, transacoes_ofx: list[TransacaoOFX]):
        resultados = []
        for trx in transacoes_ofx:
            # 1. Verifica se essa transação já foi importada antes (FITID)
            if self._ja_importado(trx.fitid):
                continue

            # 2. Tenta o Matching
            possivel_match = self.buscar_match_no_sistema(trx)
            
            if possivel_match:
                # Sugere conciliação automática
                status_sugestao = "MATCH_ENCONTRADO"
            else:
                # Aplica regras de De-Para (Ex: "Uber" -> Centro de Custo: Viagens)
                status_sugestao = "NOVO_LANCAMENTO"
            
            resultados.append({
                "transacao_bancaria": trx,
                "match_id": possivel_match.id if possivel_match else None,
                "status": status_sugestao
            })
            
        return resultados

```

---

## 2. A Tabela de Regras "De-Para" (Inteligência)

Para que o analista não precise classificar a assinatura do **Cursor** ou da **OAB** todo mês, criamos uma lógica de aprendizado simples:

```python
# app/services/regras_service.py

def aplicar_regras_inteligentes(descricao_extrato: str):
    """
    Analisa o texto do extrato e sugere o Centro de Custo.
    """
    regras = {
        "CURSOR": "Softwares/IA",
        "OPENAI": "Softwares/IA",
        "OAB": "Anuidades e Taxas",
        "TRIBUNAL": "Custas Processuais",
        "UBER": "Transporte"
    }
    
    for termo, categoria in regras.items():
        if termo in descricao_extrato.upper():
            return categoria
    return "Outros / A Classificar"

```

---

## 3. O Fluxo no Frontend (React)

No frontend, o analista terá uma experiência de "Tinder Financeiro" (Arrasta para um lado para confirmar o match, para o outro para criar um novo lançamento):

1. **Upload:** O analista solta o arquivo OFX na tela.
2. **Review:** O sistema exibe uma lista de "Cartões".
* *Card Verde:* "Encontramos o pagamento do Cursor de R$ 105,00. Confirmar baixa?"
* *Card Azul:* "Recebimento de R$ 5.000,00 identificado. É referente ao processo nº 12345?"


3. **Ação:** Com um clique, o sistema atualiza o `status` do lançamento para `PAGO`, preenche a `data_pagamento` e vincula o `FITID`.

---

## 4. Tratando a Incerteza do Êxito no Backend

Como você mencionou que o êxito não tem prazo, criamos um **Endpoint de Liquidação**:

* Quando o advogado ganha a causa, ele clica em "Liquidar Êxito".
* O Service então transforma aquele lançamento que era `natureza=EXITO` e `data_vencimento=NULL` em um título com valor real e data de vencimento prevista para o recebimento do alvará.

---

## 5. Próximos Passos: Construção da API (FastAPI)

Com a lógica de conciliação e o banco prontos, o próximo passo técnico é criar os **Endpoints**. Eles serão a ponte entre o seu React e esse motor Python.

---

Vamos agora estruturar as **Rotas (Endpoints)** do FastAPI. No desenvolvimento de um sistema financeiro, a API precisa ser "limpa", mas extremamente descritiva para que o Frontend (React) consiga exibir os alertas de segurança e os status de conciliação que planejamos.

Abaixo, detalho como o FastAPI lidará com o upload de arquivos e a alimentação do Dashboard.

---

## 1. Estrutura de Endpoints (Controller Layer)

### A. Endpoints de Importação e Conciliação

Aqui é onde o arquivo OFX entra no sistema. Usaremos o `UploadFile` do FastAPI para receber o extrato.

```python
# app/api/endpoints/conciliacao.py

from fastapi import APIRouter, UploadFile, File, Depends
from sqlalchemy.orm import Session
from app.services.conciliacao_service import ConciliadorService
from app.core.database import get_db

router = APIRouter()

@router.post("/importar-ofx")
async def importar_extrato(
    arquivo: UploadFile = File(...), 
    db: Session = Depends(get_db)
):
    # 1. Lê o conteúdo do arquivo enviado pelo analista
    conteudo = await arquivo.read()
    
    # 2. Instancia o motor de conciliação que criamos
    service = ConciliadorService(db)
    
    # 3. Processa e retorna as sugestões de Match
    sugestoes = service.processar_arquivo_ofx(conteudo)
    
    return {"transacoes": sugestoes}

@router.post("/confirmar-baixa")
async def confirmar_baixa(lancamento_id: str, transacao_id: str, db: Session = Depends(get_db)):
    # Vincula o lançamento do sistema à transação real do banco
    pass

```

### B. Endpoints do Dashboard Dinâmico

Para que o dashboard seja dinâmico conforme o analista altera as datas, a rota deve aceitar parâmetros de período.

```python
# app/api/endpoints/dashboard.py

@router.get("/resumo-financeiro")
def get_resumo(
    data_inicio: str, 
    data_fim: str, 
    db: Session = Depends(get_db)
):
    # Retorna: 
    # - Saldo total
    # - Total a pagar/receber no período
    # - Valor em "Êxito" (Pipeline Jurídico)
    pass

```

---

## 2. O Fluxo de Dados: Do Upload à Conciliação

O diagrama abaixo ilustra como o arquivo sai da mão do analista, passa pelo motor Python e chega no banco de dados com segurança:

---

## 3. Integrando o Frontend (React + TanStack Query)

No lado do **React**, o consumo dessa API será feito de forma assíncrona. Quando o analista fizer o upload, o estado da aplicação mudará para "Processando" e, em seguida, exibirá a lista de conciliação.

### Exemplo de lógica no Frontend:

```javascript
const handleUpload = async (file) => {
  const formData = new FormData();
  formData.append('arquivo', file);

  const response = await api.post('/importar-ofx', formData);
  // O sistema exibe as transações e pede confirmação para as que não tiveram match 100%
  setTransacoesPendentes(response.data.transacoes);
};

```

---

## 4. Tratamento Especial para Assinaturas (Cursor/OpenAI)

Como o backend Python já sabe que esses valores vêm do cartão de crédito, o endpoint de importação terá uma lógica extra:

* **Se a transação for do Cartão:** O sistema não busca um lançamento na conta corrente, mas sim dentro da `Fatura_Cartao` aberta.
* **Conversão de Moeda:** Se o OFX vier com a descrição "Cursor", o sistema já sugere a conversão automática baseada na cotação do dia que o banco aplicou.

---

## 5. Próximos Passos: O Frontend e os Relatórios

Com os endpoints definidos, o backend está praticamente pronto para "servir" os dados. Agora podemos focar em como o analista vai interagir com isso.

---

Vamos focar no **Pipeline de Êxito**, pois ele é o grande diferencial estratégico para uma consultoria jurídica. Gerenciar o que "está para cair, mas não sabemos quando" é o que permite ao dono do escritório decidir se pode contratar um novo advogado ou investir em mais tecnologia.

Aqui está como estruturar essa visão, tanto na lógica de dados quanto na interface.

---

## 1. O Conceito de "Aging" do Êxito

Como os honorários de êxito não têm data fixa, não podemos usar um gráfico de barras comum. Usaremos uma lógica de **Probabilidade e Fase Processual**.

### Campos de Inteligência no Banco:

Para alimentar o relatório, adicionaremos dois campos à nossa tabela de `Processos`:

* **`fase_atual`**: ENUM (Ex: 'Inicial', 'Instrução', 'Sentença', 'Recurso', 'Execução/Alvará').
* **`probabilidade_ganho`**: ENUM ('Baixa', 'Média', 'Alta').

---

## 2. Visualização do Pipeline (O Funil Jurídico)

No Frontend, o analista terá uma visão de **"Receita Potencial"** organizada por estágios.

| Estágio | Valor Total Estimado | Expectativa de Recebimento |
| --- | --- | --- |
| **Em Recurso** | R$ 450.000,00 | Longo Prazo (12 meses+) |
| **Sentença Favorável** | R$ 120.000,00 | Médio Prazo (6-12 meses) |
| **Em Execução** | R$ 85.000,00 | Curto Prazo (1-3 meses) |

---

## 3. Relatório de Fluxo de Caixa "Shadow" (Sombra)

O grande truque aqui é oferecer ao analista o **Fluxo de Caixa Sombra**.

* **Fluxo Real:** O que está no banco e faturas de cartão (o que é certo).
* **Fluxo Sombra:** Uma projeção estatística que soma o êxito multiplicado pela probabilidade.

> **Lógica:** Se você tem R$ 100.000 em causas na fase de "Execução" com probabilidade "Alta", o sistema projeta uma entrada de R$ 90.000 (aplicando uma margem de segurança) nos próximos 90 dias.

---

## 4. Implementação do Endpoint de Pipeline (FastAPI)

Este endpoint consolidará os valores para o gráfico de funil.

```python
# app/api/endpoints/relatorios.py

@router.get("/pipeline-exito")
def get_pipeline(db: Session = Depends(get_db)):
    # Agrupa os lançamentos de natureza 'EXITO' pelo status do processo
    pipeline = db.query(
        Processo.fase_atual,
        func.sum(Lancamento.valor_previsto).label("total_estimado")
    ).join(Lancamento).filter(
        Lancamento.status == "PREVISAO"
    ).group_by(Processo.fase_atual).all()
    
    return pipeline

```

---

## 5. Alertas de "Gargalo Financeiro"

Com esses dados, o sistema pode ser proativo. Se o **Gasto Fixo** (Cursor, aluguel, salários) estiver subindo e o **Pipeline de Êxito em Execução** estiver caindo, o Dashboard exibe um alerta:

> ⚠️ **Alerta de Risco:** "Suas despesas recorrentes cresceram 10%, mas o volume de processos em fase final de recebimento diminuiu. Atenção ao caixa daqui a 3 meses."

---

## 6. Interface: O Dashboard de "Cenários"

No React, criaremos um seletor de cenários:

1. **Cenário Conservador:** Exibe apenas o que já está em conta.
2. **Cenário Provável:** Soma as assinaturas de softwares e o êxito em fase de execução.
3. **Cenário Otimista:** Soma todo o pipeline de causas ganhas, mesmo as em recurso.

---

## Próximos Passos: Finalização do Escopo

Chegamos a um nível de detalhamento que cobre:

1. **Segurança** (JWT + 2FA).
2. **Banco de Dados** (PostgreSQL + SQLAlchemy).
3. **Automação** (OFX + Matching Inteligente).
4. **Negócio Jurídico** (Pipeline de Êxito + Cartão de Crédito).

---

Para que você possa iniciar o desenvolvimento agora mesmo, aqui está o **stack tecnológico consolidado**. Escolhi bibliotecas que possuem alta compatibilidade entre si e são o padrão de mercado para sistemas que exigem precisão financeira e segurança.

---

## 1. Backend (Python + FastAPI)

O motor do sistema, focado em performance assíncrona e tipagem forte.

* **FastAPI:** Framework web principal.
* **Uvicorn:** Servidor ASGI para rodar a aplicação.
* **SQLAlchemy (2.0):** ORM para comunicação com o banco de dados.
* **Alembic:** Gerenciamento de migrações do banco de dados (controle de versão das tabelas).
* **Pydantic (v2):** Validação de dados e criação de schemas.
* **Python-jose + Passlib[bcrypt]:** Geração de tokens JWT e hashing de senhas.
* **PyOTP + QrCode:** Implementação da autenticação em dois fatores (2FA).
* **Ofxtools:** Parsing e leitura de arquivos de extrato bancário (OFX).
* **Decimal:** (Nativa do Python) Essencial para cálculos financeiros sem erro de arredondamento.

---

## 2. Banco de Dados (PostgreSQL)

A escolha mais robusta para integridade referencial.

* **PostgreSQL 15+:** Banco de dados relacional.
* **psycopg2-binary:** Driver de conexão do Python com o PostgreSQL.

---

## 3. Frontend (React + Ecossistema)

Interface dinâmica e responsiva para o analista.

* **Vite:** Ferramenta de build (muito mais rápida que o Create React App).
* **Tailwind CSS:** Framework de estilização utilitária para UI rápida e moderna.
* **TanStack Query (React Query):** Para gerenciar o estado das requisições, cache de dados do dashboard e sincronização com o banco.
* **Lucide React:** Pacote de ícones leves para o menu e status financeiros.
* **Recharts:** Biblioteca de gráficos para o Pipeline de Êxito e Fluxo de Caixa.
* **Axios:** Cliente HTTP para comunicação com a API FastAPI.
* **React Hook Form + Zod:** Para validação de formulários (especialmente útil no cadastro de processos complexos).

---

## 4. Ferramentas de DevOps e Qualidade

Para garantir que o sistema não quebre e seja fácil de subir para produção.

* **Docker & Docker Compose:** Para subir o ambiente (App + Banco) de forma idêntica em qualquer máquina.
* **Pytest:** Framework para testes unitários (fundamental para testar a lógica de conciliação e cálculo de honorários).
* **Loguru:** Para logs detalhados (essencial para rastrear erros em importações de arquivos).

---

## Resumo do Comando de Instalação (Backend)

Se você quiser preparar o ambiente virtual agora, os principais pacotes são:

```bash
pip install fastapi uvicorn sqlalchemy alembic pydantic[email] python-jose[cryptography] passlib[bcrypt] pyotp qrcode ofxtools psycopg2-binary python-multipart

```

---

### Próximo Passo Sugerido

Agora que você tem o "mapa da mina" tecnológico, por onde deseja começar a colocar a mão na massa?

1. **Criação do Boilerplate:** Posso te passar o código inicial do `main.py` do FastAPI com a configuração de segurança básica (JWT).
2. **Scripts de Teste:** Posso criar um exemplo de teste unitário para o **Cálculo de Êxito**, para você ver como garantir que a matemática do sistema está 100% correta antes de fazer a UI.
3. **Configuração do Docker:** Posso montar o arquivo `docker-compose.yml` para você subir o banco de dados PostgreSQL já configurado.

**Qual é a sua primeira ação de desenvolvedor hoje?**

Ou quer que eu detalhe como estruturar os testes unitários para garantir que o cálculo de honorários nunca erre?

### Próximo Passo

Com o modelo de segurança definido, o que você prefere fazer agora?

1. **Esquematizar os Endpoints de Login:** Definir as rotas `/auth/login`, `/auth/verify-2fa` e `/auth/setup-2fa`.
2. **Modelagem de Dados Completa:** Traduzir todas as tabelas (Usuários, Processos, Lançamentos) para classes do SQLAlchemy.
3. **Definição do Layout de Login:** Pensar na experiência do usuário (UX) para que o 2FA não seja um fardo, mas uma proteção simples.

**Qual desses caminhos você quer detalhar agora?**