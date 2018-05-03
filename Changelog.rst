.. _changelog:

================
 Change history
================

.. _version-1.0.1:

1.0.1
=====
:release-date: 2018-05-01 9:52 A.M PDT
:release-by: Ask Solem

- **Stream**: Fixed issue with using :keyword:`break` when iterating
  over stream.

    The last message in a stream would not be acked if the :keyword:`break`
    keyword was used::

        async for value in stream:
            if value == 3:
                break

- **Stream**: ``.take`` now acks events *after* buffer processed.

    Previously the events were erroneously acked at the time
    of entering the buffer.

    .. note::

        To accomplish this we maintain a list of events to ack
        as soon as the buffer is processed. The operation is
        ``O(n)`` where ``n`` is the size of the buffer, so please
        keep buffer sizes small (e.g. 1000).

        A large buffer will increase the chance of consistency
        issues where events are processed more than once.

- **Stream**: New ``noack`` modifier disables acking of messages in the
  stream.

    Use this to disable automatic acknowledgment of events::

        async for value in stream.noack():
            # manual acknowledgment
            await stream.ack(stream.current_event)

    .. admonition:: Manual Acknowledgement

        The stream is a sequence of events, where each event has a sequence
        number: the "offset".

        To mark an event as processed, so that we do not process it again,
        the Kafka broker will keep track of the last committed offset
        for any topic.

        This means "acknowledgement" works quite differently from other
        message brokers, such as RabbitMQ where you can selectively
        ack some messages, but not others.

        If the messages in the topic look like this sequence:

        .. sourcecode:: text

            1 2 3 4 5 6 7 8

        You can commit the offset for #5, only after processing all
        events before it. This means you MUST ack offsets (1, 2, 3, 4)
        *before* being allowed to commit 5 as the new offset.

- **Stream**: Fixed issue with ``.take`` not properly respecting the
  ``within`` argument.

    The new implementation of take now starts a background thread
    to fill the buffer. This avoids having to restart iterating
    over the stream, which caused issues.

.. _version-1.0.0:

1.0.0
=====
:release-date: 2018-04-27 4:13 P.M PDT
:release-by: Ask Solem

- **Models**: Raise error if ``Record.asdict()`` is overridden.

- **Models**: Can now override ``Record._prepare_dict`` to change the
  payload generated.

    For example if you want your model to serialize to a dictionary,
    but not have any fields with :const:`None` values, you can override
    ``_prepare_dict`` to accomplish this:

    .. sourcecode:: python

        class Quote(faust.Record):
            ask_price: float = None
            bid_price: float = None

            def _prepare_dict(self, data):
                # Remove keys with None values from payload.
                return {k: v for k, v in data.items() if v is not None}

        assert Quote(1.0, None).asdict() == {'ask_price': 1.0}

- **Stream**: Removed annoying ``Flight Recorder`` logging that was too noisy.

.. _version-0.9.65:

0.9.65
======
:release-date: 2018-04-27 2:04 P.M PDT
:release-by: Vineet Goel

- **Producer**: New setting to configure compression.

  + See :setting:`producer_compression_type`.

- **Documentation**: New :ref:`settings-producer` section.

.. _version-0.9.64:

0.9.64
======
:release-date: 2018-04-26 4:48 P.M PDT
:release-by: Ask Solem

- **Models**: Optimization for ``FieldDescriptor.__get__``.

- **Serialization**: Optimization for :mod:`faust.utils.json`.

.. _version-0.9.63:

0.9.63
======
:release-date: 2018-04-26 04:32 P.M PDT
:release-by: Vineet Goel

- **Requirements**:

    + Now depends on :pypi:`aiokafka` 0.4.5 (Robinhood fork).

- **Models**: ``Record.asdict()`` and ``to_representation()`` were slow
  on complicated models, so we are now using code generation to optimize them.

    .. warning::

        You are no longer allowed to override ``Record.asdict()``.

.. _version-0.9.62:

0.9.62
======
:release-date: 2018-04-26 12:06 P.M PDT
:release-by: Ask Solem

- **Requirements**:

    + Now depends on :ref:`Mode 1.12.2 <mode:version-1.12.2>`.

    + Now depends on :pypi:`aiokafka` 0.4.4 (Robinhood fork).

- **Consumer**: Fixed :exc:`asyncio.base_futures.IllegalStateError` error
  in commit handler.

- **CLI**: Fixed bug when invoking worker using ``faust -A``.



-


