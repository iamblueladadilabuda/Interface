import csv
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
VARIANT_FILE = BASE_DIR / "variants.csv"
TIMES_FILE = BASE_DIR / "step_times.csv"


def read_rows(path):
    path = Path(path)
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        raw_lines = f.readlines()

    header_index = None
    for i, line in enumerate(raw_lines):
        stripped = line.strip()
        if not stripped:
            continue
        candidate = stripped.lstrip("\ufeff")
        if candidate.startswith("#"):
            candidate = candidate[1:].strip()
            if "variant_id" in candidate or "step_id" in candidate:
                raw_lines[i] = candidate + "\n"
                header_index = i
                break
        else:
            header_index = i
            break

    if header_index is None:
        return []

    lines = raw_lines[header_index:]
    cleaned = []
    for i, line in enumerate(lines):
        if i > 0 and line.lstrip().startswith("#"):
            continue
        cleaned.append(line)
    return list(csv.DictReader(cleaned))


def parse_number(value, field_name):
    value = str(value).strip().replace(",", ".")
    if not value:
        raise ValueError(f"Не заполнено поле «{field_name}».")
    try:
        return float(value)
    except ValueError:
        raise ValueError(f"В поле «{field_name}» должно быть число: {value!r}")


def load_variant(variant_id="1", variant_file=None, times_file=None):
    # Если файл не указан — берём стандартный
    variant_file = Path(variant_file) if variant_file else VARIANT_FILE
    # Файл времён ищем рядом с variant_file, а не с глобальным VARIANT_FILE
    times_file = Path(times_file) if times_file else variant_file.with_name("step_times.csv")

    variant_rows = [r for r in read_rows(variant_file)
                    if r["variant_id"].strip() == str(variant_id)]
    time_rows = [r for r in read_rows(times_file)
                 if r["variant_id"].strip() == str(variant_id)]

    if not variant_rows:
        raise ValueError(f"В файле {variant_file.name} нет варианта №{variant_id}.")

    times = {}
    for row in time_rows:
        raw = row.get("time_fixed", "").strip()
        if raw:
            times[int(row["step_id"])] = parse_number(
                raw, f"время шага {row['step_id']}")

    subsystems = {}
    for row in variant_rows:
        sid = int(row["subsystem_id"])
        if sid not in subsystems:
            subsystems[sid] = {
                "name": row["subsystem_name"].strip(),
                "probability": parse_number(row["subsystem_probability"],
                                            "вероятность подсистемы"),
                "pm": {},
                "matrix": [[0 for _ in range(10)] for _ in range(10)],
                "routes": []
            }
        seq = [int(x) for x in row["step_sequence"].split() if x.strip()]
        subsystems[sid]["routes"].append({
            "id": int(row["route_id"]),
            "probability": parse_number(row["route_probability"],
                                        "вероятность маршрута"),
            "steps": seq
        })
        for a, b in zip(seq, seq[1:]):
            subsystems[sid]["matrix"][a - 1][b - 1] = 1

    validate_data(subsystems, times)
    return {
        "variant_id": str(variant_id),
        "variant_file": str(variant_file),
        "times_file": str(times_file),
        "subsystems": subsystems,
        "times": times
    }


def make_empty_variant(n_subsystems=1, n_steps=10):
    """Пустая структура для ручного ввода.

    Маршруты пусты — пользователь должен будет их заполнить.
    Пока routes пусты, simulation.calculate работать не будет.
    """
    times = {i: 0.0 for i in range(1, n_steps + 1)}
    subsystems = {}
    for sid in range(1, n_subsystems + 1):
        subsystems[sid] = {
            "name": f"Подсистема {sid}",
            "probability": 0.0,
            "pm": {},
            "matrix": [[0] * 10 for _ in range(10)],
            "routes": [],
        }
    return {
        "variant_id": "manual",
        "variant_file": None,
        "times_file": None,
        "subsystems": subsystems,
        "times": times,
    }


def validate_data(subsystems, times):
    if not subsystems:
        raise ValueError("В варианте не задано ни одной подсистемы.")
    p_total = sum(s["probability"] for s in subsystems.values())
    if any(s["probability"] < 0 for s in subsystems.values()) or abs(p_total - 1) > 1e-6:
        raise ValueError(f"Сумма вероятностей подсистем должна быть 1 (сейчас {p_total:.4g}).")
    for sid, sub in subsystems.items():
        route_total = sum(r["probability"] for r in sub["routes"])
        if any(r["probability"] < 0 for r in sub["routes"]) or abs(route_total - 1) > 1e-6:
            raise ValueError(f"Сумма вероятностей маршрутов подсистемы {sid} должна быть 1 (сейчас {route_total:.4g}).")
        for route in sub["routes"]:
            if not route["steps"]:
                raise ValueError(f"У маршрута {route['id']} подсистемы {sid} нет шагов.")
            for step in route["steps"]:
                if step < 1 or step > 10:
                    raise ValueError(f"Номер шага {step} должен быть от 1 до 10.")
                if step not in times:
                    raise ValueError(f"Для шага {step} не задано фиксированное время в CSV.")
                if times[step] < 0:
                    raise ValueError(f"Время шага {step} не может быть отрицательным.")
