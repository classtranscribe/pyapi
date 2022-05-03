import os

from pkg.agent.tasks.QueueAwaker import QueueAwaker
from pkg.agent.tasks.ExampleTask import ExampleTask
from pkg.agent.tasks.SceneDetection import SceneDetection
from pkg.agent.tasks.PhraseHinter import PhraseHinter

RABBITMQ_CALLBACKS = {
    'QueueAwaker': QueueAwaker().rabbitpy_callback,
    'ExampleTask': ExampleTask().rabbitpy_callback,
    'SceneDetection': SceneDetection().rabbitpy_callback,
    'PhraseHinter': PhraseHinter().rabbitpy_callback
}
