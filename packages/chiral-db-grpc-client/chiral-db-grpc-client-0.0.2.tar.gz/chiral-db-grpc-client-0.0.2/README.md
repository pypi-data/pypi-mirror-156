# ChiralDB gRPC Client in Python

## Create a Client instance
```
import chiral_db_grpc_client

host = ''
port = ''
client = chiral_db_grpc_client.Client(host, port)
```

## Similarity Query
```
smiles = ''
cutoff = 0.0
client.query_similarity(smiles, cutoff)
```