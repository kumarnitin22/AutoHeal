def fetch_user_data(user_id):
    query_payload = {
        "id": user_id,
        "tags": ["active", "verified", ("priority", 1)]}
