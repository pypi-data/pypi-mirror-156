from buz.event import Event, Subscriber
from buz.event.transactional_outbox.outbox_record import OutboxRecord
from buz.locator import Locator


class OutboxRecordToEventTranslator:
    def __init__(self, locator: Locator[Event, Subscriber]):
        self.__locator = locator

    def translate(self, outbox_record: OutboxRecord) -> Event:
        event_klass = self.__locator.get_message_klass_by_fqn(outbox_record.event_fqn)
        return event_klass.restore(
            id=outbox_record.event_id, created_at=outbox_record.parsed_created_at(), **outbox_record.event_payload
        )
