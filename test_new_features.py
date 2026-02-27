import asyncio
import sys
import uuid
from decimal import Decimal
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import select, delete

from app.core.database import engine
from app.models.processo import Processo, StatusProcesso
from app.models.participante import Participante, TipoParticipante
from app.models.lancamento import Lancamento, TipoLancamento, NaturezaLancamento, StatusLancamento
from app.models.cartao_credito import CartaoCredito
from app.models.centro_custo import CentroCusto
from app.services.financeiro import FinanceiroService
from app.services.lancamento import LancamentoService
from app.schemas.lancamento import LancamentoCreate, LancamentoUpdate
from app.models.usuario import Usuario

# Mock DB session
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def test_processo_financials():
    print("\n--- Testing Processo Financials & Success Fee ---")
    unique_id = str(uuid.uuid4())[:8]
    async with AsyncSessionLocal() as db:
        # 1. Create Client
        cliente = Participante(
            nome=f"Cliente Teste Financeiro {unique_id}",
            tipo=TipoParticipante.CLIENTE,
            documento=f"123{unique_id}",
            email=f"cliente_{unique_id}@teste.com"
        )
        db.add(cliente)
        await db.commit()
        await db.refresh(cliente)
        print(f"Cliente created: {cliente.id}")

        # 2. Create Processo with financial info
        processo = Processo(
            numero=f"PROC-{uuid.uuid4()}",
            descricao="Processo Teste Financeiro",
            cliente_id=cliente.id,
            status=StatusProcesso.ATIVO,
            valor_causa_estimado=Decimal("100000.00"),
            percentual_exito=Decimal("20.00")
        )
        db.add(processo)
        await db.commit()
        await db.refresh(processo)
        print(f"Processo created: {processo.id} with 20% success fee on 100k")

        # 3. Trigger FinanceiroService manually (as it's called in API, not model)
        # In API it is called after create/update
        await FinanceiroService.atualizar_previsao_honorarios(
            db, 
            processo.id, 
            processo.valor_causa_estimado, 
            processo.percentual_exito,
            processo.cliente_id,
            processo.numero
        )
        
        # 4. Verify generated Lancamento
        stmt = select(Lancamento).where(
            Lancamento.processo_id == processo.id,
            Lancamento.natureza == NaturezaLancamento.EXITO
        )
        result = await db.execute(stmt)
        lancamento = result.scalars().first()
        
        if lancamento:
            print(f"SUCCESS: Generated Lancamento: {lancamento.descricao}, Valor: {lancamento.valor}")
            assert lancamento.valor == Decimal("20000.00")
            assert lancamento.status == StatusLancamento.AGUARDANDO_TRANSITO
        else:
            print("FAILURE: No lancamento generated!")

        # Clean up
        await db.delete(processo) # Cascades might not be set up, so be careful
        if lancamento: await db.delete(lancamento)
        await db.delete(cliente)
        await db.commit()

async def test_reimbursement():
    print("\n--- Testing Reimbursement Logic ---")
    unique_id = str(uuid.uuid4())[:8]
    async with AsyncSessionLocal() as db:
        service = LancamentoService(db)
        
        # 1. Create Client and Processo
        cliente = Participante(
            nome=f"Cliente Reembolso {unique_id}",
            tipo=TipoParticipante.CLIENTE,
            documento=f"987{unique_id}"
        )
        db.add(cliente)
        await db.commit()
        
        processo = Processo(
            numero=f"PROC-REEMB-{uuid.uuid4()}",
            descricao="Processo Reembolso",
            cliente_id=cliente.id
        )
        db.add(processo)
        await db.commit()
        
        # 2. Create Reimbursable Expense via Service
        lancamento_in = LancamentoCreate(
            descricao="Despesa de Viagem",
            valor=Decimal("500.00"),
            data_vencimento=date.today(),
            tipo=TipoLancamento.DESPESA,
            natureza=NaturezaLancamento.PONTUAL,
            status=StatusLancamento.PENDENTE,
            participante_id=cliente.id, # Using cliente as payee for simplicity, typically it's a vendor
            processo_id=processo.id,
            reembolsavel=True
        )
        
        # We need a user for logging? Service doesn't require user
        created_lancamento = await service.create(lancamento_in)
        print(f"Expense created: {created_lancamento.id}, Reembolsavel: {created_lancamento.reembolsavel}")
        
        # 3. Check for generated Reimbursement
        stmt = select(Lancamento).where(Lancamento.lancamento_pai_id == created_lancamento.id)
        result = await db.execute(stmt)
        reembolso = result.scalars().first()
        
        if reembolso:
            print(f"SUCCESS: Generated Reembolso: {reembolso.descricao}, Valor: {reembolso.valor}")
            assert reembolso.valor == Decimal("500.00")
            assert reembolso.tipo == TipoLancamento.RECEITA
            assert reembolso.natureza == NaturezaLancamento.PONTUAL
            assert reembolso.participante_id == cliente.id
        else:
            print("FAILURE: No reembolso generated!")

        # 4. Update Expense Amount
        update_in = LancamentoUpdate(valor=Decimal("600.00"))
        updated_lancamento = await service.update(created_lancamento.id, update_in)
        
        # 5. Check if Reimbursement updated
        await db.refresh(reembolso)
        print(f"Updated Expense to 600.00. Reembolso value: {reembolso.valor}")
        assert reembolso.valor == Decimal("600.00")

        # Clean up
        await db.delete(reembolso)
        await db.delete(created_lancamento)
        await db.delete(processo)
        await db.delete(cliente)
        await db.commit()

async def main():
    try:
        await test_processo_financials()
        await test_reimbursement()
        print("\n\nALL TESTS PASSED SUCCESSFULLY")
    except Exception as e:
        print(f"\n\nTESTS FAILED: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(main())
