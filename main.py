import json
import os
import re

source_files_dir = "C:\\Users\\home\\OneDrive\\Repos\\ViPNetEDI\\ViPNetEDI_3\\src"
#source_files_dir = "E:\\Work\\CodeRefact\\src"
source_files_cp = "utf-8"
source_files_ext = ["bsl"]

RE_RULES_FILE = "RefactoringRules.json"

re_rules = dict()

dict_functions_name = {
    "TypeOf": "ТипЗнч",
    "Type": "Тип",
    "Left": "Лев",
    "Right": "Прав",
    "Mid": "Сред",
    "Find": "СтрНайти",
    "StrFind": "СтрНайти",
    "StrLen": "СтрДлина",
    "IsBlankString": "ПустаяСтрока",
}

def read_re_rules(file_name: str) -> dict:
    with open(file_name, "r", encoding="utf-8") as rules_file:
        data = {key: value for key, value in json.load(rules_file).items() if value.get("isApply", 0) == 1}
    return data


def apply_rule(text: str, rule: dict):
    """ Обрабатывает текст согласно переданному правилу
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


def refactoring_functions_name(text: str):

    for key, value in dict_functions_name.items():
        # ([ = <> (])(TypeOf)\(
        regex = r"([ =<>(])("+ key + ")\("
        replace_to = r"\1"+ value + "("
        text = re.sub(regex, replace_to, text, 0, re.MULTILINE | re.IGNORECASE)

    return text


def refactoring_module(file_path: str):
    """Обрабатывает содержимое переданного по имени файла
    Args:
        file_path (str): Путь к обрабатываемому файлу
    """
    print(f"Refactoring file: {file_path}".format(file_path=file_path))
    text = ""
    with open(file_path, "r", encoding=source_files_cp) as f:
        text = f.read()

    for rule_value in re_rules.values():
        text = apply_rule(text, rule_value)

    text = refactoring_functions_name(text)

    with open(file_path, "w", encoding=source_files_cp) as f:
        f.write(text)


def refactoring_all(SourceFilesRoot: str):
    """ В переданном каталоге обрабатывает рекурсивно все файлы с заданными расширениями
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

    refactoring_all(source_files_dir)
