import tkinter as tk
import simulation


class ThirdWindow:
    def __init__(self, data, N, policy):
        self.data = data
        self.N = int(N)
        self.policy = policy

        # считаем один раз
        self.results = simulation.calculate(self.data, self.N, self.policy)

        self.root = tk.Tk()
        self.root.title("Результаты")
        self.root.state("zoomed")

        # сетка корня: слева — гистограмма, справа — таблица и кнопка
        self.root.columnconfigure(0, weight=3)   # гистограмма шире
        self.root.columnconfigure(1, weight=2)   # таблица уже
        self.root.rowconfigure(0, weight=1)

        self.build_ui()

        # Первая отрисовка — после того, как окно получит реальные размеры
        self.root.after_idle(self.redraw_histograms)
        # Перерисовывать при изменении размера окна
        self.canvas.bind("<Configure>", lambda e: self.redraw_histograms())

    # ---------- Интерфейс ----------
    def build_ui(self):
        # ============ ЛЕВАЯ ЧАСТЬ: гистограмма ============
        left = tk.Frame(self.root, bg="#f8f8ff")
        left.grid(row=0, column=0, sticky="nsew")
        left.rowconfigure(1, weight=1)
        left.columnconfigure(0, weight=1)

        # Заголовок
        tk.Label(left, text=f"Дисциплина: {self.policy}   N = {self.N}",
                 font=("Arial", 18), bg="#f8f8ff").grid(
            row=0, column=0, pady=10)

        # Канва
        self.canvas = tk.Canvas(left, bg="white")
        self.canvas.grid(row=1, column=0, sticky="nsew", padx=10, pady=10)

        # Панель управления гистограммой
        ctrl = tk.Frame(left, bg="#f8f8ff")
        ctrl.grid(row=2, column=0, pady=10)

        tk.Label(ctrl, text="Столбцов:", font=("Arial", 14),
                 bg="#f8f8ff").pack(side="left")
        self.bins_entry = tk.Entry(ctrl, font=("Arial", 14), width=6)
        self.bins_entry.pack(side="left", padx=5)
        self.bins_entry.insert(0, str(self.results[0]["histogram_bins"]))

        tk.Button(ctrl, text="Пересчитать", font=("Arial", 14),
                  command=self.redraw_histograms).pack(side="left", padx=10)

        tk.Label(ctrl, text="Pi:", font=("Arial", 14),
                 bg="#f8f8ff").pack(side="left", padx=(20, 5))
        self.pi_var = tk.StringVar(value=str(self.results[0]["Pi"]))
        pi_menu = tk.OptionMenu(ctrl, self.pi_var,
                                *[str(r["Pi"]) for r in self.results],
                                command=lambda _: self.redraw_histograms())
        pi_menu.config(font=("Arial", 14))
        pi_menu.pack(side="left")

        # ============ ПРАВАЯ ЧАСТЬ: таблица + кнопка ============
        right = tk.Frame(self.root, bg="#fff5f5")
        right.grid(row=0, column=1, sticky="nsew")
        right.rowconfigure(1, weight=1)
        right.columnconfigure(0, weight=1)

        tk.Label(right, text="Средние по Pi", font=("Arial", 18),
                 bg="#fff5f5").grid(row=0, column=0, pady=10)

        self.build_table(right)

        # --- Кнопка «Заново» в правом нижнем углу ---
        btn_restart = tk.Button(right, text="Заново", font=("Arial", 15),
                                command=self.restart)
        btn_restart.grid(row=2, column=0, sticky="e", padx=15, pady=15)

    def build_table(self, parent):
        table = tk.Frame(parent, bg="#fff5f5")
        table.grid(row=1, column=0, sticky="n", padx=10)

        headers = ["Pi", "Среднее", "Минимум", "Максимум"]
        for c, h in enumerate(headers):
            tk.Label(table, text=h, font=("Arial", 13, "bold"),
                     borderwidth=1, relief="solid", width=14).grid(
                row=0, column=c, sticky="nsew")

        for r, res in enumerate(self.results, start=1):
            for c, val in enumerate([
                f"{res['Pi']:.2f}",
                f"{res['average_time']:.4f}",
                f"{res['min_time']:.4f}",
                f"{res['max_time']:.4f}",
            ]):
                tk.Label(table, text=val, font=("Arial", 12),
                         borderwidth=1, relief="solid", width=14).grid(
                    row=r, column=c, sticky="nsew")

    # ---------- Гистограмма ----------
    def redraw_histograms(self):
        try:
            bins = int(self.bins_entry.get().strip())
            if bins < 1:
                bins = 1
        except ValueError:
            bins = 10

        try:
            pi_value = float(self.pi_var.get())
        except ValueError:
            pi_value = self.results[0]["Pi"]

        res = next(r for r in self.results if abs(r["Pi"] - pi_value) < 1e-9)
        self.draw_histogram(res["times"], bins)

    def draw_histogram(self, values, bins):
        self.canvas.delete("all")

        if not values:
            return

        W = self.canvas.winfo_width()
        H = self.canvas.winfo_height()
        # если канва ещё не получила размер — пропускаем (после after_idle
        # или <Configure> вызовется снова)
        if W <= 1 or H <= 1:
            return

        vmin = min(values)
        vmax = max(values)
        if vmax == vmin:
            vmax = vmin + 1

        width = (vmax - vmin) / bins
        counts = [0] * bins
        for v in values:
            idx = min(int((v - vmin) / width), bins - 1)
            counts[idx] += 1

        pad_left = 60
        pad_bottom = 60
        pad_top = 30
        pad_right = 20

        plot_w = W - pad_left - pad_right
        plot_h = H - pad_bottom - pad_top
        if plot_w <= 0 or plot_h <= 0:
            return

        max_count = max(counts) or 1
        bar_w = plot_w / bins

        # оси
        self.canvas.create_line(pad_left, pad_top,
                                pad_left, pad_top + plot_h)
        self.canvas.create_line(pad_left, pad_top + plot_h,
                                pad_left + plot_w, pad_top + plot_h)

        # столбцы
        for i, count in enumerate(counts):
            x0 = pad_left + i * bar_w
            x1 = x0 + bar_w - 2
            h = plot_h * count / max_count
            y0 = pad_top + plot_h - h
            y1 = pad_top + plot_h
            self.canvas.create_rectangle(x0, y0, x1, y1,
                                         fill="#4a90d9", outline="black")
            self.canvas.create_text((x0 + x1) / 2, y0 - 8,
                                    text=str(count), font=("Arial", 10))

        # подписи X
        for i in range(bins + 1):
            x = pad_left + i * bar_w
            val = vmin + i * width
            self.canvas.create_text(x, pad_top + plot_h + 15,
                                    text=f"{val:.2f}",
                                    font=("Arial", 9), angle=45)

        # подписи осей
        self.canvas.create_text(pad_left + plot_w / 2, H - 10,
                                text="Время", font=("Arial", 12))
        self.canvas.create_text(15, pad_top + plot_h / 2,
                                text="Частота", font=("Arial", 12),
                                angle=90)

    # ---------- «Заново» ----------
    def restart(self):
        self.root.destroy()
        import first_window
        first_window.FirstWindow().run()

    def run(self):
        self.root.mainloop()
