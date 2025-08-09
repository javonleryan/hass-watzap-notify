import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from .const import DOMAIN
from .api import WatzapApiClient

class WatzapConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Watzap."""

    VERSION = 1

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            session = async_get_clientsession(self.hass)
            client = WatzapApiClient(user_input["api_key"], user_input["number_key"], session)
            
            return self.async_create_entry(title="Watzap Notifier", data=user_input)

        data_schema = vol.Schema({
            vol.Required("api_key"): str,
            vol.Required("number_key"): str,
            vol.Optional("phone_no"): str,
            vol.Optional("group_id"): str,
        })

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={
                "link_watzap": "https://watzap.id/pricing"
            }
        )