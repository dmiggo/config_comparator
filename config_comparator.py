import os
import xml.etree.ElementTree as ET
from datetime import datetime
from tkinter import Tk, filedialog

def parse_xml(file_path):
    """Парсит XML-файл и возвращает словарь с ключами и значениями из appSettings, исключая комментарии."""
    tree = ET.parse(file_path)
    root = tree.getroot()
    settings = {}
    for elem in root.find('appSettings'):
        if elem.tag == 'add': # Исключаем комментарии
            key = elem.get('key')
            value = elem.get('value')
            settings[key] = value
    return settings, tree, root

def indent_tree(elem, level=0):
    """Добавляет отступы для дерева XML для красивого форматирования."""
    i = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for child in elem:
            indent_tree(child, level + 1)
        if not child.tail or not child.tail.strip():
            child.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

def compare_configs(file1, file2):
    # Загружаем и парсим оба файла
    settings1, tree1, root1 = parse_xml(file1)
    settings2, _, _ = parse_xml(file2)
    
    # Разделяем совпадающие и несовпадающие ключи
    matches = []
    mismatches = []
    all_keys = set(settings1.keys()).union(settings2.keys())
    
    for key in sorted(all_keys):
        value1 = settings1.get(key)
        value2 = settings2.get(key)
        if value1 == value2 and value1 is not None:
            matches.append((key, value1))
        else:
            if value1 is not None:
                mismatches.append((f"new:<add key=\"{key}\" value=\"{value1}\" />"))
            if value2 is not None:
                mismatches.append((f"old:<add key=\"{key}\" value=\"{value2}\" />"))

    # Очищаем старые записи в <appSettings> в первом файле
    app_settings = root1.find('appSettings')
    app_settings.clear()
    
    # Добавляем совпадающие ключи в начало
    for key, value in matches:
        elem = ET.Element('add')
        elem.set('key', key)
        elem.set('value', value)
        app_settings.append(elem)
    
    # Добавляем разделительную черту
    separator = ET.Comment(" ----------------------------------------------- ")
    app_settings.append(separator)
    
    # Добавляем несовпадающие строки
    for line in mismatches:
        prefix, element_str = line.split(":<")
        elem = ET.Comment(f"{prefix}")
        app_settings.append(elem)

        # Создаем элемент XML из строки с "key" и "value"
        key_value_pair = element_str.split('" ')
        key_part = key_value_pair[0].replace('add key="', '').replace('"', '')
        value_part = key_value_pair[1].replace('value="', '').replace('"', '').strip()
        
        add_elem = ET.Element('add')
        add_elem.set('key', key_part)
        add_elem.set('value', value_part)
        app_settings.append(add_elem)
    
    # Добавляем отступы к дереву для красивого форматирования
    indent_tree(root1)

    # Формируем название выходного файла с текущей датой и временем (без недопустимых символов)
    timestamp = datetime.now().strftime("%d-%b_%H-%M")
    file1_name = os.path.basename(file1)
    file2_name = os.path.basename(file2)
    output_file = f"Файл сравнения {file1_name} и {file2_name} {timestamp}.config".replace("/", "_")
    # Записываем отформатированное дерево в выходной файл
    tree1.write(output_file, encoding="utf-8", xml_declaration=True)
    print(f"Файл успешно сохранён как {output_file}")

def select_files():
    """Открывает диалог для выбора двух файлов и запускает сравнение."""
    Tk().withdraw()
    file1 = filedialog.askopenfilename(title="Выберите первый файл", filetypes=[("Config Files", "*.config")])
    file2 = filedialog.askopenfilename(title="Выберите второй файл", filetypes=[("Config Files", "*.config")])

    if file1 and file2:
        compare_configs(file1, file2)
    else:
        print("Выбор файлов отменен.")

# Запускаем выбор файлов
select_files()