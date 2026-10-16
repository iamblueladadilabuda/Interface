import random
import math
from collections import defaultdict


ERROR_PROBABILITIES = (0.0, 0.3, 0.6, 0.9)
POLICIES = ("Начать с начала", "Начать с предыдущего", "Конец")
MAX_ITERATIONS = 100000


def weighted_choice(items, probability_key):
    """Выбирает элемент с учётом указанной вероятности."""
    return random.choices(
        items,
        weights=[item[probability_key] for item in items],
        k=1,
    )[0]


def run_route(route, times, pi, policy):
    """Моделирует выполнение маршрута с заданной дисциплиной обработки ошибок.

    Ошибка проверяется после выполнения текущего шага, поэтому время этого
    шага учитывается даже тогда, когда после него обнаруживается ошибка.
    """
    if policy not in POLICIES:
        raise ValueError(f"Неизвестная дисциплина обработки ошибок: {policy}")
    if not 0 <= pi <= 1:
        raise ValueError("Вероятность ошибки Pi должна быть от 0 до 1.")

    total = 0.0
    index = 0
    steps = route["steps"]
    iterations = 0

    while index < len(steps):
        iterations += 1
        if iterations > MAX_ITERATIONS:
            raise RuntimeError(
                "Превышен лимит повторов. Проверьте вероятность ошибки "
                "и выбранную дисциплину."
            )

        # Выполняем текущий шаг и учитываем его время.
        total += times[steps[index]]

        # Ошибки нет — переходим к следующему шагу маршрута.
        if random.random() >= pi:
            index += 1
            continue

        # Ошибка возникла после выполнения текущего шага.
        if policy == "Конец":
            # Прекращаем маршрут сразу после обнаружения ошибки.
            break
        elif policy == "Начать с начала":
            # Следующая попытка начнётся с первого шага.
            index = 0
        elif policy == "Начать с предыдущего":
            # Возвращаемся на один шаг назад. На первом шаге остаёмся
            # на нём же, чтобы повторить его, а затем продолжить маршрут.
            index = max(0, index - 1)

    return total


def calculate(data, n, policy):
    """Проводит N имитаций для каждой вероятности ошибки Pi."""
    if n < 1:
        raise ValueError("Количество имитаций N должно быть не меньше 1.")
    if policy not in POLICIES:
        raise ValueError(f"Неизвестная дисциплина обработки ошибок: {policy}")

    subsystems = list(data["subsystems"].values())
    times = data["times"]
    results = []

    for pi in ERROR_PROBABILITIES:
        all_times = []
        sub_times = defaultdict(list)

        for _ in range(n):
            sub = weighted_choice(subsystems, "probability")
            route = weighted_choice(sub["routes"], "probability")
            duration = run_route(route, times, pi, policy)
            all_times.append(duration)
            sub_times[sub["name"]].append(duration)

        average = sum(all_times) / n
        histogram_bins = max(1, int(1 + 3.22 * math.log10(n)))
        results.append({
            "Pi": pi,
            "average_time": average,
            "min_time": min(all_times),
            "max_time": max(all_times),
            "times": all_times,
            "subsystem_averages": {
                name: sum(vals) / len(vals)
                for name, vals in sub_times.items()
            },
            "histogram_bins": histogram_bins,
        })

    return results
