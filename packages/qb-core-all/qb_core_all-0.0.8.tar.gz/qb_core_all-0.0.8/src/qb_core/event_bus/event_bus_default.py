import asyncio
from collections import defaultdict

from qb_core.event_bus.event_bus_interface import EventBusInterface


class EventBusDefault(EventBusInterface):
    def __init__(self):
        self.listeners = defaultdict(set)

    def add_listener(self, event_name, listener):
        self.listeners[event_name].add(listener)

    # I don't think I need this
    # def remove_listener(self, event_name, listener):
    #     self.listeners[event_name].remove(listener)
    #     if len(self.listeners[event_name]) == 0:
    #         del self.listeners[event_name]

    def emit(self, event_name, event):
        listeners = self.listeners.get(event_name, [])
        print(f'emitting {event_name=} with {str(event)=} to {len(listeners)} listeners')
        for listener in listeners:
            print(f'{event_name=} with {event=} sent to {str(listener)}')
            asyncio.create_task(listener(event))
