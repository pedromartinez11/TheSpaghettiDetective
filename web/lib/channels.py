from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer

from . import redis
from app.models import *

def commands_group_name(printer_id):
    return 'p_cmd_{}'.format(printer_id)

def status_group_name(printer_id):
    return 'p_sts_{}'.format(printer_id)

def janus_web_group_name(printer_id):
    return 'janus_web_{}'.format(printer_id)

def send_commands_to_printer(printer_id):
    commands = PrinterCommand.objects.filter(printer_id=printer_id, status=PrinterCommand.PENDING)
    if not commands:
        return

    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        commands_group_name(printer_id),
        {
            'type': 'printer.commands',    # mapped to -> printer_commands in consumer
            'commands': [ json.loads(c.command) for c in commands ],
        }
    )

    commands.update(status=PrinterCommand.SENT)

def send_janus_msg_to_printer(printer_id, msg):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        commands_group_name(printer_id),
        {
            'type': 'printer.commands',    # mapped to -> printer_commands in consumer
            'janus': msg
        }
    )

def send_status_to_web(printer_id):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        status_group_name(printer_id),
        {
            'type': 'printer.status',         # mapped to -> printer_status in consumer
        }
    )

def send_janus_to_web(printer_id, msg):
    layer = get_channel_layer()
    async_to_sync(layer.group_send)(
        janus_web_group_name(printer_id),
        {
            'type': 'janus.message',         # mapped to -> janus_message in consumer
            'msg': msg,
        }
    )
