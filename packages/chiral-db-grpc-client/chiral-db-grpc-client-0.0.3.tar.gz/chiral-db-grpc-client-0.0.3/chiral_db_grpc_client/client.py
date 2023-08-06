import typing
import grpc

from . import chiral_db_pb2
from . import chiral_db_pb2_grpc


class Client:
    def __init__(self, host: str, port: str):
        self.channel = grpc.insecure_channel(f'{host}:{port}')
        self.stub = chiral_db_pb2_grpc.ChiralDbStub(self.channel)

    def __del__(self):
        self.channel.close()

    def query_similarity(self, smiles: str, cutoff: float) -> typing.Dict[str, float]:
        mol = chiral_db_pb2.Molecule(smiles=smiles)
        return self.stub.QuerySimilarity(chiral_db_pb2.RequestSimilarity(mol=mol, cutoff=cutoff)).results

    