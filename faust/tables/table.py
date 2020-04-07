"""Table (key/value changelog stream)."""
import time
from typing import Any, ClassVar, Type

from mode import Seconds, get_logger

from faust import windows
from faust.streams import current_event
from faust.types.tables import KT, TableT, VT, WindowWrapperT
from faust.types.windows import WindowT
from faust.utils.terminal.tables import dict_as_ansitable

from . import wrappers
from .base import Collection

logger = get_logger(__name__)


__all__ = ['Table']


class Table(TableT[KT, VT], Collection):
    """Table (non-windowed)."""

    WindowWrapper: ClassVar[Type[WindowWrapperT]] = wrappers.WindowWrapper

    def using_window(self, window: WindowT, *,
                     key_index: bool = False) -> WindowWrapperT:
        """Wrap table using a specific window type."""
        self.window = window
        self._changelog_compacting = True
        self._changelog_deleting = True
        self._changelog_topic = None  # will reset on next property access
        return self.WindowWrapper(self, key_index=key_index)

    def hopping(self, size: Seconds, step: Seconds,
                expires: Seconds = None,
                key_index: bool = False) -> WindowWrapperT:
        """Wrap table in a hopping window."""
        return self.using_window(
            windows.HoppingWindow(size, step, expires),
            key_index=key_index,
        )

    def tumbling(self, size: Seconds,
                 expires: Seconds = None,
                 key_index: bool = False) -> WindowWrapperT:
        """Wrap table in a tumbling window."""
        return self.using_window(
            windows.TumblingWindow(size, expires),
            key_index=key_index,
        )

    def __missing__(self, key: KT) -> VT:
        if self.default is not None:
            return self.default()
        raise KeyError(key)

    def _has_key(self, key: KT) -> bool:
        return key in self

    def _get_key(self, key: KT) -> VT:
        return self[key]

    def _set_key(self, key: KT, value: VT) -> None:
        self[key] = value

    def _del_key(self, key: KT) -> None:
        del self[key]

    def on_key_get(self, key: KT) -> None:
        """Call when the value for a key in this table is retrieved."""
        self._sensor_on_get(self, key)

    def on_key_set(self, key: KT, value: VT) -> None:
        """Call when the value for a key in this table is set."""
        start = time.time()
        event = current_event()
        if event is None:
            raise TypeError(
                'Setting table key from outside of stream iteration')
        self._send_changelog(event, key, value)
        partition = event.message.partition
        self._maybe_set_key_ttl(key, partition)
        self._sensor_on_set(self, key, value)
        logger.info('on_key_set took %ss', time.time() - start)

    def on_key_del(self, key: KT) -> None:
        """Call when a key in this table is removed."""
        event = current_event()
        if event is None:
            raise TypeError(
                'Deleting table key from outside of stream iteration')
        self._send_changelog(event, key, value=None, value_serializer='raw')
        partition = event.message.partition
        self._maybe_del_key_ttl(key, partition)
        self._sensor_on_del(self, key)

    def as_ansitable(self, title: str = '{table.name}',
                     **kwargs: Any) -> str:
        """Draw table as a a terminal ANSI table."""
        return dict_as_ansitable(
            self,
            title=title.format(table=self),
            **kwargs)
