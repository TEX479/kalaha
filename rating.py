def get_rating(wins:list[int], losses:list[int]) -> int:
    return (sum(wins) + sum(losses) + 400 * len(wins) - 400 * len(losses)) // max(len(wins)+len(losses), 1)