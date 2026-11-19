import unittest
import numpy as np

from core.aco import AntColonyOptimizer


class TestAntColonyOptimizer(unittest.TestCase):
    def test_finds_valid_closed_tour_starting_and_ending_at_center(self):
        distances = np.array([
            [999999999.0, 10.0, 15.0, 20.0],
            [10.0, 999999999.0, 35.0, 25.0],
            [15.0, 35.0, 999999999.0, 30.0],
            [20.0, 25.0, 30.0, 999999999.0],
        ])
        np.random.seed(42)

        optimizer = AntColonyOptimizer(
            distances=distances,
            n_ants=12,
            n_best=4,
            n_iterations=15,
            decay=0.6,
        )
        best_path, best_dist, history = optimizer.run()

        self.assertEqual(best_path[0], 0)
        self.assertEqual(best_path[-1], 0)
        self.assertEqual(len(best_path), 5)
        self.assertEqual(set(best_path[:-1]), {0, 1, 2, 3})
        self.assertGreater(best_dist, 0)
        self.assertLess(best_dist, 120)
        self.assertEqual(len(history), 15)

    def test_gen_path_dist_sums_edges_correctly(self):
        distances = np.array([
            [999999999.0, 4.0, 9.0],
            [4.0, 999999999.0, 6.0],
            [9.0, 6.0, 999999999.0],
        ])
        optimizer = AntColonyOptimizer(distances, n_ants=2, n_best=1, n_iterations=1, decay=0.5)
        self.assertEqual(optimizer.gen_path_dist([0, 1, 2, 0]), 19.0)


if __name__ == "__main__":
    unittest.main()
