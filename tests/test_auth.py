def test_app_starts_and_homepage_renders(client):
    response = client.get("/")
    assert response.status_code == 200
    assert "BenzinaChiara" in response.text


def test_user_can_login_and_admin_route_is_role_protected(client):
    response = client.post(
        "/auth/login",
        data={"email": "driver@example.invalid", "password": "Driver-Password-123"},
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert client.get("/admin/").status_code == 403

    client.post("/auth/logout")
    client.post(
        "/auth/login",
        data={"email": "admin@example.invalid", "password": "Admin-Password-123"},
        follow_redirects=False,
    )
    assert client.get("/admin/").status_code == 200


def test_registration_creates_standard_role_account(client):
    response = client.post(
        "/auth/registrazione",
        data={
            "display_name": "Nuovo Demo",
            "email": "new@example.invalid",
            "password": "Another-Password-123",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    assert client.get("/admin/").status_code == 403
