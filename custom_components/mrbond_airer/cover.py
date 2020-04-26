"""Support for MrBond Airer."""
import logging

from miio import Device
import voluptuous as vol
import homeassistant.helpers.config_validation as cv

from homeassistant.components.cover import CoverDevice, PLATFORM_SCHEMA
from homeassistant.const import CONF_HOST, CONF_NAME, CONF_TOKEN

_LOGGER = logging.getLogger(__name__)

PLATFORM_SCHEMA = PLATFORM_SCHEMA.extend(
    {
        vol.Required(CONF_HOST): cv.string,
        vol.Required(CONF_TOKEN): vol.All(cv.string, vol.Length(min=32, max=32)),
        vol.Optional(CONF_NAME): cv.string,
    }
)


async def async_setup_platform(hass, config, async_add_entities, discovery_info=None):
    """Set up the light from config."""
    host = config[CONF_HOST]
    token = config[CONF_TOKEN]
    name = config.get(CONF_NAME)
    async_add_entities([MrBondAirer(name, host, token)], True)


class MrBondAirer(CoverDevice):
    """Representation of a cover."""

    @property
    def current_cover_position(self):
        """Return current position of cover.

        None is unknown, 0 is closed, 100 is fully open.
        """
        pass

    @property
    def current_cover_tilt_position(self):
        """Return current position of cover tilt.

        None is unknown, 0 is closed, 100 is fully open.
        """
        pass

    @property
    def state(self):
        """Return the state of the cover."""
        if self.is_opening:
            return STATE_OPENING
        if self.is_closing:
            return STATE_CLOSING

        closed = self.is_closed

        if closed is None:
            return None

        return STATE_CLOSED if closed else STATE_OPEN

    @property
    def state_attributes(self):
        """Return the state attributes."""
        data = {}

        current = self.current_cover_position
        if current is not None:
            data[ATTR_CURRENT_POSITION] = self.current_cover_position

        current_tilt = self.current_cover_tilt_position
        if current_tilt is not None:
            data[ATTR_CURRENT_TILT_POSITION] = self.current_cover_tilt_position

        return data

    @property
    def supported_features(self):
        """Flag supported features."""
        supported_features = SUPPORT_OPEN | SUPPORT_CLOSE | SUPPORT_STOP

        if self.current_cover_position is not None:
            supported_features |= SUPPORT_SET_POSITION

        if self.current_cover_tilt_position is not None:
            supported_features |= (
                SUPPORT_OPEN_TILT
                | SUPPORT_CLOSE_TILT
                | SUPPORT_STOP_TILT
                | SUPPORT_SET_TILT_POSITION
            )

        return supported_features

    @property
    def is_opening(self):
        """Return if the cover is opening or not."""
        pass

    @property
    def is_closing(self):
        """Return if the cover is closing or not."""
        pass

    @property
    def is_closed(self):
        """Return if the cover is closed or not."""
        raise NotImplementedError()

    def open_cover(self, **kwargs: Any) -> None:
        """Open the cover."""
        raise NotImplementedError()

    async def async_open_cover(self, **kwargs):
        """Open the cover."""
        await self.hass.async_add_job(ft.partial(self.open_cover, **kwargs))

    def close_cover(self, **kwargs: Any) -> None:
        """Close cover."""
        raise NotImplementedError()

    async def async_close_cover(self, **kwargs):
        """Close cover."""
        await self.hass.async_add_job(ft.partial(self.close_cover, **kwargs))

    def toggle(self, **kwargs: Any) -> None:
        """Toggle the entity."""
        if self.is_closed:
            self.open_cover(**kwargs)
        else:
            self.close_cover(**kwargs)

    async def async_toggle(self, **kwargs):
        """Toggle the entity."""
        if self.is_closed:
            await self.async_open_cover(**kwargs)
        else:
            await self.async_close_cover(**kwargs)

    def set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        pass

    async def async_set_cover_position(self, **kwargs):
        """Move the cover to a specific position."""
        await self.hass.async_add_job(ft.partial(self.set_cover_position, **kwargs))

    def stop_cover(self, **kwargs):
        """Stop the cover."""
        pass

    async def async_stop_cover(self, **kwargs):
        """Stop the cover."""
        await self.hass.async_add_job(ft.partial(self.stop_cover, **kwargs))

    def open_cover_tilt(self, **kwargs: Any) -> None:
        """Open the cover tilt."""
        pass

    async def async_open_cover_tilt(self, **kwargs):
        """Open the cover tilt."""
        await self.hass.async_add_job(ft.partial(self.open_cover_tilt, **kwargs))

    def close_cover_tilt(self, **kwargs: Any) -> None:
        """Close the cover tilt."""
        pass

    async def async_close_cover_tilt(self, **kwargs):
        """Close the cover tilt."""
        await self.hass.async_add_job(ft.partial(self.close_cover_tilt, **kwargs))

    def set_cover_tilt_position(self, **kwargs):
        """Move the cover tilt to a specific position."""
        pass

    async def async_set_cover_tilt_position(self, **kwargs):
        """Move the cover tilt to a specific position."""
        await self.hass.async_add_job(
            ft.partial(self.set_cover_tilt_position, **kwargs)
        )

    def stop_cover_tilt(self, **kwargs):
        """Stop the cover."""
        pass

    async def async_stop_cover_tilt(self, **kwargs):
        """Stop the cover."""
        await self.hass.async_add_job(ft.partial(self.stop_cover_tilt, **kwargs))

    def toggle_tilt(self, **kwargs: Any) -> None:
        """Toggle the entity."""
        if self.current_cover_tilt_position == 0:
            self.open_cover_tilt(**kwargs)
        else:
            self.close_cover_tilt(**kwargs)

    async def async_toggle_tilt(self, **kwargs):
        """Toggle the entity."""
        if self.current_cover_tilt_position == 0:
            await self.async_open_cover_tilt(**kwargs)
        else:
            await self.async_close_cover_tilt(**kwargs)
