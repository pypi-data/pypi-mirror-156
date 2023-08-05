import sgqlc.types
import sgqlc.operation
import dapp_api.schema

_schema = dapp_api.schema
_schema_root = _schema.schema

__all__ = ('Operations',)


def query_leaderboard():
    _op = sgqlc.operation.Operation(_schema_root.query_type, name='Leaderboard')
    _op_top_users = _op.top_users(first=10)
    _op_top_users_nodes = _op_top_users.nodes()
    _op_top_users_nodes.user_id()
    _op_top_users_nodes.submitted_statement_count()
    return _op


class Query:
    leaderboard = query_leaderboard()


class Operations:
    query = Query
