import tkinter as tk
from tkinter import messagebox
import third_window
import data_io


def routes_from_matrix(matrix):
    """Строит все пути от шага 1 до шага 10 по матрице смежности.

    matrix[r][c] == 1 означает переход из шага (r+1) в шаг (c+1).
    Возвращает список путей, каждый путь — список номеров шагов [1, ..., 10].
    """
    n = len(matrix)
    routes = []

    def dfs(node, path, visited):
        if node == n - 1:               # дошли до шага 10 (индекс 9)
            routes.append([x + 1 for x in path])
            return
        for nxt in range(n):
            if matrix[node][nxt] == 1 and nxt not in visited:
                dfs(nxt, path + [nxt], visited | {nxt})

    dfs(0, [0], {0})                    # старт с шага 1
    return routes


class SecondWindow:
    def __init__(self, variant_id, policy, N_sim, n_subsystems=0,
                 variant_file=None, times_file=None):
        self.variant_id = str(variant_id)
        self.policy = policy
        self.N_sim = int(N_sim)
        self.manual_mode = not variant_file

        # загружаем данные
        if not self.manual_mode:
            self.data = data_io.load_variant(
                variant_id=self.variant_id,
                variant_file=variant_file,
                times_file=times_file,
            )
        else:
            n = n_subsystems if n_subsystems and n_subsystems > 0 else 1
            self.data = data_io.make_empty_variant(n)

        self.subsystems = self.data["subsystems"]

        # если пользователь ограничил число подсистем — берём первые N
        sids = sorted(self.subsystems.keys())
        if n_subsystems and n_subsystems > 0:
            sids = sids[:n_subsystems]

        self.root = tk.Tk()
        self.root.title(f"Вариант {self.variant_id} — {self.policy}")
        self.root.state("zoomed")

        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)

        # ===================== КОНТЕЙНЕР СТРАНИЦ =====================
        self.pages_container = tk.Frame(self.root, bg="#fee")
        self.pages_container.grid(row=0, column=0, sticky="nsew")
        self.pages_container.rowconfigure(0, weight=1)
        self.pages_container.columnconfigure(0, weight=1)

        self.pages = []
        self.page_sids = []
        for sid in sids:
            page = self.create_page(sid)
            page.grid(row=0, column=0, sticky="nsew")
            self.pages.append(page)
            self.page_sids.append(sid)

        self.N = len(self.pages)
        if self.N == 0:
            raise ValueError("Не выбрано ни одной подсистемы для отображения.")

        self.current = 0

        # ============= НИЖНЯЯ ПАНЕЛЬ =============
        bottom = tk.Frame(self.root, bg="#eef")
        bottom.grid(row=1, column=0, sticky="we")
        bottom.columnconfigure(0, weight=1)
        bottom.columnconfigure(1, weight=1)
        bottom.columnconfigure(2, weight=1)

        self.btn_back = tk.Button(bottom, text="Назад", font=("Arial", 15),
                                  command=self.go_back)
        self.btn_back.grid(row=0, column=0, sticky="w", padx=10, pady=10)

        self.counter_label = tk.Label(bottom, text=f"1/{self.N}",
                                      font=("Arial", 15), bg="#eef")
        self.counter_label.grid(row=0, column=1)

        self.btn_next = tk.Button(bottom, text="Далее", font=("Arial", 15),
                                  command=self.go_next)
        self.btn_next.grid(row=0, column=2, sticky="e", padx=10, pady=10)

        self.show_page(0)

    # ---------- Создание одной страницы по подсистеме ----------
    def create_page(self, sid):
        sub = self.subsystems[sid]

        page = tk.Frame(self.pages_container)
        page.columnconfigure(0, weight=1)
        page.columnconfigure(1, weight=1)
        page.rowconfigure(0, weight=1)

        # ===== ЛЕВАЯ ПОЛОВИНА =====
        left_frame = tk.Frame(page, bg="#eef")
        left_frame.grid(row=0, column=0, sticky="nsew")

        left_frame.columnconfigure(0, weight=1)
        left_frame.columnconfigure(1, weight=1)
        left_frame.rowconfigure(0, weight=1)
        left_frame.rowconfigure(3, weight=1)

        tk.Label(left_frame, text="Название подсистемы:",
                 font=("Arial", 15), anchor="e", bg="#eef").grid(
            row=1, column=0, sticky="we", padx=(10, 0), pady=10)

        page.entry_1 = tk.Entry(left_frame, font=("Arial", 15))
        page.entry_1.grid(row=1, column=1, sticky="we",
                          padx=(0, 10), pady=10)
        page.entry_1.insert(0, sub["name"])

        tk.Label(left_frame, text="Вероятность подсистемы:",
                 font=("Arial", 15), anchor="e", bg="#eef").grid(
            row=2, column=0, sticky="we", padx=(10, 0), pady=10)

        page.entry_2 = tk.Entry(left_frame, font=("Arial", 15))
        page.entry_2.grid(row=2, column=1, sticky="we",
                          padx=(0, 10), pady=10)
        page.entry_2.insert(0, str(sub["probability"]))

        # ===== ПРАВАЯ ПОЛОВИНА =====
        right_frame = tk.Frame(page, bg="#fee")
        right_frame.grid(row=0, column=1, sticky="nsew")

        right_frame.columnconfigure(0, weight=1)
        right_frame.columnconfigure(1, weight=1)
        right_frame.rowconfigure(0, weight=1)

        # ----- Левая подполовина: Pm -----
        right_left = tk.Frame(right_frame, bg="#fdd")
        right_left.grid(row=0, column=0, sticky="nsew")

        right_left.columnconfigure(0, weight=1)
        right_left.rowconfigure(0, weight=0)

        tk.Label(right_left, text="Вероятность Pm",
                 font=("Arial", 20), bg="#fdd", anchor="center").grid(
            row=0, column=0, sticky="we", pady=(10, 15))

        page.entries_left = []
        for i in range(10):
            right_left.rowconfigure(i + 1, weight=1)
            e = tk.Entry(right_left, font=("Arial", 15), bg="#fdd",
                         justify="left")
            e.grid(row=i + 1, column=0, sticky="nsew", padx=10, pady=2)
            val = sub["pm"].get(i + 1, "")
            e.insert(0, str(val))
            page.entries_left.append(e)

        # ----- Правая подполовина: таблица -----
        right_right = tk.Frame(right_frame, bg="#fdf")
        right_right.grid(row=0, column=1, sticky="nsew")

        right_right.columnconfigure(0, weight=1)
        right_right.rowconfigure(0, weight=0)
        right_right.rowconfigure(1, weight=1)

        tk.Label(right_right, text="Последовательность шагов",
                 font=("Arial", 20), bg="#fdf", anchor="center").grid(
            row=0, column=0, sticky="we", pady=(10, 15))

        table_frame = tk.Frame(right_right, bg="#fdf")
        table_frame.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)

        page.table = []
        for r in range(10):
            table_frame.rowconfigure(r, weight=1)
            row_cells = []
            for c in range(10):
                table_frame.columnconfigure(c, weight=1)
                cell = tk.Entry(table_frame, font=("Arial", 15), width=5,
                                justify="center")
                cell.grid(row=r, column=c, sticky="nsew", padx=1, pady=1)
                cell.insert(0, str(sub["matrix"][r][c]))
                row_cells.append(cell)
            page.table.append(row_cells)

        return page

    # ---------- Переключение страниц ----------
    def show_page(self, index):
        if not (0 <= index < self.N):
            return

        self.current = index
        self.pages[index].tkraise()
        self.counter_label.config(text=f"{index + 1}/{self.N}")

        self.btn_back.config(state="normal" if index > 0 else "disabled")
        self.btn_next.config(state="normal")

        if index == self.N - 1:
            self.btn_next.config(text="Завершить")
        else:
            self.btn_next.config(text="Далее")

    # ---------- Сбор правок из UI в self.data ----------
    def collect_data(self):
        for sid, page in zip(self.page_sids, self.pages):
            sub = self.subsystems[sid]

            sub["name"] = page.entry_1.get().strip()

            try:
                sub["probability"] = float(
                    page.entry_2.get().strip().replace(",", ".") or 0)
            except ValueError:
                sub["probability"] = 0.0

            sub["pm"] = {}
            for i, e in enumerate(page.entries_left):
                val = e.get().strip().replace(",", ".")
                if val:
                    try:
                        sub["pm"][i + 1] = float(val)
                    except ValueError:
                        pass

            for r in range(10):
                for c in range(10):
                    val = page.table[r][c].get().strip()
                    sub["matrix"][r][c] = int(val) if val.isdigit() else 0

            if self.manual_mode:
                routes = routes_from_matrix(sub["matrix"])
                if routes:
                    p = 1.0 / len(routes)
                    sub["routes"] = [
                        {"id": i + 1, "probability": p, "steps": r}
                        for i, r in enumerate(routes)
                    ]
                else:
                    sub["routes"] = []

        if self.manual_mode and not self.data.get("times"):
            self.data["times"] = {i: 1.0 for i in range(1, 11)}

        return self.data

    def go_next(self):
        if self.current < self.N - 1:
            self.show_page(self.current + 1)
            return

        data = self.collect_data()

        # проверяем маршруты
        problems = []
        for sid, sub in data["subsystems"].items():
            if not sub["routes"]:
                problems.append(f"Подсистема {sid}: нет маршрутов.")

        if problems:
            messagebox.showerror(
                "Ошибка",
                "Нет маршрутов:\n\n" + "\n".join(problems)
            )
            return

        # сумма вероятностей подсистем
        p_total = sum(s["probability"] for s in data["subsystems"].values())
        if abs(p_total - 1) > 1e-6:
            messagebox.showerror(
                "Ошибка",
                f"Сумма вероятностей подсистем должна быть 1 "
                f"(сейчас {p_total:.4g})."
            )
            return

        self.root.destroy()
        third_window.ThirdWindow(data, self.N_sim, self.policy).run()

    def go_back(self):
        self.show_page(self.current - 1)

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    SecondWindow(1, "Начать с начала", 1000).run()
