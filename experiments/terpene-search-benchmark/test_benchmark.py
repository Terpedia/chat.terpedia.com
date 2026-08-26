import unittest

import benchmark


class BenchmarkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.library, cls.adjacency = benchmark.build_library(450, seed=9)

    def test_library_is_unique_and_valid(self):
        smiles = [record.smiles for record in self.library]
        self.assertEqual(len(smiles), len(set(smiles)))
        self.assertTrue(all(benchmark.is_valid(benchmark.Chem.MolFromSmiles(s)) for s in smiles))

    def test_searches_have_equal_budget_and_valid_output(self):
        task = benchmark.ProxyTask(0)
        naive = benchmark.naive_random_search(self.library, task.score, 300, 11, output_size=50)
        evolved = benchmark.evolutionary_search(
            self.library, self.adjacency, task.score, 300, 11, output_size=50
        )
        self.assertEqual(naive.evaluations, evolved.evaluations)
        self.assertEqual(len(naive.selected), 50)
        self.assertEqual(len(evolved.selected), 50)
        self.assertEqual(len(set(evolved.selected)), 50)

    def test_deterministic_scores(self):
        task = benchmark.ProxyTask(2)
        first = benchmark.naive_random_search(self.library, task.score, 300, 22, output_size=50)
        second = benchmark.naive_random_search(self.library, task.score, 300, 22, output_size=50)
        self.assertEqual(first.selected, second.selected)
        self.assertEqual(first.mean_score, second.mean_score)


if __name__ == "__main__":
    unittest.main()
