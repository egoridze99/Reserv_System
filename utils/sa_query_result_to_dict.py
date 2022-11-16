from sqlalchemy.engine import ResultProxy


def sa_query_result_to_dict(data: 'ResultProxy'):
    return [{column: value for column, value in rowproxy.items()} for rowproxy in data]