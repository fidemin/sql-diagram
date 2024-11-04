import graphviz

from src import build_dot
from src.core.query import QueryGraph

if __name__ == "__main__":
    sql = """
        WITH cte1 AS (
            SELECT a, b, COUNT(*) OVER (PARTITION BY a) AS count_a
            FROM mytable
        ),
        cte2 AS (
            SELECT c, d, ROW_NUMBER() OVER (PARTITION BY c ORDER BY d DESC) AS row_num
            FROM table2
            WHERE d > 10
        ),
        cte3 AS (
            SELECT cte1.a, cte2.c, cte1.b
            FROM cte1
            INNER JOIN cte2 ON cte1.b = cte2.c
            WHERE cte1.count_a > 1
        ),
        cte4 AS (
            SELECT a, b, c, SUM(b) OVER (PARTITION BY a) AS sum_b
            FROM (
                SELECT cte3.a, cte3.b, cte3.c
                FROM cte3
                WHERE cte3.c IS NOT NULL
            ) AS filtered_cte3
        ),
        cte5 AS (
            SELECT cte4.a, cte4.c,
                   CASE 
                       WHEN cte4.sum_b > 100 THEN 'High'
                       ELSE 'Low'
                   END AS category
            FROM cte4
        ),
        final_result AS (
            SELECT cte1.a, cte5.c, cte5.category, COALESCE(cte1.b, 0) AS b
            FROM cte1
            LEFT JOIN cte5 ON cte1.a = cte5.a
            WHERE cte1.count_a < 2
            UNION ALL
            SELECT a, c, category, b
            FROM cte5
            WHERE category = 'High'
            UNION ALL
            SELECT a, c, category, b
            FROM cte5
            WHERE category = 'Low'
        )
        SELECT *
        FROM final_result
        ORDER BY a, c
        """

    dot = graphviz.Digraph(comment="CTE and Table DAG")
    build_dot(sql, dot)
    print(QueryGraph(sql).represent_all())
    dot.render("cte_dag", format="png", cleanup=True, view=True)
