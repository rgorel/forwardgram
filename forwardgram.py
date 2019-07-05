from telethon import TelegramClient, events, sync
from telethon.tl.types import InputChannel
import yaml
import sys
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logging.getLogger('telethon').setLevel(level=logging.WARNING)
logger = logging.getLogger(__name__)


def start(config):
    client = TelegramClient(config["session_name"],
                            config["api_id"],
                            config["api_hash"])
    client.start()

    input_dialog_entities = []
    output_dialog_entity = None
    for d in client.iter_dialogs():
        if d.name in config["input_dialog_names"]:
            input_dialog_entities.append(d.input_entity)
        if d.name == config["output_dialog_name"]:
            output_dialog_entity = d.input_entity

    if output_dialog_entity is None:
        logger.error(f"Could not find the dialog \"{config['output_dialog_name']}\" in the user's dialogs")
        sys.exit(1)
    logging.info(f"Listening on {len(input_dialog_entities)} channels. Forwarding messages to {config['output_dialog_name']}.")

    @client.on(events.NewMessage(chats=input_dialog_entities))
    async def handler(event):
        await client.forward_messages(output_dialog_entity, event.message)

    client.run_until_disconnected()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} CONFIG_PATH")
        sys.exit(1)
    with open(sys.argv[1], 'rb') as f:
        config = yaml.load(f)
    start(config)
