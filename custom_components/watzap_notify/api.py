import aiohttp
import logging

_LOGGER = logging.getLogger(__name__)

API_BASE_URL = "https://api.watzap.id/v1"

class WatzapApiClient:
    """Kelas untuk berinteraksi dengan API Watzap.id."""

    def __init__(self, api_key: str, number_key: str, session: aiohttp.ClientSession):
        """Inisialisasi client API."""
        self._api_key = api_key
        self._number_key = number_key
        self._session = session
        self._headers = {"Content-Type": "application/json"}

    async def _post_request(self, endpoint: str, data: dict):
        """Fungsi helper untuk mengirim POST request."""
        url = f"{API_BASE_URL}/{endpoint}"
        payload = {"api_key": self._api_key, "number_key": self._number_key, **data}
        try:
            async with self._session.post(url, headers=self._headers, json=payload) as response:
                response.raise_for_status()
                _LOGGER.info("Watzap: Pesan berhasil dikirim ke %s", data.get("phone_no") or data.get("group_id"))
                return await response.json()
        except aiohttp.ClientError as err:
            _LOGGER.error("Watzap: Gagal mengirim pesan. Error: %s", err)
            return None

    async def send_message(self, phone_no: str, message: str):
        """Kirim pesan teks ke nomor pribadi."""
        return await self._post_request("send_message", {"phone_no": phone_no, "message": message})

    async def send_image_url(self, phone_no: str, url: str, message: str, separate_caption: int):
        """Kirim gambar dari URL ke nomor pribadi."""
        return await self._post_request("send_image_url", {
            "phone_no": phone_no,
            "url": url,
            "message": message,
            "separate_caption": separate_caption
        })

    async def send_message_group(self, group_id: str, message: str):
        """Kirim pesan teks ke grup."""
        return await self._post_request("send_message_group", {"group_id": group_id, "message": message})
        
    async def send_image_group(self, group_id: str, url: str, message: str, separate_caption: int):
        """Kirim gambar dari URL ke grup."""
        return await self._post_request("send_image_group", {
            "group_id": group_id,
            "url": url,
            "message": message,
            "separate_caption": separate_caption
        })