

def get_gc_data(parent_key):

    query = "SELECT yg_util_pre, yg_util_post, yg_size_post, " + 
            "heap_util_pre, heap_util_post, heap_size_post "
            "FROM YoungGenGCModel " +
            "WHERE parent_key = :1"

    results = db.GqlQuery(query, parent_key).get()

    return results
    