
from threading import Thread
from src import messages
from src.schemas import itemschemas
from src.models.itemmodel import ItemModel, ItemHistoricModel
from src.models.stepmodel import StepModel
from src.services.kafkaservice import KafkaService
from src.logging import Logger


__module_name__ = 'src.callbacks'


def send_to_kafka(current_step, item, message):
    Thread(target=KafkaService().producer, args=(current_step.topic, item.uuid, message,)).start()


def verify_if_next_step_exists(msg, item):
    if msg['steps']['next_step'] is not None:
        if 'Exception' in msg['status']:
            current_step, message = next_step_not_exists(msg)

            item.status = 'failed'
            msg['try_count'] = msg['try_count'] - 1

            description = f'{str(msg["status"])}'
            Logger().dispatch('ERROR', __module_name__, 'verify_if_next_step_exists',
                                   f'Item {msg["uuid"]} marked as Error', msg["transaction_id"])

        else:
            current_step, message = next_step_exists(msg, item)

            item.status = 'pending'
            description = messages.ITEM_SENT_TO_QUEUE.format(current_step.topic)
            Logger().dispatch('INFO', __module_name__, 'verify_if_next_step_exists',
                                   f'Item {msg["uuid"]} sent to Queue {current_step.topic}', msg["transaction_id"])

        send_to_kafka(current_step, item, message)

    else:
        item.status = 'finished'
        description = messages.ITEM_FINISHED
        Logger().dispatch('INFO', __module_name__, 'verify_if_next_step_exists',
                               f'Item {msg["uuid"]} finished.', msg["transaction_id"])

    return description


def next_step_exists(msg, item):
    max_step = msg['steps']['max_steps']

    current_step = StepModel.get_by_uuid(uuid=msg['steps']['next_step']['uuid'])
    next_step = StepModel.get_step_by_automation_id(
        automation_id=msg['steps']['next_step']['automation_id'],
        step=msg['steps']['next_step']['step'] + 1) \
        if msg['steps']['next_step']['step'] < max_step else None

    next_step = next_step.to_json() if next_step else None

    item.step = current_step

    schema_item = itemschemas.ItemGetSchema()
    schema_data = schema_item.dump(item)

    json_steps = {
        "steps": {
            "max_steps": max_step,
            "current_step": current_step.to_json(),
            "next_step": next_step
        }
    }

    json_try_count = {
        "try_count": current_step.try_count
    }

    transaction_id = {
        "transaction_id": msg["transaction_id"]
    }

    schema_data.update(json_steps)
    schema_data.update(json_try_count)
    schema_data.update(transaction_id)
    message = schema_data

    return current_step, message


def next_step_not_exists(msg):
    current_step = StepModel.get_by_uuid(uuid=msg['steps']['current_step']['uuid'])
    message = msg
    return current_step, message


def items_processed(app, key, msg):
    with app.app_context():
        item = ItemModel.get_by_uuid(uuid=msg['uuid'])
        if item:
            if msg['try_count'] > 1:

                description = verify_if_next_step_exists(msg, item)

            else:
                if 'Exception' in msg['status']:
                    item.status = 'failed'
                    description = f'{str(msg["status"])}'
                    Logger().dispatch('EXCEPTION', __module_name__, 'items_processed',
                                           f'It was not possible to process the item {msg["uuid"]}',
                                           msg["transaction_id"])

                else:
                    description = verify_if_next_step_exists(msg, item)
                    Logger().dispatch('INFO', __module_name__, 'items_processed',
                                           f'Item {msg["uuid"]} processed successfully', msg["transaction_id"])

            new_item = {
                "data": msg['data'],
                "steps": msg['steps'],
            }

            try:
                ItemHistoricModel.create(item=item, description=f'{description}')
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'items_processed', e.args[0],
                                       msg["transaction_id"])
            try:
                ItemModel.update(item, new_item)
                Logger().dispatch('INFO', __module_name__, 'items_processed',
                                       f'Item {msg["uuid"]} updated successfully', msg["transaction_id"])
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'items_processed', e.args[0],
                                       msg["transaction_id"])


def items_in_process(app, key, msg):
    with app.app_context():
        item = ItemModel.get_by_uuid(uuid=msg['uuid'])
        if item:
            item.status = 'running'
            try:
                ItemModel.update_status(item)
                Logger().dispatch('INFO', __module_name__, 'items_in_progress',
                                       f'Item {msg["uuid"]} is running', msg["transaction_id"])
            except Exception as e:
                Logger().dispatch('CRITICAL', __module_name__, 'items_in_progress', e.args[0],
                                       msg["transaction_id"])

