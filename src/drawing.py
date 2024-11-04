import html

import graphviz

from src.core.query import QueryGraph, Query


def _set_node(dot: graphviz.Digraph, query: Query):

    if query.alias:
        alias_str = query.alias
    else:
        alias_str = ""

    sql_str = (
        html.escape(query.sql).replace("\n", '<BR ALIGN="LEFT"/>')
        + '<BR ALIGN="LEFT"/>'
    )

    node_body = f"""<
    <TABLE BORDER="1" CELLBORDER="1" CELLSPACING="0" CELLPADDING="10" >
        <TR>
            <TD><B> {alias_str} </B></TD>
        </TR>
        <TR>
            <TD>{sql_str}</TD>
        </TR>
    </TABLE>>"""

    dot.node(query.key, node_body)


def build_dot(sql: str, dot: graphviz.Digraph):
    dot.attr("node", shape="plaintext", margin="0.05")

    query_graph = QueryGraph(sql)

    for key, query in query_graph.query_dict.items():
        _set_node(dot, query)

    for from_key, to_key in query_graph.edges():
        dot.edge(from_key, to_key)
