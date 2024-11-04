import uuid
from copy import deepcopy
from typing import Optional, Dict

from sqlglot import exp, parse_one

from src.core.utils import extract_table


class Query:
    def __init__(self, ast: exp.Expression, cte_alias: Optional[str] = None):
        self.expression: exp.Expression = ast
        self.key: str = uuid.uuid4().hex
        self.tables = extract_table(ast)
        self._alias = cte_alias

    @staticmethod
    def from_cte(cte: exp.CTE):
        return Query(cte.this, cte.alias)

    @property
    def alias(self) -> str:
        if self._alias:
            return self._alias
        return ""

    @property
    def sql(self):
        return self.expression.sql(pretty=True)

    def represent(self):
        text = f"{self.alias}\n{'-' * 50}\n{self.sql}"
        return text

    def __repr__(self):
        return self.expression.__repr__()


def _extract_queries(sql: str) -> Dict[str, Query]:
    ast = parse_one(sql)
    query_dict = {}
    alias_set = set()

    for cte in ast.ctes:
        cte = Query.from_cte(cte)
        if cte.alias in alias_set:
            raise ValueError(f"Duplicate alias found: {cte.alias}")

        alias_set.add(cte.alias)
        query_dict[cte.key] = cte

    copied_ast = deepcopy(ast)

    if isinstance(copied_ast, exp.Select) and ast.args.get("with"):
        # To extract only main query, remove with clause
        copied_ast.set("with", None)

    cte = Query(copied_ast)
    query_dict[cte.key] = cte
    return query_dict


class QueryGraph:
    def __init__(self, sql: str):
        self.sql = sql
        self.query_dict = _extract_queries(sql)
        self.graph_dict = self._to_graph_dict()

    def edges(self):
        for from_key, to_keys in self.graph_dict.items():
            for to_key in to_keys:
                yield from_key, to_key

    def _to_graph_dict(self):
        query_dict = self.query_dict
        alias_to_key_dict = {}

        for key, query in query_dict.items():
            if query.alias:
                alias_to_key_dict[query.alias] = key

        graph_dict = {}

        for key, query in query_dict.items():
            graph_dict[key] = []

            for table in query.tables:
                if table in alias_to_key_dict:
                    graph_dict[alias_to_key_dict[table]].append(key)

        return graph_dict

    def represent_all(self):
        return f"{'=' * 50}\n" + f"\n\n{'=' * 50}\n".join(
            [query.represent() for query in self.query_dict.values()]
        )
