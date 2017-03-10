import logging
import json
import socket
import time

from messaging.message import Message
from messaging.queue.dqs import DQS

log = logging.getLogger("nap")


def enqueue(dirq, destination, event):
    mq_header = {'measurement_agent': socket.gethostname(),
                 'destination': destination
                 }
    if 'timestamp' not in event.keys():
        event['timestamp'] = time.time()
    mq_body = json.dumps(event)

    msg = Message(body=mq_body, header=mq_header)
    msg.is_text = True
    mq = DQS(path=dirq)
    mq.add_message(msg)
