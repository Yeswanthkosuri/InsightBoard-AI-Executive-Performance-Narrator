def test_frontend_index_serves_html(client) -> None:
    response = client.get("/")

    assert response.status_code == 200
    assert "text/html" in response.headers["content-type"]
    assert "Executive KPI Narratives from a Single CSV Upload" in response.text


def test_frontend_static_assets_are_served(client) -> None:
    response = client.get("/static/app.js")

    assert response.status_code == 200
    assert "javascript" in response.headers["content-type"]
    assert "generate-report" in response.text
