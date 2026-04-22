def calculate_sleep(age: int) -> tuple[int, int]:
    if age < 14:
        return (9, 11)
    if 14 <= age <= 17:
        return (9, 10)
    if 18 <= age <= 25:
        return (8, 9)
    if 26 <= age <= 64:
        return (7, 8)
    return (6, 7)
