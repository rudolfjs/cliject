import httpx

GITHUB_GRAPHQL_URL = "https://api.github.com/graphql"


def execute_query(token: str, query: str, variables: dict) -> dict:
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }
    response = httpx.post(
        GITHUB_GRAPHQL_URL,
        json={"query": query, "variables": variables},
        headers=headers,
        timeout=30,
    )
    response.raise_for_status()
    data = response.json()
    if "errors" in data:
        messages = "; ".join(e.get("message", str(e)) for e in data["errors"])
        raise RuntimeError(f"GraphQL error: {messages}")
    return data


def paginate_query(
    token: str,
    query: str,
    variables: dict,
    path_to_connection: list[str],
) -> list[dict]:
    """
    Paginate through a GraphQL connection.

    path_to_connection: list of keys to traverse from data root to the
    connection object (which must have pageInfo and nodes).
    Example: ["viewer", "projectV2", "items"]
    """
    results = []
    cursor = None

    while True:
        vars_with_cursor = {**variables, "cursor": cursor}
        data = execute_query(token, query, vars_with_cursor)

        node = data.get("data", {})
        for key in path_to_connection:
            node = node.get(key, {}) or {}

        nodes = node.get("nodes", [])
        results.extend(nodes)

        page_info = node.get("pageInfo", {})
        if not page_info.get("hasNextPage"):
            break
        cursor = page_info.get("endCursor")

    return results
