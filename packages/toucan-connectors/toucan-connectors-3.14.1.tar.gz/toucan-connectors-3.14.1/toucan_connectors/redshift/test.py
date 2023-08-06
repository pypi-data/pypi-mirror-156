# from typing import Any

# import redshift_connector

# HOST = "redshift-cluster-shared-sin-redshiftclusterpublic-1ayn50qyyo3cd.cdpwpbggeuti.us-west-2.redshift.amazonaws.com"
# USER = "toucan"
# PASSWORD = "89%64^tree^PLAIN^right^14+bad1"
# DATABASE = "ticketstream-live"


# def get_connection(database: str) -> redshift_connector.Connection:
#     return redshift_connector.connect(
#         host=HOST,
#         user=USER,
#         password=PASSWORD,
#         database=database,
#         timeout=10,
#     )


# def get_table_infos_rows(database: str) -> list[tuple[str, str, str, str]]:
#     with get_connection(database) as conn, conn.cursor() as cur:
#         """Get rows of (schema, table name, column name, column type)"""
#         cur.execute(
#             r"""SELECT "schemaname", "tablename", "column", "type" FROM PG_TABLE_DEF WHERE schemaname = 'public';"""
#         )
#         return cur.fetchall()


# def get_model(database: str) -> list[dict[str, Any]]:
#     """Retrieves the database tree structure using current connection"""
#     table_infos = []
#     for schema, table_name, column_name, column_type in get_table_infos_rows(database):
#         for row in table_infos[::-1]:
#             if row['schema'] == schema and row['name'] == table_name:
#                 row['columns'].append({'name': column_name, 'type': column_type})
#                 break
#         else:
#             table_infos.append(
#                 {
#                     'database': DATABASE,
#                     'schema': schema,
#                     'name': table_name,
#                     'type': 'table',
#                     'columns': [{'name': column_name, 'type': column_type}],
#                 }
#             )
#     return table_infos


from enum import Enum

from pydantic import create_model


class StrEnum(str, Enum):
    """Class to easily make schemas with enum values and type string"""


def strlist_to_enum(field: str, strlist: list[str], default_value=...) -> tuple:
    """
    Convert a list of strings to a pydantic schema enum
    the value is either <default value> or a tuple ( <type>, <default value> )
    If the field is required, the <default value> has to be '...' (cf pydantic doc)
    By default, the field is considered required.
    """
    return StrEnum(field, {v: v for v in strlist}), default_value


available_dbs = ["dev", "qweqwe", "live"]
constraints = {'database': strlist_to_enum('database', available_dbs, 'dev')}
M = create_model("FormSchema", **constraints).schema()

breakpoint()
