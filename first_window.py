import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import second_window


class FirstWindow:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("1")
        self.root.state("zoomed")
        self.root.option_add("*TCombobox*Listbox.font", ("Arial", 15))

        self.root.columnconfigure(0, weight=1)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(0, weight=1)

        # ===================== ЛЕВАЯ ПОЛОВИНА =====================
        left_frame = tk.Frame(self.root)
        left_frame.grid(row=0, column=0, sticky="nsew")

        left_frame.columnconfigure(0, weight=1)
        left_frame.columnconfigure(1, weight=1)
        left_frame.columnconfigure(2, weight=0)

        left_frame.rowconfigure(0, weight=1)   # распорка сверху
        left_frame.rowconfigure(10, weight=1)  # распорка снизу

        # --- Пара 1: Количество подсистем ---
        tk.Label(left_frame, text="Количество подсистем:",
                 font=("Arial", 15), anchor="e").grid(
            row=1, column=0, sticky="we", padx=(10, 0), pady=10)

        self.entry_1 = tk.Entry(left_frame, font=("Arial", 15))
        self.entry_1.grid(row=1, column=1, columnspan=2, sticky="we",
                          padx=(0, 10), pady=10)

        # --- Пара 2: Вероятность ошибки P ---
        tk.Label(left_frame, text="Вероятность ошибки, P:",
                 font=("Arial", 15), anchor="e").grid(
            row=2, column=0, sticky="we", padx=(10, 0), pady=10)

        self.entry_2 = tk.Entry(left_frame, font=("Arial", 15))
        self.entry_2.grid(row=2, column=1, columnspan=2, sticky="we",
                          padx=(0, 10), pady=10)

        # --- Пара 3: Количество имитаций N ---
        tk.Label(left_frame, text="Количество имитаций, N:",
                 font=("Arial", 15), anchor="e").grid(
            row=3, column=0, sticky="we", padx=(10, 0), pady=10)

        self.entry_3 = tk.Entry(left_frame, font=("Arial", 15))
        self.entry_3.grid(row=3, column=1, columnspan=2, sticky="we",
                          padx=(0, 10), pady=10)
        self.entry_3.insert(0, "1000")

        # --- Пара 4: Дисциплина ---
        tk.Label(left_frame, text="Дисциплина обработок ошибок:",
                 font=("Arial", 15), anchor="e").grid(
            row=4, column=0, sticky="we", padx=(10, 0), pady=10)

        self.combo_policy = ttk.Combobox(
            left_frame, font=("Arial", 15),
            values=["Начать с начала", "Начать с предыдущего", "Конец"],
            state="readonly")
        self.combo_policy.grid(row=4, column=1, columnspan=2, sticky="we",
                               padx=(0, 10), pady=10)
        self.combo_policy.current(0)

        # --- Пара 5: Файл вариантов ---
        tk.Label(left_frame, text="Файл вариантов:",
                 font=("Arial", 15), anchor="e").grid(
            row=5, column=0, sticky="we", padx=(10, 0), pady=10)

        self.variant_path = tk.StringVar()
        tk.Entry(left_frame, textvariable=self.variant_path,
                 font=("Arial", 15)).grid(row=5, column=1, sticky="we",
                                          padx=(0, 10), pady=10)

        tk.Button(left_frame, text="Обзор…", font=("Arial", 12),
                  command=self.choose_variant_file).grid(
            row=5, column=2, padx=(0, 10), pady=10)

        # --- Пара 6: Файл времён шагов ---
        tk.Label(left_frame, text="Файл времён шагов:",
                 font=("Arial", 15), anchor="e").grid(
            row=6, column=0, sticky="we", padx=(10, 0), pady=10)

        self.times_path = tk.StringVar()
        tk.Entry(left_frame, textvariable=self.times_path,
                 font=("Arial", 15)).grid(row=6, column=1, sticky="we",
                                          padx=(0, 10), pady=10)

        tk.Button(left_frame, text="Обзор…", font=("Arial", 12),
                  command=self.choose_times_file).grid(
            row=6, column=2, padx=(0, 10), pady=10)

        # --- Пара 7: Номер варианта ---
        tk.Label(left_frame, text="Номер варианта:",
                 font=("Arial", 15), anchor="e").grid(
            row=7, column=0, sticky="we", padx=(10, 0), pady=10)

        self.entry_variant = tk.Entry(left_frame, font=("Arial", 15))
        self.entry_variant.grid(row=7, column=1, columnspan=2, sticky="we",
                                padx=(0, 10), pady=10)
        self.entry_variant.insert(0, "1")

        # ===================== ПРАВАЯ ПОЛОВИНА =====================
        right_frame = tk.Frame(self.root)
        right_frame.grid(row=0, column=1, sticky="nsew")

        right_frame.columnconfigure(0, weight=1)
        right_frame.columnconfigure(1, weight=1)
        right_frame.columnconfigure(2, weight=1)

        right_frame.rowconfigure(0, weight=0)    # заголовок
        right_frame.rowconfigure(1, weight=1)    # распорка сверху
        right_frame.rowconfigure(12, weight=1)   # распорка снизу
        right_frame.rowconfigure(13, weight=0)   # строка кнопки

        title_label = tk.Label(right_frame, text="Время выполнения шага",
                               font=("Arial", 22), anchor="center")
        title_label.grid(row=1, column=0, columnspan=3, sticky="we",
                         pady=(10, 15))

        # --- 10 строк: label + entry + entry ---
        for i in range(10):
            r = i + 2
            tk.Label(right_frame, text=f"{i + 1}:", font=("Arial", 15),
                     anchor="e").grid(row=r, column=0, sticky="we",
                                      padx=(10, 5), pady=4)
            tk.Entry(right_frame, font=("Arial", 15)).grid(
                row=r, column=1, sticky="we", padx=(0, 5), pady=4)
            tk.Entry(right_frame, font=("Arial", 15)).grid(
                row=r, column=2, sticky="we", padx=(0, 10), pady=4)

        # --- Кнопка справа снизу ---
        button = tk.Button(right_frame, text="Далее", font=("Arial", 15),
                           command=self.on_click)
        button.grid(row=13, column=2, sticky="e", padx=(0, 10), pady=15)

    # ---------- Выбор файлов ----------
    def choose_variant_file(self):
        path = filedialog.askopenfilename(
            title="Выберите файл вариантов",
            filetypes=[("CSV files", "*.csv"), ("Все файлы", "*.*")])
        if path:
            self.variant_path.set(path)

    def choose_times_file(self):
        path = filedialog.askopenfilename(
            title="Выберите файл времён шагов",
            filetypes=[("CSV files", "*.csv"), ("Все файлы", "*.*")])
        if path:
            self.times_path.set(path)

    # ---------- Переход ----------
    def on_click(self):
        # N подсистем
        try:
            n_subsystems = int(self.entry_1.get().strip() or "0")
        except ValueError:
            messagebox.showerror("Ошибка",
                                 "«Количество подсистем» должно быть числом")
            return

        # N имитаций
        try:
            n_sim = int(self.entry_3.get().strip() or "1000")
        except ValueError:
            messagebox.showerror("Ошибка",
                                 "«Количество имитаций» должно быть числом")
            return
        if n_sim < 1:
            messagebox.showerror("Ошибка", "N имитаций должно быть ≥ 1")
            return

        policy = self.combo_policy.get()
        variant_id = self.entry_variant.get().strip() or "1"
        variant_file = self.variant_path.get().strip()
        variant_file = variant_file or None
        times_file = self.times_path.get().strip() or None

        self.root.destroy()
        second_window.SecondWindow(
            variant_id=variant_id,
            policy=policy,
            N_sim=n_sim,
            n_subsystems=n_subsystems,
            variant_file=variant_file,
            times_file=times_file,
        ).run()

    def run(self):
        self.root.mainloop()


if __name__ == "__main__":
    FirstWindow().run()
