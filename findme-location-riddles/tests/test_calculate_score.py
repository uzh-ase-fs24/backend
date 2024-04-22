import unittest

from src.helpers.CalculateScore import calculate_score_and_distance


class TestCalculateScore(unittest.TestCase):
    def test_calculate_score_perfect_guess(self):
        # Test scoring for a perfect guess --> 10'000 points
        actual_location = (47.3781750, 8.5391383)  # Zurich Hauptbahnhof
        guessed_location = (47.3781750, 8.5391383)  # Zurich Hauptbahnhof

        score, _ = calculate_score_and_distance(actual_location, guessed_location, 10000, 100)
        self.assertEqual(score, 10000)

    def test_calculate_score_far_guess(self):
        # Test scoring where user guessed St.Gallen instead of Zurich
        actual_location = (47.3781750, 8.5391383)  # Zurich Hauptbahnhof
        guessed_location = (47.4223234, 9.3680846)  # St. Gallen Hauptbahnhof

        # Guessing St.Gallen instead of Zurich should lead to an approx. score of 3741 due to the distance penalty
        score, _ = calculate_score_and_distance(actual_location, guessed_location, 10000, 100)
        self.assertAlmostEqual(score, 3741, delta=5)

        # Reversing the order (Zurich instead of St.Gallen) should lead to the same result
        score2, _ = calculate_score_and_distance(guessed_location, actual_location, 10000, 100)
        self.assertAlmostEqual(score2, 3741, delta=5)

    def test_calculate_score_zero(self):
        # Score should be 0 since points are way too far apart of each other
        actual_location = (0.3781750, 8.5391383)
        guessed_location = (47.4223234, 9.3680846)
        score, _ = calculate_score_and_distance(actual_location, guessed_location, 10000, 100)
        self.assertEqual(score, 0)


if __name__ == '__main__':
    unittest.main()
