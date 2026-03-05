import httpx
import pytest
import respx

from cliject.api import execute_query, paginate_query

TOKEN = "test_token"
GQL_URL = "https://api.github.com/graphql"


@respx.mock
def test_execute_query_success():
    respx.post(GQL_URL).mock(return_value=httpx.Response(200, json={"data": {"viewer": {"login": "alice"}}}))
    result = execute_query(TOKEN, "{ viewer { login } }", {})
    assert result["data"]["viewer"]["login"] == "alice"


@respx.mock
def test_execute_query_http_error():
    respx.post(GQL_URL).mock(return_value=httpx.Response(401))
    with pytest.raises(httpx.HTTPStatusError):
        execute_query(TOKEN, "query", {})


@respx.mock
def test_execute_query_graphql_errors():
    respx.post(GQL_URL).mock(
        return_value=httpx.Response(200, json={"errors": [{"message": "Not found"}]})
    )
    with pytest.raises(RuntimeError, match="GraphQL error: Not found"):
        execute_query(TOKEN, "query", {})


@respx.mock
def test_execute_query_sends_auth_header():
    route = respx.post(GQL_URL).mock(return_value=httpx.Response(200, json={"data": {}}))
    execute_query("my_token", "query", {})
    assert route.calls[0].request.headers["Authorization"] == "Bearer my_token"


@respx.mock
def test_paginate_query_single_page():
    respx.post(GQL_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "viewer": {
                        "projectsV2": {
                            "nodes": [{"id": "1", "title": "A"}],
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                        }
                    }
                }
            },
        )
    )
    results = paginate_query(TOKEN, "query", {}, ["viewer", "projectsV2"])
    assert len(results) == 1
    assert results[0]["title"] == "A"


@respx.mock
def test_paginate_query_multiple_pages():
    page1 = httpx.Response(
        200,
        json={
            "data": {
                "viewer": {
                    "projectsV2": {
                        "nodes": [{"id": "1"}],
                        "pageInfo": {"hasNextPage": True, "endCursor": "cursor1"},
                    }
                }
            }
        },
    )
    page2 = httpx.Response(
        200,
        json={
            "data": {
                "viewer": {
                    "projectsV2": {
                        "nodes": [{"id": "2"}],
                        "pageInfo": {"hasNextPage": False, "endCursor": None},
                    }
                }
            }
        },
    )
    respx.post(GQL_URL).mock(side_effect=[page1, page2])
    results = paginate_query(TOKEN, "query", {}, ["viewer", "projectsV2"])
    assert len(results) == 2
    assert results[0]["id"] == "1"
    assert results[1]["id"] == "2"


@respx.mock
def test_paginate_query_empty():
    respx.post(GQL_URL).mock(
        return_value=httpx.Response(
            200,
            json={
                "data": {
                    "viewer": {
                        "projectsV2": {
                            "nodes": [],
                            "pageInfo": {"hasNextPage": False, "endCursor": None},
                        }
                    }
                }
            },
        )
    )
    results = paginate_query(TOKEN, "query", {}, ["viewer", "projectsV2"])
    assert results == []
