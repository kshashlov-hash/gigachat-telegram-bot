def arctan_taylor(x, eps=1e-10, max_iter=1000000):
    """
    Вычисление arctan(x) через ряд Тейлора.

        x — число, |x| <= 1
        eps — требуемая точность
        max_iter — ограничение по количеству итераций
    """

    if abs(x) > 1:
        raise ValueError("Для корректной работы ряда необходимо |x| <= 1")

    result = 0.0
    term = x  # первый член ряда при n=1
    n = 1

    while abs(term) > eps and n <= max_iter:
        result += term
        n += 1
        term = ((-1) ** (n - 1)) * x ** (2 * n - 1) / (2 * n - 1)

    return result


# Пример использования:
x = float(input("Введите x (|x| <= 1): "))
value = arctan_taylor(x)
print(f"arctan({x}) ≈ {value}")
