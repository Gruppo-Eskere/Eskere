import httpx

from app.config import get_settings


async def current_weather(latitude: float, longitude: float) -> dict | None:
    base_url = get_settings().external_api_base_url.rstrip("/")
    url = f"{base_url}/forecast"
    async with httpx.AsyncClient(timeout=5.0) as client:
        response = await client.get(
            url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": "temperature_2m,precipitation,weather_code",
            },
        )
        response.raise_for_status()
        return response.json().get("current")
