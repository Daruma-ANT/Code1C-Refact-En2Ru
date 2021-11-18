import sys
import json
import os
import re
import argparse


def create_parser():
    arg_parser = argparse.ArgumentParser(
        prog='coderefact',
        description='''Рефакторинг исходного кода модулей с английского на русский согласно описанных правил.
                        Правила находятся в файле в формате json, имя файла передаются программе через параметр --rules  
                        ''',
        epilog='''ZAA 2021. Автор, как обычно, ни перед кем, ничего, никогда :)'''
    )
    arg_parser.add_argument('-c', '--config', default="config.json", metavar="<Файл настроек>",
                            help="Путь к файлу с настройками "
                                 "(по умолчанию \"config.json\" в текущем каталоге)")
    arg_parser.add_argument('-r', '--rules', default="refactoring_rules.json", metavar="<Файл c правилами>",
                            help="Путь к файлу с правилами  "
                                 "(по умолчанию - файл \"refactoring_rules.json\" из текущего каталога)")
    arg_parser.add_argument('-f', '--function-names', default="function_names.json", metavar="<Файл с именами функций>",
                            help="Путь к файлу со словарем функций "
                                 "(ппо умолчанию - \"function_names.json\" из текущего каталога)")
    return arg_parser


def read_json_to_dict(file_name) -> dict:
    with open(file_name, "r", encoding="utf-8") as file:
        return json.load(file)


def read_rules(file_name: str) -> dict:
    """ Читает правила рефакторинга из JSON файла

    :param file_name: str
    :return: dict
    """
    with open(file_name, "r", encoding="utf-8") as file:
        return {key: value for key, value in json.load(file).items() if value.get("isApply", True)}


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


def translate_function_names(text: str, function_names: dict):
    """ Изменяет имена встроенных функций платформы c английского на русский

    :param text: str
    :param function_names: dict: Словарь имен встроенных функций
    :return: str
    """
    for key, value in function_names.items():
        # ([ = <> (])(TypeOf)\(
        regex = r"([ =<>(])(" + key + r")\("
        replace_to = r"\1" + value + "("
        text = re.sub(regex, replace_to, text, 0, re.MULTILINE | re.IGNORECASE)

    return text


def refactoring_module(file_path: str, work_params: dict):
    """ Обрабатывает содержимое единичного файла в соответствии с правилами

        :param file_path: Путь к обрабатываемому файлу
        :param work_params: Словарь с параметрами выполнения
    """
    print(f"Refactoring file: {file_path}".format(file_path=file_path))
    with open(file_path, "r", encoding=work_params["code_page"]) as f:
        text = f.read()

    for rule_value in rules_dict.values():
        text = apply_rule(text, rule_value)

    text = translate_function_names(text, work_params["function_names"])

    with open(file_path, "w", encoding=work_params["code_page"]) as f:
        f.write(text)


def refactoring_all(work_params):
    """В переданном каталоге обрабатывает рекурсивно все файлы с заданными расширениями

    :param work_params: Словарь с параметрами обработки
    :type work_params: dict

    """
    for root, dirs, files in os.walk(work_params["root_dir"]):
        for file in files:
            if file.endswith(work_params["source_ext"]):
                refactoring_module(os.path.join(root, file), work_params)
                # return


def check_file(file_path: str, file_desc: str) -> bool:
    if not os.path.isfile(file_path):
        print(f"{file_desc} \"{file_path}\" не существует.")
        return False
    else:
        print(f"{file_desc}: \"{file_path}\"...")
        return True


if __name__ == '__main__':

    parser = create_parser()
    namespace_args = parser.parse_args(sys.argv[1:])

    config_file = namespace_args.config
    if not check_file(config_file, "Файл настроек"):
        exit(-1)
    configs = read_json_to_dict(config_file)

    rules_file = namespace_args.rules
    if not check_file(rules_file, "Файл правил"):
        exit(-1)
    rules_dict = read_rules(rules_file)

    function_names_file = namespace_args.function_names
    if not check_file(function_names_file, "Файл словаря функций"):
        exit(-1)
    functions_dict = read_json_to_dict(function_names_file)

    params = {}
    sources_config = configs.get("Sources", {})
    params.setdefault("root_dir", sources_config.get("RootDir", os.getcwd()))
    params.setdefault("code_page", sources_config.get("CodePage", "utf-8"))
    params.setdefault("source_ext", sources_config.get("FilesExt", "bsl"))
    params.setdefault("rules", rules_dict)
    params.setdefault("function_names", functions_dict)

    refactoring_all(params)
