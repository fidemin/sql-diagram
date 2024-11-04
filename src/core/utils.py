from sqlglot import exp


def extract_table(ast: exp.Expression) -> set:
    tables = set()

    if hasattr(ast, "left"):
        tables.update(extract_table(ast.left))

    if hasattr(ast, "right"):
        tables.update(extract_table(ast.right))

    if from_table := ast.args.get("from"):
        tables.add(from_table.alias_or_name)

    if joins := ast.args.get("joins"):
        for join in joins:
            tables.add(join.alias_or_name)

    return tables
