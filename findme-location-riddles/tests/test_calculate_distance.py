import unittest

from ..src.helpers.CalculateDistance import haversine_distance


class TestCalculateDistance(unittest.TestCase):
    def setUp(self):
        self.location_zurich = (47.3781750, 8.5391383)  # Zurich Hauptbahnhof
        self.location_st_gallen = (47.4223234, 9.3680846)  # St. Gallen Hauptbahnhof

    def test_haversine_distance_zero(self):
        # Test the distance calculation when both points are the same (Zurich HB to Zurich HB)
        distance = haversine_distance(self.location_zurich, self.location_zurich)
        self.assertEqual(distance, 0)

    def test_haversine_distance_zurich_to_st_gallen(self):
        # Test the distance calculation from Zurich to St. Gallen
        distance = haversine_distance(self.location_zurich, self.location_st_gallen)
        # Distance between choosen point at Zurich Hauptbahnhof and St.Gallen Hauptbahnhof is approx. 62'583 km (according to google maps)
        self.assertAlmostEqual(
            distance, 62.583, delta=5
        )  # Allowing margin for calculation errors


if __name__ == "__main__":
    unittest.main()
