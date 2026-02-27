
import unittest
from unittest.mock import MagicMock, patch
from decimal import Decimal
from datetime import datetime, date
from app.services.ofx_parser import OfxParserService

class TestOfxParser(unittest.TestCase):
    @patch('app.services.ofx_parser.LibOfxParser.parse')
    def test_parse_file_single_account(self, mock_parse):
        # Mock OFX structure
        mock_ofx = MagicMock()
        mock_account = MagicMock()
        mock_statement = MagicMock()
        
        # Mock transactions
        tx1 = MagicMock()
        tx1.id = "TX123"
        tx1.date = datetime(2023, 10, 1)
        tx1.amount = Decimal("-150.50")
        tx1.memo = "PAGAMENTO BOLETO"
        tx1.payee = ""

        tx2 = MagicMock()
        tx2.id = "TX124"
        tx2.date = datetime(2023, 10, 2)
        tx2.amount = Decimal("2500.00")
        tx2.memo = ""
        tx2.payee = "CLIENTE A"

        mock_statement.transactions = [tx1, tx2]
        mock_account.statement = mock_statement
        
        # Set up mock OFX object
        mock_ofx.account = mock_account
        mock_ofx.accounts = [mock_account] # Support both ways
        
        mock_parse.return_value = mock_ofx
        
        # Test
        content = b"DUMMY OFX CONTENT"
        transactions = OfxParserService.parse_file(content)
        
        # Assertions
        self.assertEqual(len(transactions), 2)
        
        self.assertEqual(transactions[0].id, "TX123")
        self.assertEqual(transactions[0].valor, Decimal("-150.50"))
        self.assertEqual(transactions[0].descricao, "PAGAMENTO BOLETO")
        self.assertEqual(transactions[0].data, date(2023, 10, 1))
        
        self.assertEqual(transactions[1].id, "TX124")
        self.assertEqual(transactions[1].valor, Decimal("2500.00"))
        self.assertEqual(transactions[1].descricao, "CLIENTE A")
        self.assertEqual(transactions[1].data, date(2023, 10, 2))
        
        print("OFX Parser Test Passed!")

if __name__ == '__main__':
    unittest.main()
