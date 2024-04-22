from .CalculateDistance import haversine_distance


# TODO The current implementation allows to adjust the scoring algorithm quite easily. It is to be investigated by
#  UAT tests whether a linear curve is suitable
def calculate_score_and_distance(
    actual_coord, guessed_coord, max_score=10000, distance_penalty=100
):
    """
    Calculate a score based on the distance between the actual and guessed coordinates. The greater the distance, the lower the score.

    Parameters:
    - actual_coord (tuple): Latitude and longitude of the actual location (degrees).
    - guessed_coord (tuple): Latitude and longitude of the guessed location (degrees).
    - max_score (int, optional): The maximum possible score for a perfect guess. Default is 10000.
    - distance_penalty (int, optional): Penalty factor applied per kilometer of distance. Default is 100.

    Returns:
    - int: Calculated score, with zero as the minimum possible score.
    """
    distance = haversine_distance(actual_coord, guessed_coord)

    # Calculate score, simple linear penalty
    score = max(0, max_score - distance * distance_penalty)
    return score, distance
