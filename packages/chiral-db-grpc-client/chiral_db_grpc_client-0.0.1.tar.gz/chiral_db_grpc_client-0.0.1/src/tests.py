import client

def test_cases():
    chiral_db_client = client.Client('localhost', '10000')
    print("-------------- Testing QuerySimilarity ... --------------", end='\r')
    results = chiral_db_client.query_similarity('Cc1cc(NC(=O)c2cc(Cl)cc(Cl)c2O)ccc1Sc1nc2ccccc2s1', 1.0)
    assert 'CHEMBL263810' in results.keys()
    print("-------------- Testing QuerySimilarity Pass -------------")


if __name__ == '__main__':
    test_cases()