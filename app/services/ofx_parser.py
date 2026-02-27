
from io import BytesIO
from decimal import Decimal
from datetime import date
from ofxparse import OfxParser as LibOfxParser
from app.schemas.ofx import OfxTransactionSchema

class OfxParserService:
    @staticmethod
    def parse_file(file_content: bytes) -> list[OfxTransactionSchema]:
        """
        Lê o conteúdo de um arquivo OFX e retorna uma lista de transações padronizadas.
        """
        # ofxparse espera um arquivo-like object (stream)
        # O arquivo pode estar em codificação diferente (ex: ISO-8859-1 ou UTF-8)
        # ofxparse tenta lidar com isso, mas BytesIO é o caminho seguro.
        ofx = LibOfxParser.parse(BytesIO(file_content))
        
        transactions = []
        
        # Lidar com uma ou múltiplas contas
        accounts = []
        if hasattr(ofx, 'accounts') and ofx.accounts:
            accounts = ofx.accounts
        elif hasattr(ofx, 'account') and ofx.account:
            accounts = [ofx.account]
            
        for account in accounts:
            if not hasattr(account, 'statement') or not account.statement:
                continue
                
            for tx in account.statement.transactions:
                # Converter para o nosso schema
                # ofxparse retorna data como datetime
                tx_date = tx.date.date() if hasattr(tx.date, 'date') else tx.date
                
                # ID da transação
                tx_id = str(tx.id)
                
                # Descrição (memo ou payee)
                descricao = (tx.memo or tx.payee or "Transação OFX").strip()
                
                # Valor (Decimal)
                # ofxparse retorna decimal.Decimal geralmente, mas garantimos
                valor = Decimal(str(tx.amount))
                
                transactions.append(OfxTransactionSchema(
                    id=tx_id,
                    data=tx_date,
                    valor=valor,
                    descricao=descricao
                ))
                
        return transactions
