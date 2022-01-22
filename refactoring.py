class Rule:
    def __init__(self, rule: dict):
        self.desc = rule.get("desc", "").strip()
        self.reg_ex = rule.get("reg_ex", "").strip()
        self.replace_by = rule.get("replace_by", "").strip()
        self.is_apply = rule.get("is_aplly", False) and len(self.reg_ex) > 0

    def __str__(self):
        pass

    def __repr__(self):
        if len(self.desc.strip()) != 0:
            desc = self.desc.strip()
        elif len(self.replace_by.strip()) != 0:
            desc = f"Замена по шаблону: \"{self.reg_ex}\" --> '{self.replace_by}'"
        else:
            desc = f"Удаление по шаблону: \"{self.reg_ex}\""
        return desc
