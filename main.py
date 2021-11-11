import json
import os
from pprint import pprint
import re

SourceFilesRoot = "E:\\Work\\CodeRefact\\src"
SourceFilesCodePage = "utf-8"
SourceFilesExt = ["bsl"]

# RE_RULES_FILE = "E:\\Work\\CodeRefact\\RefactoringRules.json"
RE_RULES_FILE = "RefactoringRules.json"

re_rules = dict()


def read_re_rules(file_name: str) -> dict:
    with open(file_name, "r", encoding="utf-8") as rules_file:
        data = {key:value for key, value in json.load(rules_file).items() 
                if value.get("isApply", 0) == 1}
    return data


# def clear_unused_rules(data: dict) -> dict:
#     '''Очищаем словарь от неиспользуемых правил'''
#     data = {key:value for key, value in data.items() if value.get("isApply", 0) == 1}
#     return data


def apply_rule(text: str, rule: dict) -> str:
    """ Обрабатывает текст согласно переданноиу правилу

    Args:
        text (str): Обрабатываемый текст
        rule (dict): Правило обработки

    Returns:
        str: Обработанный текст
    """
        
    regex = rule.get("RegEx", "")
    if len(regex.strip()) == 0:
        return text
    
    replace_to = rule.get("ReplaceWith", "")
    if len(replace_to.strip()) != 0:
        desc_default = f"Замена по шаблону: \"{regex}\" --> '{replace_to}'"
    else:    
        desc_default = f"Удаление по шаблону: \"{regex}\""
                        
    print(rule.get("Desc", desc_default))

    text = re.sub(regex, replace_to, text, 0, re.MULTILINE | re.IGNORECASE)
    return text


def refactoring_module(file_path:str):
    """ Обрабатывает содержимое переданного по имени файла

    Args:
        file_path (str): Путь к обрабатываемому файлу
    """    
    print(f"Refactoring file: {file_path}".format(file_path=file_path))
    text = ""
    with open(file_path, "r", encoding=SourceFilesCodePage) as f:
        text = f.read()

    for rule_value in re_rules.values():
        text = apply_rule(text, rule_value)

    with open(file_path, "w", encoding=SourceFilesCodePage) as f:
        f.write(text)


def refactoring_all(SourceFilesRoot: str):
    """В переданном каталоге обрабатывает рекурсивно все файлы с заданными расширениями

    Args:
        SourceFilesRoot (str): Корневой каталог файлов с исходными кодами
    """    
    for root, dirs, files in os.walk(SourceFilesRoot):
        for file in files:
            if file.endswith(".bsl"):
                refactoring_module(os.path.join(root, file))
                # return



if __name__ == '__main__':
    
    re_rules = read_re_rules(RE_RULES_FILE)
    
    refactoring_all(SourceFilesRoot)
