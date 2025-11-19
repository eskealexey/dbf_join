import json
import tkinter as tk
from datetime import date
from datetime import datetime
from tkinter import ttk, filedialog, messagebox, scrolledtext

import dbf
from dbfread import DBF


class DBFConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Объединение DBF")
        self.root.geometry("800x700")

        # Переменные для хранения путей к файлам
        self.dbf1_var = tk.StringVar()
        self.dbf2_var = tk.StringVar()
        self.output_json_var = tk.StringVar(value="final_merged.json")
        self.output_dbf_var = tk.StringVar(value="output.dbf")

        self.field_defs_var = tk.StringVar(value=(
            "LC:C:6,FM:C:23,IM:C:21,OT:C:21,REM:C:10,GOD:C:4,"
            "N:C:2,KOD_OTKR:C:4,DAT_OTKR:D,KOD_ZAKR:C:11,DAT_ZAKR:D,"
            "DATR:D,VPEN:C:3,SNAZN:N:10:2,D_YXOD:D,D_DESTR:D,"
            "VPN:C:3,CART:C:2,DNASN:D"
        ))

        self.setup_ui()

    def setup_ui(self):
        # Создаем основную рамку
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Настройка весов для растягивания
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)

        # Заголовок
        # title_label = ttk.Label(main_frame, text="Конвертер DBF ↔ JSON",
        #                         font=("Arial", 16, "bold"))
        # title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))

        # Секция входных файлов
        input_frame = ttk.LabelFrame(main_frame, text="Входные файлы DBF", padding="10")
        input_frame.grid(row=1, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        input_frame.columnconfigure(1, weight=1)

        # Файл 1
        ttk.Label(input_frame, text="DBF файл 1:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(input_frame, textvariable=self.dbf1_var).grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(input_frame, text="Обзор", command=self.browse_dbf1).grid(row=0, column=2, pady=2)

        # Файл 2
        ttk.Label(input_frame, text="DBF файл 2:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(input_frame, textvariable=self.dbf2_var).grid(row=1, column=1, sticky=(tk.W, tk.E), padx=(5, 5))
        ttk.Button(input_frame, text="Обзор", command=self.browse_dbf2).grid(row=1, column=2, pady=2)

        # Секция выходных файлов
        output_frame = ttk.LabelFrame(main_frame, text="Выходные файлы", padding="10")
        output_frame.grid(row=2, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        output_frame.columnconfigure(1, weight=1)

        # JSON выход
        ttk.Label(output_frame, text="JSON файл:").grid(row=0, column=0, sticky=tk.W, pady=2)
        ttk.Entry(output_frame, textvariable=self.output_json_var).grid(row=0, column=1, sticky=(tk.W, tk.E),
                                                                        padx=(5, 5))
        ttk.Button(output_frame, text="Обзор", command=self.browse_output_json).grid(row=0, column=2, pady=2)

        # DBF выход
        ttk.Label(output_frame, text="DBF файл:").grid(row=1, column=0, sticky=tk.W, pady=2)
        ttk.Entry(output_frame, textvariable=self.output_dbf_var).grid(row=1, column=1, sticky=(tk.W, tk.E),
                                                                       padx=(5, 5))
        ttk.Button(output_frame, text="Обзор", command=self.browse_output_dbf).grid(row=1, column=2, pady=2)

        # Секция определения полей
        fields_frame = ttk.LabelFrame(main_frame, text="Определение полей DBF", padding="10")
        fields_frame.grid(row=3, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        fields_frame.columnconfigure(0, weight=1)

        fields_entry = ttk.Entry(fields_frame, textvariable=self.field_defs_var)
        fields_entry.grid(row=0, column=0, sticky=(tk.W, tk.E))

        # Кнопки управления
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=4, column=0, columnspan=3, pady=10)

        ttk.Button(button_frame, text="Выполнить конвертацию",
                   command=self.run_conversion, style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Очистить",
                   command=self.clear_all).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Выход",
                   command=self.root.quit).pack(side=tk.LEFT, padx=5)

        # Лог выполнения
        log_frame = ttk.LabelFrame(main_frame, text="Лог выполнения", padding="10")
        log_frame.grid(row=5, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 10))
        log_frame.columnconfigure(0, weight=1)
        log_frame.rowconfigure(0, weight=1)
        main_frame.rowconfigure(5, weight=1)

        self.log_text = scrolledtext.ScrolledText(log_frame, height=15, width=80)
        self.log_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))

        # Статус бар
        self.status_var = tk.StringVar(value="Готов к работе")
        status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief=tk.SUNKEN)
        status_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E))

    def browse_dbf1(self):
        filename = filedialog.askopenfilename(
            title="Выберите DBF файл 1",
            filetypes=[("DBF files", "*.dbf"), ("All files", "*.*")]
        )
        if filename:
            self.dbf1_var.set(filename)

    def browse_dbf2(self):
        filename = filedialog.askopenfilename(
            title="Выберите DBF файл 2",
            filetypes=[("DBF files", "*.dbf"), ("All files", "*.*")]
        )
        if filename:
            self.dbf2_var.set(filename)

    def browse_output_json(self):
        filename = filedialog.asksaveasfilename(
            title="Сохранить JSON файл как",
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if filename:
            self.output_json_var.set(filename)

    def browse_output_dbf(self):
        filename = filedialog.asksaveasfilename(
            title="Сохранить DBF файл как",
            defaultextension=".dbf",
            filetypes=[("DBF files", "*.dbf"), ("All files", "*.*")]
        )
        if filename:
            self.output_dbf_var.set(filename)

    def clear_all(self):
        self.dbf1_var.set("")
        self.dbf2_var.set("")
        self.output_json_var.set("final_merged.json")
        self.output_dbf_var.set("output.dbf")
        self.log_text.delete(1.0, tk.END)
        self.status_var.set("Поля очищены")

    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update()

    def run_conversion(self):
        try:
            self.log_text.delete(1.0, tk.END)
            self.status_var.set("Выполняется конвертация...")

            dbf1 = self.dbf1_var.get().strip()
            dbf2 = self.dbf2_var.get().strip()

            if not dbf1 or not dbf2:
                messagebox.showerror("Ошибка", "Пожалуйста, выберите оба DBF файла")
                return

            # Конфигурация
            INPUT_FILES = [dbf1, dbf2]
            OUTPUT_JSON = self.output_json_var.get().strip()
            OUTPUT_DBF = self.output_dbf_var.get().strip()
            FIELD_DEFS = self.field_defs_var.get().strip()

            self.log_message("=" * 50)
            self.log_message("НАЧАЛО КОНВЕРТАЦИИ")
            self.log_message("=" * 50)

            # Выполнение конвейера
            json_files = []
            for i, dbf_file in enumerate(INPUT_FILES, 1):
                self.log_message(f"Обработка DBF файла {i}: {dbf_file}")
                json_file = f'temp_{i}.json'
                result = self.dbf_to_json(dbf_file, json_file)
                json_files.append(json_file)
                self.log_message(f"Создан JSON файл: {json_file} ({len(result)} записей)")

            # Объединение
            if len(json_files) == 2:
                self.log_message("Объединение JSON файлов...")
                result = self.smart_json_merge(json_files[0], json_files[1], OUTPUT_JSON)
                if result:
                    self.log_message(f"Объединенный JSON сохранен: {OUTPUT_JSON}")

            # Конвертация обратно
            self.log_message("Создание DBF файла...")
            self.json_to_dbf_corrected(OUTPUT_JSON, OUTPUT_DBF, FIELD_DEFS)

            self.log_message("=" * 50)
            self.log_message("КОНВЕРТАЦИЯ УСПЕШНО ЗАВЕРШЕНА!")
            self.log_message("=" * 50)
            self.status_var.set("Конвертация завершена успешно!")

            messagebox.showinfo("Успех", "Конвейер выполнен успешно!")

        except Exception as e:
            error_msg = f"Ошибка в основном потоке: {e}"
            self.log_message(f"ОШИБКА: {error_msg}")
            self.status_var.set("Ошибка при выполнении")
            messagebox.showerror("Ошибка", error_msg)

    # ------ код отвечающий за создание json из dbf
    def dbf_to_json(self, dbf_file_path, json_file_path):
        self.log_message(f"Чтение DBF: {dbf_file_path}")
        table = DBF(dbf_file_path, encoding='cp866')

        result = {}

        for record in table:
            first_column = list(record.keys())[0]
            key = record[first_column]

            processed_record = {}
            for field_name, value in record.items():
                if isinstance(value, (datetime, date)):
                    processed_record[field_name] = value.strftime("%d.%m.%Y")
                else:
                    processed_record[field_name] = value

            result[str(key)] = processed_record

        with open(json_file_path, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        return result

    # ------- код отвечающий за объединение json файлов
    def smart_json_merge(self, file1, file2, output_file):
        try:
            self.log_message(f"Чтение {file1}")
            with open(file1, 'r', encoding='utf-8') as f:
                data1 = json.load(f)

            self.log_message(f"Чтение {file2}")
            with open(file2, 'r', encoding='utf-8') as f:
                data2 = json.load(f)

            if not isinstance(data1, dict) or not isinstance(data2, dict):
                raise ValueError("Оба файла должны содержать JSON объекты (словари)")

            if data1 and data2:
                sample_key1 = next(iter(data1))
                sample_key2 = next(iter(data2))

                if isinstance(data1[sample_key1], dict) and isinstance(data2[sample_key2], dict):
                    keys1 = set(data1[sample_key1].keys())
                    keys2 = set(data2[sample_key2].keys())

                    if keys1 != keys2:
                        self.log_message("Предупреждение: структуры записей различаются")
                        self.log_message(f"Общие поля: {keys1 & keys2}")
                        self.log_message(f"Уникальные в file1: {keys1 - keys2}")
                        self.log_message(f"Уникальные в file2: {keys2 - keys1}")

            merged_data = {}
            merged_data.update(data1)
            merged_data.update(data2)

            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(merged_data, f, ensure_ascii=False, indent=2)

            common_keys = set(data1.keys()) & set(data2.keys())
            unique_in_file1 = set(data1.keys()) - set(data2.keys())
            unique_in_file2 = set(data2.keys()) - set(data1.keys())

            self.log_message("ОТЧЕТ ОБ ОБЪЕДИНЕНИИ")
            self.log_message(f"Файл 1: {len(data1)} записей")
            self.log_message(f"Файл 2: {len(data2)} записей")
            self.log_message(f"Результат: {len(merged_data)} записей")
            self.log_message(f"Общие ключи: {len(common_keys)}")
            self.log_message(f"Уникальные в file1: {len(unique_in_file1)}")
            self.log_message(f"Уникальные в file2: {len(unique_in_file2)}")

            return merged_data

        except Exception as e:
            self.log_message(f"Ошибка при объединении: {e}")
            return None

    def parse_field_definitions(self, field_defs_str):
        field_definitions = []
        fields = [f.strip() for f in field_defs_str.split(',') if f.strip()]

        for field in fields:
            if ':' in field:
                parts = [p.strip() for p in field.split(':')]
            else:
                parts = [p.strip() for p in field.split()]

            if len(parts) < 2:
                continue

            field_name = parts[0]
            field_type = parts[1].upper()

            if field_type == 'C':
                length = int(parts[2]) if len(parts) >= 3 else 254
                field_def = f"{field_name} C({length})"

            elif field_type in ('N', 'F'):
                if len(parts) >= 4:
                    length = int(parts[2])
                    decimals = int(parts[3])
                elif len(parts) >= 3:
                    length = int(parts[2])
                    decimals = 2
                else:
                    length = 10
                    decimals = 2
                field_def = f"{field_name} N({length},{decimals})"

            elif field_type == 'D':
                field_def = f"{field_name} D"

            elif field_type == 'L':
                field_def = f"{field_name} L"

            else:
                field_def = f"{field_name} C(100)"

            field_definitions.append(field_def)

        return field_definitions

    def clean_value(self, value, field_type):
        if value is None:
            if field_type == 'D':
                return None
            elif field_type in ('N', 'F'):
                return 0.0
            elif field_type == 'L':
                return False
            else:
                return ''

        if field_type == 'D':
            if isinstance(value, str):
                try:
                    return datetime.strptime(value.strip(), "%d.%m.%Y").date()
                except:
                    return None
            return None

        elif field_type in ('N', 'F'):
            try:
                if isinstance(value, str):
                    value = value.replace(',', '.')
                return float(value)
            except:
                return 0.0

        elif field_type == 'L':
            if isinstance(value, str):
                return value.strip().upper() in ('TRUE', 'T', 'YES', 'Y', '1', 'ON')
            return bool(value)

        else:
            return str(value) if value is not None else ''

    def json_to_dbf_corrected(self, json_file_path, dbf_file_path, field_defs_str):
        field_definitions = self.parse_field_definitions(field_defs_str)
        field_spec = ";".join(field_definitions)

        self.log_message("Создаваемые поля DBF:")
        for i, field in enumerate(field_definitions, 1):
            self.log_message(f"  {i}. {field}")

        table = dbf.Table(dbf_file_path, field_spec, codepage='cp866')
        table.open(mode=dbf.READ_WRITE)

        with open(json_file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        successful = 0

        for key, record in data.items():
            try:
                record_data = []

                for field_def in field_definitions:
                    field_name = field_def.split()[0]
                    field_type_char = field_def.split()[1][0]

                    value = record.get(field_name, '')
                    cleaned_value = self.clean_value(value, field_type_char)
                    record_data.append(cleaned_value)

                table.append(tuple(record_data))
                successful += 1

            except Exception as e:
                self.log_message(f"Ошибка в записи {key}: {e}")
                continue

        table.close()
        self.log_message(f"Успешно создано записей: {successful}")


def main():
    root = tk.Tk()
    app = DBFConverterApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()