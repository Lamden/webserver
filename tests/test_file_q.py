from unittest import TestCase

from webserver import WebServer, FileQueue
from lamden.crypto.wallet import Wallet
from contracting.client import ContractingClient
from contracting.db.driver import ContractDriver, decode, encode
from lamden.storage import BlockStorage
from lamden.crypto.transaction import build_transaction
from lamden import storage

n = ContractDriver()


class TestFileQueue(TestCase):
    def setUp(self):
        self.w = Wallet()

        self.blocks = BlockStorage()
        self.driver = ContractDriver()

        self.ws = WebServer(
            wallet=self.w,
            contracting_client=ContractingClient(),
            blocks=self.blocks,
            driver=n
        )
        self.ws.client.flush()
        self.ws.blocks.drop_collections()

        self.q = FileQueue('./txs')

    def tearDown(self):
        self.ws.client.flush()
        self.ws.blocks.drop_collections()

        self.q.flush()

    def test_len_zero_initially(self):
        self.assertEqual(len(self.q), 0)

    def test_append_increases_len(self):
        self.q.append('thing')
        self.assertEqual(len(self.q), 1)

    def test_push_transaction_can_be_retrieved_with_pop(self):
        tx = build_transaction(
            wallet=Wallet(),
            processor='b' * 64,
            stamps=123,
            nonce=0,
            contract='currency',
            function='transfer',
            kwargs={
                'amount': 123,
                'to': 'jeff'
            }
        )

        self.q.append(tx)

        tx_2 = self.q.pop(0)
        self.assertEqual(decode(tx), tx_2)

    def test_push_two_transaction_pop_gets_oldest_first(self):
        tx = build_transaction(
            wallet=Wallet(),
            processor='b' * 64,
            stamps=123,
            nonce=0,
            contract='currency',
            function='transfer',
            kwargs={
                'amount': 123,
                'to': 'jeff'
            }
        )

        self.q.append(tx)

        tx2 = build_transaction(
            wallet=Wallet(),
            processor='b' * 64,
            stamps=123,
            nonce=0,
            contract='currency',
            function='transfer',
            kwargs={
                'amount': 123,
                'to': 'jeff2'
            }
        )

        self.q.append(tx2)

        tx_2 = self.q.pop(0)
        self.assertEqual(decode(tx), tx_2)

    def test_pop_deletes_file(self):
        tx = build_transaction(
            wallet=Wallet(),
            processor='b' * 64,
            stamps=123,
            nonce=0,
            contract='currency',
            function='transfer',
            kwargs={
                'amount': 123,
                'to': 'jeff'
            }
        )

        self.q.append(tx)

        tx2 = build_transaction(
            wallet=Wallet(),
            processor='b' * 64,
            stamps=123,
            nonce=0,
            contract='currency',
            function='transfer',
            kwargs={
                'amount': 123,
                'to': 'jeff2'
            }
        )

        self.q.append(tx2)

        self.q.pop(0)

        self.assertEqual(len(self.q), 1)


