
import asyncio
import sys
import os
# Add the parent directory to sys.path to import app modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import app.core.database
print(f"app.core.database file: {app.core.database.__file__}")
print(f"app.core.database dir: {dir(app.core.database)}")

from app.core.database import async_session
from sqlalchemy import select
from app.models.centro_custo import CentroCusto
from app.models.lancamento import Lancamento
from app.models.enums import TipoLancamento

async def update_cost_centers():
    async with async_session() as session:
        print("Starting Cost Center Migration...")
        
        # 1. Ensure Default Cost Centers Exist
        default_centers = {
            TipoLancamento.RECEITA: [
                "Honorários Fixos",
                "Honorários de Êxito",
                "Consultoria Avulsa",
                "Reembolsos"
            ],
            TipoLancamento.DESPESA: [
                "Software & IA",
                "Infraestrutura",
                "Custas Judiciais",
                "Marketing Jurídico",
                "Outros" # Fallback
            ]
        }
        
        cost_centers_map = {} # Name -> ID

        for tipo, names in default_centers.items():
            for name in names:
                stmt = select(CentroCusto).where(CentroCusto.nome == name)
                result = await session.execute(stmt)
                center = result.scalar_one_or_none()
                
                if not center:
                    print(f"Creating Cost Center: {name} ({tipo})")
                    center = CentroCusto(nome=name, tipo=tipo, descricao=f"Categoria padrão: {name}")
                    session.add(center)
                    await session.flush() # Get ID
                
                cost_centers_map[name] = center.id
        
        await session.commit()
        print("Default Cost Centers ensured.")
        
        # 2. Update Lancamentos
        print("Updating existing Lancamentos...")
        stmt = select(Lancamento).where(Lancamento.centro_custo_id.is_(None))
        result = await session.execute(stmt)
        lancamentos = result.scalars().all()
        
        updated_count = 0
        
        for lancamento in lancamentos:
            description = lancamento.descricao.lower() if lancamento.descricao else ""
            tipo = lancamento.tipo
            
            target_center_id = None
            
            if tipo == TipoLancamento.DESPESA:
                if any(term in description for term in ["cursor", "openai", "chatgpt", "api", "software", "licença"]):
                    target_center_id = cost_centers_map.get("Software & IA")
                elif any(term in description for term in ["tribunal", "taxa", "alvará", "custas", "guia", "gru"]):
                    target_center_id = cost_centers_map.get("Custas Judiciais")
                elif any(term in description for term in ["aluguel", "luz", "água", "internet", "energia", "condomínio"]):
                    target_center_id = cost_centers_map.get("Infraestrutura")
                elif any(term in description for term in ["marketing", "anúncio", "facebook", "instagram", "google"]):
                    target_center_id = cost_centers_map.get("Marketing Jurídico")
                else:
                    target_center_id = cost_centers_map.get("Outros")
            
            elif tipo == TipoLancamento.RECEITA:
                if any(term in description for term in ["fixo", "mensal", "manutenção"]):
                    target_center_id = cost_centers_map.get("Honorários Fixos")
                elif any(term in description for term in ["êxito", "sucesso", "final"]):
                    target_center_id = cost_centers_map.get("Honorários de Êxito")
                elif any(term in description for term in ["reembolso", "devolução"]):
                    target_center_id = cost_centers_map.get("Reembolsos")
                else:
                    target_center_id = cost_centers_map.get("Consultoria Avulsa") # Default fallback for Receita
            
            if target_center_id:
                lancamento.centro_custo_id = target_center_id
                updated_count += 1
        
        await session.commit()
        print(f"Migration Complete. Updated {updated_count} lancamentos.")

if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
    asyncio.run(update_cost_centers())
