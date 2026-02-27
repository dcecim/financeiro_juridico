
import sys
import os

# Add the current directory to sys.path
sys.path.append(os.getcwd())

try:
    from app.core.config import settings
    from app.core.database import Base, engine
    from app.models.participante import Participante
    from app.models.processo import Processo
    from app.models.lancamento import Lancamento
    from app.services.conciliacao import ConciliacaoService
    from app.schemas.ofx import OfxTransactionSchema
    
    print("All modules imported successfully.")
except Exception as e:
    print(f"Error importing modules: {e}")
    sys.exit(1)
