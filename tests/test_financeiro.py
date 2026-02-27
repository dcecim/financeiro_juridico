
import pytest
import uuid
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy.exc import IntegrityError
from app.models.lancamento import Lancamento, NaturezaLancamento, TipoLancamento, StatusLancamento
from app.models.processo import Processo
from app.models.participante import Participante, TipoParticipante
from app.services.conciliacao import ConciliacaoService
from app.schemas.ofx import OfxTransactionSchema

@pytest.mark.asyncio
async def test_criar_lancamento_exito_sem_processo(db_session):
    # Cria um participante para vincular
    cliente = Participante(
        nome="Cliente Teste", 
        documento="12345678900", 
        tipo=TipoParticipante.CLIENTE
    )
    db_session.add(cliente)
    await db_session.flush()

    # Tenta criar um lançamento de êxito SEM processo vinculado
    # A validação deve ocorrer no nível da aplicação ou banco.
    # Como não adicionamos validação explícita no modelo ainda, vamos adicionar um validador no modelo Lancamento
    # ou assumir que o teste espera falha.
    # Vou adicionar o validador no modelo em um passo separado, mas aqui assumo que ele lançará ValueError.
    
    lancamento = Lancamento(
        descricao="Honorários Êxito",
        valor=Decimal("10000.00"),
        tipo=TipoLancamento.RECEITA,
        natureza=NaturezaLancamento.EXITO, # Êxito
        status=StatusLancamento.AGUARDANDO_TRANSITO,
        participante_id=cliente.id,
        processo_id=None # ERRO: Deve exigir processo
    )
    
    db_session.add(lancamento)
    
    # Expect IntegrityError due to CheckConstraint or Database Constraint
    try:
        await db_session.commit()
        # If we reach here, validation failed
        pytest.fail("Deveria ter falhado ao criar honorário de êxito sem processo")
    except IntegrityError:
        # Expected behavior
        await db_session.rollback()
    except Exception as e:
        # Check if it's related to the constraint
        if "constraint" in str(e).lower() or "check" in str(e).lower():
            await db_session.rollback()
        else:
            raise e

@pytest.mark.asyncio
async def test_conciliacao_matching_taxa(db_session):
    service = ConciliacaoService(db_session)
    
    # Setup: Lançamento pendente de R$ 100,00
    cliente = Participante(nome="Cliente A", documento="111", tipo=TipoParticipante.CLIENTE)
    db_session.add(cliente)
    await db_session.flush()
    
    lancamento = Lancamento(
        descricao="Mensalidade",
        valor=Decimal("100.00"),
        tipo=TipoLancamento.RECEITA,
        natureza=NaturezaLancamento.FIXO,
        status=StatusLancamento.PENDENTE,
        data_vencimento=date.today(),
        participante_id=cliente.id
    )
    db_session.add(lancamento)
    await db_session.commit()
    await db_session.refresh(lancamento)
    
    # Execução: OFX de R$ 106.38 (Valor recebido ou pago?)
    # Se for RECEITA, geralmente recebe-se MENOS (desconto taxa). Se entrou 106, talvez seja juros?
    # O user disse: "sugerir lançamento automático em 'Impostos/Taxas'".
    # Vamos assumir que entrou 106.38 (talvez juros) ou entrou 93.62 (taxa).
    # O exemplo do user: "pendente de R$ 100,00 e uma transação de extrato (OFX) de R$ 106,38"
    # Diferença de 6.38. 6.38/100 = 6.38% (< 10%).
    
    ofx_tx = OfxTransactionSchema(
        id="ofx-1",
        data=date.today(),
        valor=Decimal("106.38"),
        descricao="Depósito via Boleto"
    )
    
    resultados = await service.processar_ofx([ofx_tx])
    
    # Verificação
    assert len(resultados) == 1
    res = resultados[0]
    
    assert res.tipo_match == "PARTIAL"
    assert res.lancamento_id == str(lancamento.id)
    # A diferença é 6.38
    assert abs(res.valor_taxa_sugerida - Decimal("6.38")) < Decimal("0.01")
    assert "Sugestão de lançamento de taxa/imposto" in res.mensagem

@pytest.mark.asyncio
async def test_integridade_participante(db_session):
    # Setup
    cliente = Participante(nome="Cliente B", documento="222", tipo=TipoParticipante.CLIENTE)
    db_session.add(cliente)
    await db_session.flush()
    
    processo = Processo(numero="001", cliente_id=cliente.id)
    db_session.add(processo)
    await db_session.commit()
    
    # Tenta deletar participante com processo vinculado
    # SQLAlchemy relationship cascade padrão é set null ou raise?
    # No modelo definimos: processos = relationship(..., cascade="all, delete-orphan")
    # Se deletar o participante, vai deletar os processos (cascade).
    # O requisito diz: "Valide que NÃO é possível deletar".
    # Então precisamos mudar o comportamento do cascade ou configurar o banco para RESTRICT.
    # No modelo atual: cascade="all, delete-orphan" SIGNIFICA que VAI deletar.
    # O usuário pediu para validar que NÃO é possível.
    # Eu terei que alterar o modelo para remover o cascade delete ou usar passive_deletes='all' com foreign key ondelete='RESTRICT'.
    # Como estou usando SQLite e SQLAlchemy, o cascade padrão do python vai deletar.
    # Vou ajustar o teste para verificar se o cascade está configurado (se deletar, falha o teste de integridade desejado).
    # E depois ajustarei o modelo se necessário.
    
    try:
        await db_session.delete(cliente)
        await db_session.commit()
        pytest.fail("Deveria falhar ao deletar participante com processos vinculados")
    except IntegrityError:
        # Expected
        await db_session.rollback()
    except AssertionError:
         # SQLAlchemy might raise this if it detects non-nullable FK violation in memory before flush?
         # Or if we removed cascade, it might raise IntegrityError on flush.
         await db_session.rollback()
