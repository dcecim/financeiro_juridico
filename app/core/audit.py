from sqlalchemy import event, inspect
from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.core.context import current_user_id_context
import uuid
from datetime import datetime, date

def serialize_value(v):
    if isinstance(v, (datetime, date)):
        return v.isoformat()
    if isinstance(v, uuid.UUID):
        return str(v)
    return v

def audit_listener(session, flush_context, instances):
    user_id = current_user_id_context.get()
    
    # Iterate over copies of collections
    for obj in list(session.new):
        if isinstance(obj, AuditLog): continue
        create_audit_entry(session, obj, "INSERT", user_id)
        
    for obj in list(session.dirty):
        if isinstance(obj, AuditLog): continue
        create_audit_entry(session, obj, "UPDATE", user_id)
        
    for obj in list(session.deleted):
        if isinstance(obj, AuditLog): continue
        create_audit_entry(session, obj, "DELETE", user_id)

def create_audit_entry(session, obj, action, user_id):
    state = inspect(obj)
    if not state.mapper:
        return

    table_name = state.mapper.local_table.name
    
    # Primary Key Logic
    pk_columns = state.mapper.primary_key
    pk_values = [getattr(obj, col.name) for col in pk_columns]
    registro_id = str(pk_values[0]) if pk_values else "N/A"
    
    dados_antigos = {}
    dados_novos = {}
    
    for attr in state.attrs:
        key = attr.key
        history = attr.history
        
        if action == "INSERT":
            val = getattr(obj, key)
            if val is not None:
                dados_novos[key] = serialize_value(val)
                     
        elif action == "UPDATE":
            if history.has_changes():
                old_val = history.deleted[0] if history.deleted else None
                new_val = history.added[0] if history.added else None
                dados_antigos[key] = serialize_value(old_val)
                dados_novos[key] = serialize_value(new_val)
                
        elif action == "DELETE":
             # For delete, try to capture state
             try:
                # Use history.unchanged or similar if available, or just getattr
                # If object is deleted, attributes might be expired.
                # But usually they are available in memory if loaded.
                val = getattr(obj, key)
                dados_antigos[key] = serialize_value(val)
             except:
                pass

    # Filter out empty updates (shouldn't happen if session.dirty is correct, but good safety)
    if action == "UPDATE" and not dados_novos:
        return

    audit = AuditLog(
        tabela=table_name,
        registro_id=registro_id,
        acao=action,
        usuario_id=user_id,
        dados_antigos=dados_antigos if dados_antigos else None,
        dados_novos=dados_novos if dados_novos else None
    )
    session.add(audit)

def setup_audit_listeners(session_class):
    event.listen(session_class, "before_flush", audit_listener)
