import uuid
from typing import Optional

from sqlglot import exp


class CTE:
    def __init__(self, expression: exp.Expression, cte_alias: Optional[str] = None):
        self.expression: exp.Expression = expression
        self._cte_alias = cte_alias
        self.key: str = uuid.uuid4().hex

    @property
    def cte_alias(self) -> str:
        if self._cte_alias:
            return self._cte_alias
        return ""

    @property
    def sql(self):
        return self.expression.sql(pretty=True)

    def __repr__(self):
        return self.expression.__repr__()
