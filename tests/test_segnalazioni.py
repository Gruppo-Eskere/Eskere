def test_user_can_create_edit_and_delete_own_report(client):
    client.post(
        "/auth/login",
        data={"email": "driver@example.invalid", "password": "Driver-Password-123"},
    )
    created = client.post(
        "/impianti/1/segnalazioni",
        data={"testo_libero": "Prezzo esposto diverso dal prezzo comunicato."},
        follow_redirects=False,
    )
    assert created.status_code == 303
    detail = client.get("/impianti/1")
    assert "Prezzo esposto diverso" in detail.text

    edited = client.post(
        "/segnalazioni/1/modifica",
        data={"testo_libero": "Prezzo aggiornato, colonnina disponibile."},
        follow_redirects=False,
    )
    assert edited.status_code == 303
    assert "Prezzo aggiornato" in client.get("/impianti/1").text

    deleted = client.post("/segnalazioni/1/elimina", follow_redirects=False)
    assert deleted.status_code == 303
    assert "Prezzo aggiornato" not in client.get("/impianti/1").text


def test_users_cannot_edit_other_users_reports(client):
    client.post(
        "/auth/login",
        data={"email": "driver@example.invalid", "password": "Driver-Password-123"},
    )
    client.post(
        "/impianti/1/segnalazioni",
        data={"testo_libero": "Segnalazione di test valida."},
    )
    client.post("/auth/logout")
    client.post(
        "/auth/login",
        data={"email": "admin@example.invalid", "password": "Admin-Password-123"},
    )
    response = client.post(
        "/segnalazioni/1/modifica", data={"testo_libero": "Tentativo non autorizzato."}
    )
    assert response.status_code == 403
