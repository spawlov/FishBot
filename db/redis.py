import redis

_database = None


def get_database_connection(host, port, password):
    global _database
    if _database is None:
        _database = redis.Redis(host=host, port=port, password=password)
    return _database
