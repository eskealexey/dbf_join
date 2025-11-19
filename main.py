# from lib import json_to_dbf_corrected, dbf_to_json, smart_json_merge
#
# def main():
#     dbf1 = input("Введите имя файла 1: ").strip()
#     dbf2 = input("Введите имя файла 2: ").strip()
#
#     try:
#         # Конфигурация
#         INPUT_FILES = [dbf1, dbf2]
#         OUTPUT_JSON = 'final_merged.json'
#         OUTPUT_DBF = 'output.dbf'
#
#         FIELD_DEFS = (
#             "LC:C:6,FM:C:23,IM:C:21,OT:C:21,REM:C:10,GOD:C:4,"
#             "N:C:2,KOD_OTKR:C:4,DAT_OTKR:D,KOD_ZAKR:C:11,DAT_ZAKR:D,"
#             "DATR:D,VPEN:C:3,SNAZN:N:10:2,D_YXOD:D,D_DESTR:D,"
#             "VPN:C:3,CART:C:2,DNASN:D"
#         )
#
#         # Выполнение конвейера
#         json_files = []
#         for i, dbf_file in enumerate(INPUT_FILES, 1):
#             json_file = f'temp_{i}.json'
#             dbf_to_json(dbf_file, json_file)
#             json_files.append(json_file)
#
#         # Объединение
#         if len(json_files) == 2:
#             smart_json_merge(json_files[0], json_files[1], OUTPUT_JSON)
#
#         # Конвертация обратно
#         json_to_dbf_corrected(OUTPUT_JSON, OUTPUT_DBF, FIELD_DEFS)
#
#         print("✓ Конвейер выполнен успешно!")
#
#     except Exception as e:
#         print(f"✗ Ошибка в основном потоке: {e}")
#
#
# if __name__ == "__main__":
#     main()

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import json
import os
from pathlib import Path
import threading
import time
from datetime import datetime
import sys


class DBFProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DBF to JSON Converter Pro")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)

        # Иконка приложения (можно добавить файл icon.ico)
        try:
            self.root.iconbitmap("icon.ico")
        except:
            pass

        # Переменные
        self.file1_path = tk.StringVar()
        self.file2_path = tk.StringVar()
        self.output_path = tk.StringVar()
        self.is_processing = False

        self.setup_ui()

    def setup_ui(self):
        # Создаем основной контейнер с прокруткой
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # Заголовок
        header_frame = ttk.Frame(main_frame)
        header_frame.pack(fill=tk.X, pady=(0, 20))

        title_label = ttk.Label(
            header_frame,
            text="🔄 Конвертер DBF в JSON",
            font=("Arial", 16, "bold"),
            foreground="#2c3e50"
        )
        title_label.pack(pady=5)

        subtitle_label = ttk.Label(
            header_frame,
            text="Объедините два DBF файла и конвертируйте в JSON формат",
            font=("Arial", 10),
            foreground="#7f8c8d"
        )
        subtitle_label.pack()

        # Разделитель
        ttk.Separator(main_frame, orient=tk.HORIZONTAL).pack(fill=tk.X, pady=10)

        # Фрейм для загрузки файлов
        files_frame = ttk.LabelFrame(main_frame, text="📁 Загрузка файлов", padding=15)
        files_frame.pack(fill=tk.X, pady=(0, 15))

        # Поле для первого файла
        file1_frame = ttk.Frame(files_frame)
        file1_frame.pack(fill=tk.X, pady=5)

        ttk.Label(file1_frame, text="Первый DBF файл:").pack(side=tk.LEFT)
        ttk.Entry(file1_frame, textvariable=self.file1_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(file1_frame, text="Обзор", command=self.browse_file1).pack(side=tk.LEFT, padx=2)
        ttk.Button(file1_frame, text="🗑️", width=3, command=lambda: self.file1_path.set("")).pack(side=tk.LEFT)

        # Поле для второго файла
        file2_frame = ttk.Frame(files_frame)
        file2_frame.pack(fill=tk.X, pady=5)

        ttk.Label(file2_frame, text="Второй DBF файл:").pack(side=tk.LEFT)
        ttk.Entry(file2_frame, textvariable=self.file2_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(file2_frame, text="Обзор", command=self.browse_file2).pack(side=tk.LEFT, padx=2)
        ttk.Button(file2_frame, text="🗑️", width=3, command=lambda: self.file2_path.set("")).pack(side=tk.LEFT)

        # Фрейм для настроек вывода
        output_frame = ttk.LabelFrame(main_frame, text="💾 Настройки вывода", padding=15)
        output_frame.pack(fill=tk.X, pady=(0, 15))

        output_path_frame = ttk.Frame(output_frame)
        output_path_frame.pack(fill=tk.X, pady=5)

        ttk.Label(output_path_frame, text="Выходной файл:").pack(side=tk.LEFT)
        ttk.Entry(output_path_frame, textvariable=self.output_path, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(output_path_frame, text="Обзор", command=self.browse_output).pack(side=tk.LEFT, padx=2)

        # Автогенерация имени выходного файла
        ttk.Button(
            output_path_frame,
            text="🎯 Авто",
            command=self.auto_generate_output
        ).pack(side=tk.LEFT, padx=2)

        # Фрейм для кнопок управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 15))

        self.process_btn = ttk.Button(
            control_frame,
            text="🔄 Начать обработку",
            command=self.start_processing,
            style="Accent.TButton"
        )
        self.process_btn.pack(side=tk.LEFT, padx=(0, 10))

        ttk.Button(
            control_frame,
            text="🗑️ Очистить все",
            command=self.clear_all
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="📋 Копировать логи",
            command=self.copy_logs
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            control_frame,
            text="💾 Сохранить логи",
            command=self.save_logs
        ).pack(side=tk.LEFT, padx=5)

        # Прогресс-бар
        self.progress = ttk.Progressbar(
            main_frame,
            orient=tk.HORIZONTAL,
            mode='determinate',
            length=100
        )
        self.progress.pack(fill=tk.X, pady=(0, 10))

        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(
            main_frame,
            textvariable=self.status_var,
            relief=tk.SUNKEN,
            anchor=tk.W,
            padding=5
        )
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

        # Текстовое поле для логов
        log_frame = ttk.LabelFrame(main_frame, text="📝 Журнал обработки", padding=10)
        log_frame.pack(fill=tk.BOTH, expand=True)

        self.log_text = scrolledtext.ScrolledText(
            log_frame,
            wrap=tk.WORD,
            width=80,
            height=20,
            font=("Consolas", 9)
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # Добавляем контекстное меню для текстового поля
        self.setup_context_menu()

        # Запускаем мониторинг состояния кнопок
        self.update_ui_state()

    def setup_context_menu(self):
        """Добавляет контекстное меню для текстового поля логов"""
        self.context_menu = tk.Menu(self.log_text, tearoff=0)
        self.context_menu.add_command(label="Копировать", command=self.copy_selected_text)
        self.context_menu.add_command(label="Выделить все", command=self.select_all_text)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Очистить логи", command=self.clear_logs)

        self.log_text.bind("<Button-3>", self.show_context_menu)  # Right-click

    def show_context_menu(self, event):
        """Показывает контекстное меню"""
        try:
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    def copy_selected_text(self):
        """Копирует выделенный текст"""
        try:
            selected = self.log_text.get(tk.SEL_FIRST, tk.SEL_LAST)
            self.root.clipboard_clear()
            self.root.clipboard_append(selected)
        except tk.TclError:
            pass

    def select_all_text(self):
        """Выделяет весь текст в логах"""
        self.log_text.tag_add(tk.SEL, "1.0", tk.END)
        self.log_text.mark_set(tk.INSERT, "1.0")
        self.log_text.see(tk.INSERT)

    def browse_file1(self):
        filename = filedialog.askopenfilename(
            title="Выберите первый DBF файл",
            filetypes=[("DBF files", "*.dbf"), ("All files", "*.*")]
        )
        if filename:
            self.file1_path.set(filename)
            self.auto_generate_output()

    def browse_file2(self):
        filename = filedialog.askopenfilename(
            title="Выберите второй DBF файл",
            filetypes=[("DBF files", "*.dbf"), ("All files", "*.*")]
        )
        if filename:
            self.file2_path.set(filename)
            self.auto_generate_output()

    def browse_output(self):
        filename = filedialog.asksaveasfilename(
            title="Сохранить результат как",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.output_path.set(filename)

    def auto_generate_output(self):
        """Автоматически генерирует имя выходного файла"""
        if self.file1_path.get() and self.file2_path.get():
            base_name = f"merged_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            output_file = f"{base_name}.json"
            self.output_path.set(output_file)

    def clear_all(self):
        """Очищает все поля"""
        self.file1_path.set("")
        self.file2_path.set("")
        self.output_path.set("")
        self.clear_logs()
        self.update_ui_state()

    def clear_logs(self):
        """Очищает поле логов"""
        self.log_text.delete(1.0, tk.END)

    def copy_logs(self):
        """Копирует все логи в буфер обмена"""
        logs = self.log_text.get(1.0, tk.END)
        self.root.clipboard_clear()
        self.root.clipboard_append(logs)
        messagebox.showinfo("Успех", "Логи скопированы в буфер обмена")

    def save_logs(self):
        """Сохраняет логи в файл"""
        filename = filedialog.asksaveasfilename(
            title="Сохранить логи как",
            defaultextension=".log",
            filetypes=[("Log files", "*.log"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            try:
                logs = self.log_text.get(1.0, tk.END)
                with open(filename, 'w', encoding='utf-8') as f:
                    f.write(logs)
                self.log_message(f"✅ Логи сохранены в: {filename}")
            except Exception as e:
                messagebox.showerror("Ошибка", f"Не удалось сохранить логи: {e}")

    def log_message(self, message):
        """Добавляет сообщение в лог с временной меткой"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        formatted_message = f"[{timestamp}] {message}\n"

        self.log_text.insert(tk.END, formatted_message)
        self.log_text.see(tk.END)  # Автопрокрутка к новому сообщению
        self.root.update_idletasks()

    def update_ui_state(self):
        """Обновляет состояние UI элементов"""
        files_selected = bool(self.file1_path.get() and self.file2_path.get())

        if self.is_processing:
            self.process_btn.config(text="⏹️ Остановить", state=tk.NORMAL)
            self.process_btn.config(command=self.stop_processing)
        else:
            self.process_btn.config(text="🔄 Начать обработку", state=tk.NORMAL if files_selected else tk.DISABLED)
            self.process_btn.config(command=self.start_processing)

    def start_processing(self):
        """Запускает обработку в отдельном потоке"""
        if not self.file1_path.get() or not self.file2_path.get():
            messagebox.showerror("Ошибка", "Пожалуйста, выберите оба DBF файла")
            return

        if not self.output_path.get():
            self.auto_generate_output()

        self.is_processing = True
        self.update_ui_state()

        # Запускаем обработку в отдельном потоке
        thread = threading.Thread(target=self.process_files)
        thread.daemon = True
        thread.start()

    def stop_processing(self):
        """Останавливает обработку"""
        self.is_processing = False
        self.update_ui_state()
        self.log_message("⏹️ Обработка остановлена пользователем")

    def process_files(self):
        """Основная функция обработки файлов"""
        try:
            self.log_message("🚀 Начало обработки файлов...")
            self.update_progress(10)

            # Имитация обработки (замените на реальную логику)
            steps = [
                (20, "📖 Чтение первого DBF файла..."),
                (30, "📖 Чтение второго DBF файла..."),
                (50, "🔍 Проверка структуры файлов..."),
                (60, "🔄 Конвертация в JSON..."),
                (75, "🔗 Объединение данных..."),
                (85, "💾 Сохранение результата..."),
                (95, "✅ Проверка целостности...")
            ]

            for progress, message in steps:
                if not self.is_processing:
                    break

                time.sleep(1)  # Имитация работы
                self.update_progress(progress)
                self.log_message(message)

            if self.is_processing:
                self.update_progress(100)
                self.log_message(f"✅ Обработка завершена! Результат сохранен в: {self.output_path.get()}")
                messagebox.showinfo("Успех", "Обработка файлов завершена успешно!")
            else:
                self.update_progress(0)
                self.log_message("❌ Обработка прервана")

        except Exception as e:
            self.log_message(f"❌ Ошибка при обработке: {str(e)}")
            messagebox.showerror("Ошибка", f"Произошла ошибка: {str(e)}")
        finally:
            self.is_processing = False
            self.update_ui_state()

    def update_progress(self, value):
        """Обновляет прогресс-бар и статус"""
        self.progress['value'] = value
        self.status_var.set(f"Выполнено: {value}%")
        self.root.update_idletasks()


def main():
    # Создаем главное окно
    root = tk.Tk()

    # Устанавливаем стиль для современных тем
    try:
        root.tk.call("source", "azure.tcl")
        root.tk.call("set_theme", "dark")
    except:
        pass

    # Создаем приложение
    app = DBFProcessorApp(root)

    # Запускаем главный цикл
    root.mainloop()


if __name__ == "__main__":
    main()