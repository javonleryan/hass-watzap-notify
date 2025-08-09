# custom_components/watzap/__init__.py
import logging
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .api import WatzapApiClient

_LOGGER = logging.getLogger(__name__)

async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Watzap from a config entry."""
    hass.data.setdefault(DOMAIN, {})
    
    # Buat instance API client
    session = async_get_clientsession(hass)
    client = WatzapApiClient(
        api_key=entry.data["api_key"],
        number_key=entry.data["number_key"],
        session=session
    )
    hass.data[DOMAIN][entry.entry_id] = client

    # Ambil nilai default dari konfigurasi yang disimpan
    default_phone_no = entry.data.get("phone_no")
    default_group_id = entry.data.get("group_id")

    # Log nilai default saat startup untuk memudahkan debugging
    _LOGGER.info(
        "Watzap integration loaded. Default Phone: %s, Default Group: %s",
        default_phone_no,
        default_group_id
    )

    # ----- HANDLER UNTUK SETIAP SERVICE -----

    async def handle_send_message(call: ServiceCall):
        """Handle the send_message service call."""
        message = call.data["message"]
        phone_no = call.data.get("phone_no", default_phone_no)
        
        if not phone_no:
            _LOGGER.error("Watzap Gagal: 'phone_no' harus diisi di service call atau di konfigurasi default integrasi.")
            return
        await client.send_message(phone_no=phone_no, message=message)

    async def handle_send_image_url(call: ServiceCall):
        """Handle the send_image_url service call."""
        phone_no = call.data.get("phone_no", default_phone_no)

        if not phone_no:
            _LOGGER.error("Watzap Gagal: 'phone_no' harus diisi di service call atau di konfigurasi default integrasi.")
            return
            
        await client.send_image_url(
            phone_no=phone_no,
            url=call.data["url"],
            message=call.data["message"],
            separate_caption=call.data.get("separate_caption", 0)
        )

    async def handle_send_message_group(call: ServiceCall):
        """Handle the send_message_group service call."""
        message = call.data["message"]
        group_id = call.data.get("group_id", default_group_id)

        if not group_id:
            _LOGGER.error("Watzap Gagal: 'group_id' harus diisi di service call atau di konfigurasi default integrasi.")
            return
            
        await client.send_message_group(group_id=group_id, message=message)

    async def handle_send_image_group(call: ServiceCall):
        """Handle the send_image_group service call."""
        group_id = call.data.get("group_id", default_group_id)

        if not group_id:
            _LOGGER.error("Watzap Gagal: 'group_id' harus diisi di service call atau di konfigurasi default integrasi.")
            return
            
        await client.send_image_group(
            group_id=group_id,
            url=call.data["url"],
            message=call.data["message"],
            separate_caption=call.data.get("separate_caption", 0)
        )

    # ----- DAFTARKAN SEMUA SERVICE KE HOME ASSISTANT -----
    hass.services.async_register(DOMAIN, "send_message", handle_send_message)
    hass.services.async_register(DOMAIN, "send_image_url", handle_send_image_url)
    hass.services.async_register(DOMAIN, "send_message_group", handle_send_message_group)
    hass.services.async_register(DOMAIN, "send_image_group", handle_send_image_group)

    # Simpan listener agar bisa dihapus saat unload
    entry.async_on_unload(lambda: hass.services.async_remove(DOMAIN, "send_message"))
    entry.async_on_unload(lambda: hass.services.async_remove(DOMAIN, "send_image_url"))
    entry.async_on_unload(lambda: hass.services.async_remove(DOMAIN, "send_message_group"))
    entry.async_on_unload(lambda: hass.services.async_remove(DOMAIN, "send_image_group"))
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # Hapus data client dari hass.data
    if entry.entry_id in hass.data[DOMAIN]:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    # Proses unload service sudah ditangani oleh entry.async_on_unload di atas
    # sehingga tidak perlu ditulis ulang di sini.
    
    return True