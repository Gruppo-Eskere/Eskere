def test_search_filters_station_and_orders_prices(client):
    response = client.get("/impianti?comune=Torino&provincia=TO&carburante=Benzina&modalita=self")
    assert response.status_code == 200
    assert "Stazione Test" in response.text
    assert "€ 1.750/l" in response.text
    assert "Nessun impianto trovato" not in response.text


def test_admin_can_create_station_and_price(client):
    client.post(
        "/auth/login",
        data={"email": "admin@example.invalid", "password": "Admin-Password-123"},
    )
    response = client.post(
        "/admin/impianti",
        data={
            "id_impianto": "TEST-002", "nome": "Nuova Stazione", "gestore": "Demo",
            "bandiera": "Test", "tipo_impianto": "Stradale", "indirizzo": "Via Demo 2",
            "comune": "Alba", "provincia": "CN",
        },
        follow_redirects=False,
    )
    assert response.status_code == 303
    station_response = client.get("/impianti?comune=Alba")
    assert "Nuova Stazione" in station_response.text
