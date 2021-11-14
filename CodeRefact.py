import sys
import json
import os
import re
import argparse

source_files_dir = "C:\\Users\\home\\OneDrive\\Repos\\ViPNetEDI\\ViPNetEDI_3\\src"
source_files_cp = "utf-8"
source_files_ext = ["bsl"]

rules_dict = dict()

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


def create_parser():

    arg_parser = argparse.ArgumentParser(
        prog='coderefact',
        description='''Рефакторинг исходного кода модулей с английского на русский согласно описанных правил.
                        Правила находятся в файле в формате json, имя файла передаются программе через параметр --rules  
                        ''',
        epilog='''ZAA 2021. Автор, как обычно, ни перед кем, ничего, никогда :)'''
    )
    # parser.add_argument('-r', '--rules', type=argparse.FileType(), default="RefactoringRules.json")
    arg_parser.add_argument('-r', '--rules', default="RefactoringRules.json", metavar="ПУТЬ",
                            help="Путь к файлу с правилами (по умолчанию \"RefactoringRules.json\" в текущем каталоге)")
    return arg_parser


def read_rules(file_name: str) -> dict:
    """ Читает правила рефакторинга из JSON файла

    :param file_name: str
    :return: dict
    """
    with open(file_name, "r", encoding="utf-8") as rules_file:
        data = {key: value for key, value in json.load(rules_file).items() if value.get("isApply", 0) == 1}
    return data


def apply_rule(text: str, rule: dict):
    """ Обрабатывает текст согласно переданному правилу

        :param text: str
        :param rule: dict
        :return: str
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
    """ Изменяет имена встроенных функций платформы c английского на русский

    :param text: str
    :return: str
    """
    for key, value in dict_functions_name.items():
        # ([ = <> (])(TypeOf)\(
        regex = r"([ =<>(])("+ key + ")\("
        replace_to = r"\1"+ value + "("
        text = re.sub(regex, replace_to, text, 0, re.MULTILINE | re.IGNORECASE)

    return text


def refactoring_module(file_path: str):
    """ Обрабатывает содержимое переданного по имени файла
    Args:
        file_path (str): Путь к обрабатываемому файлу
    """
    print(f"Refactoring file: {file_path}".format(file_path=file_path))
    text = ""
    with open(file_path, "r", encoding=source_files_cp) as f:
        text = f.read()

    for rule_value in rules_dict.values():
        text = apply_rule(text, rule_value)

    text = refactoring_functions_name(text)

    with open(file_path, "w", encoding=source_files_cp) as f:
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

    parser = create_parser()
    namespace = parser.parse_args(sys.argv[1:])

    rules_filepath = namespace.re_rules
    if not os.path.isfile(rules_filepath):
        print(f"Файл правил \"{rules_filepath}\" не существует.")
        exit(-1)

    print(f"Файл правил: {rules_filepath}.")

    rules_dict = read_rules(rules_filepath)
    refactoring_all(source_files_dir)
