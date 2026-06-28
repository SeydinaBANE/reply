def exact_match_score(predictions: list[str], references: list[str]) -> float:
    if len(predictions) != len(references):
        raise ValueError("predictions and references length mismatch")
    if not predictions:
        return 0.0
    matches = sum(
        1 for pred, ref in zip(predictions, references) if pred.strip() == ref.strip()
    )
    return matches / len(predictions)
