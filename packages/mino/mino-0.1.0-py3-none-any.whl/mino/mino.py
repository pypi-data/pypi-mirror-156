import ast

def convert_schema_in_file(path):
    with open(path) as f:
        file_content = f.read()

    tree = ast.parse(file_content)
    result = ""
    for target in tree.body:
        if isinstance(target, ast.ClassDef):
            classname = target.name.replace("Schema", "Class")
            result += f"class {classname}(object):\n"
            for j in target.body:
                for m in j.targets:
                    if isinstance(m.ctx, ast.Store):
                        result += f"    {m.id}: "
                result += f"{j.value.func.attr.lower()}\n"
            result += "\n\n"
    return result

def convert_schema_in_dir():
    raise NotImplementedError
