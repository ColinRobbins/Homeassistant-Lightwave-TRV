"""Support for device connected via Lightwave WiFi-link hub."""
from lightwave.lightwave import LWLink
import voluptuous as vol

from homeassistant.const import CONF_HOST, CONF_LIGHTS, CONF_NAME, CONF_SWITCHES
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.discovery import async_load_platform

LIGHTWAVE_LINK = "lightwave_link"

DOMAIN = "lightwave"


CONFIG_SCHEMA = vol.Schema(
    {
        DOMAIN: vol.Schema(
            vol.All(
                cv.has_at_least_one_key(CONF_LIGHTS, CONF_SWITCHES),
                {
                    vol.Required(CONF_HOST): cv.string,
                    vol.Optional(CONF_LIGHTS, default={}): {
                        cv.string: vol.Schema({vol.Required(CONF_NAME): cv.string})
                    },
                    vol.Optional(CONF_SWITCHES, default={}): {
                        cv.string: vol.Schema({vol.Required(CONF_NAME): cv.string})
                    },
                },
            )
        )
    },
    extra=vol.ALLOW_EXTRA,
)


async def async_setup(hass, config):
    """Try to start embedded Lightwave broker."""

    host = config[DOMAIN][CONF_HOST]
    hass.data[LIGHTWAVE_LINK] = LWLink(host)

    lights = config[DOMAIN][CONF_LIGHTS]
    if lights:
        hass.async_create_task(
            async_load_platform(hass, "light", DOMAIN, lights, config)
        )

    switches = config[DOMAIN][CONF_SWITCHES]
    if switches:
        hass.async_create_task(
            async_load_platform(hass, "switch", DOMAIN, switches, config)
        )

    return True
