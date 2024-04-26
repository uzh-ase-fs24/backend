import unittest
from ..src.LocationRiddlesService import LocationRiddlesService


class TestCalculateDistance(unittest.TestCase):
    def setUp(self):
        self.location_zurich = (950773.5032378712, 6003947.738097198)  # Zurich Hauptbahnhof
        self.location_st_gallen = (1043079.6590545248, 6011475.68947705)  # St. Gallen Hauptbahnhof

    def test_distance_zero(self):
        # Test the distance calculation when both points are the same (Zurich HB to Zurich HB)
        _ ,distance = LocationRiddlesService.calculate_score_and_distance(self.location_zurich, self.location_zurich)
        self.assertEqual(distance, 0)

    def test_distance_zurich_to_st_gallen(self):
        # Test the distance calculation from Zurich to St. Gallen
        _, distance = LocationRiddlesService.calculate_score_and_distance(self.location_zurich, self.location_st_gallen)
        # Distance between choosen point at Zurich Hauptbahnhof and St.Gallen Hauptbahnhof is approx. 62'583 km (according to google maps)
        self.assertAlmostEqual(
            distance,  92.612, delta=5
        )  # Allowing margin for calculation errors

    def test_calculate_score_perfect_guess(self):
        score, _ = LocationRiddlesService.calculate_score_and_distance(
            self.location_zurich, self.location_zurich, 10000, 100
        )
        self.assertEqual(score, 10000)

    def test_calculate_score_far_guess(self):
        score, _ = LocationRiddlesService.calculate_score_and_distance(
            self.location_zurich, self.location_st_gallen, 10000, 100
        )
        self.assertAlmostEqual(score, 738.7, delta=5)

        # Reversing the order (Zurich instead of St.Gallen) should lead to the same result
        score2, _ = LocationRiddlesService.calculate_score_and_distance(
            self.location_st_gallen, self.location_zurich, 10000, 100
        )
        self.assertAlmostEqual(score2, 738.7, delta=5)


if __name__ == "__main__":
    unittest.main()
