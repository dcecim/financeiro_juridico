
import enum

class TipoParticipante(str, enum.Enum):
    CLIENTE = "CLIENTE"
    FORNECEDOR = "FORNECEDOR"
    AMBOS = "AMBOS"

class TipoLancamento(str, enum.Enum):
    RECEITA = "RECEITA"
    DESPESA = "DESPESA"

class NaturezaLancamento(str, enum.Enum):
    FIXO = "FIXO"
    PONTUAL = "PONTUAL"
    EXITO = "EXITO"

class StatusLancamento(str, enum.Enum):
    PENDENTE = "PENDENTE"
    PAGO = "PAGO"
    AGUARDANDO_TRANSITO = "AGUARDANDO_TRANSITO"
    CANCELADO = "CANCELADO"

class StatusProcesso(str, enum.Enum):
    ATIVO = "ATIVO"
    SUSPENSO = "SUSPENSO"
    ENCERRADO = "ENCERRADO"
    TRANSITO_JULGADO = "TRANSITO_JULGADO"
