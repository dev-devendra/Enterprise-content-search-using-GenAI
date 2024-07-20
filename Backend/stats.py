import os, pickle

#stats storage
stats = {}
stats_path = './db/stats.pickle'
if os.path.exists(stats_path):
    with open(stats_path, 'rb') as f:
        stats = pickle.load(f)
else:
    stats = {
        "cost":5,
        "total_queries":500,
        "liked":25,
        "disliked":2
    }

def serialize_stats():
    with open(stats_path, 'wb') as f:
        pickle.dump(stats,f)

def update_openapi_cost(val):
    global stats
    stats['cost'] = stats['cost'] + val
    serialize_stats()

def increment_query_count():
    global stats
    stats['total_queries'] += 1
    serialize_stats()
    
def update_user_feedback(like):
    global stats
    if like:
        stats['liked'] = stats['liked'] + 1
    else:
        stats['disliked'] = stats['disliked'] + 1
    serialize_stats()

def get_stats():
    global stats
    return stats
