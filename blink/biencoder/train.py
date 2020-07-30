import logging
import subprocess
import shlex 
import os
import pathlib
import json

## Runs the command "python train_biencoder.py <CONFIG_FILE>".
## env variables:
# CONFIG_FILE ( defaults to config.json )
# TELEGRAM_PATH (optional, defaults to ./telegram )
# TELEGRAM_CHAT (optional)
# TELEGRAM_TOKEN (optional)
# CUDA_VISIBLE_DEVICES ( defaults to None )


def create_logger(filename, name):
    obj_1 = "{\"time\":\"%(asctime)s\", \"name\": \"%(name)s\", \"level\": \"%(levelname)s\" }"
    obj_2 = "%(message)s"
    time_signature = "%Y-%m-%d %H:%M:%S"
    formatting = obj_1 + '\n' + obj_2
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)
    fh = logging.FileHandler(filename)
    fh.setLevel(logging.DEBUG)
    ch = logging.StreamHandler()
    ch.setLevel(logging.ERROR)
    formatter = logging.Formatter(formatting, time_signature)
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)
    logger.addHandler(fh)
    logger.addHandler(ch)
    return logger

class Telegram_Driver(object):

    def __init__(self, token=None, chat=None, path=None):
        self.token = token
        self.chat = chat
        self.executable_path = path

    def send_message(self, message_or_path, message_type='message'):
        allowed_types = ['message', 'markdown', 'image', 'filename']
        assert(message_type in allowed_types)
        cmd_dict = {
            "message": "{0} -t {1} -c {2}",
            "markdown": "{0} -t {1} -c {2} -M",
            "image": "{0} -t {1} -c {2} -i",
            "filename": "{0} -t {1} -c {2} -f \"{2}\""
        }
        command = cmd_dict[message_type].format(self.executable_path, self.token, self.chat)
        command = command.split(" ")
        command = command + ["\"{0}\"".format(message_or_path)]
        subprocess.Popen(command)


def execute_command(system_command, logger, **kwargs):
    """Execute a system command, passing STDOUT and STDERR to logger.

    Source: https://stackoverflow.com/a/4417735/2063031
    """
    logger.info("system_command: '%s'", system_command)
    popen = subprocess.Popen(
        shlex.split(system_command),
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        universal_newlines=True,
        **kwargs)
    for stdout_line in iter(popen.stdout.readline, ""):
        logger.debug(stdout_line.strip())
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, system_command)

def main():
    config_path = os.environ.get('CONFIG_FILE', 'config.json')
    with open(config_path,'r') as f:
        params = json.load(f)

    pathlib.Path(params['output_path']).mkdir(parents=True, exist_ok=True)

    logfile_path = os.path.join(params['output_path'], 'model.log')

    logger = create_logger(logfile_path, __name__)

    with open(os.path.join(params['output_path'], 'config.json'),'w') as f:
        json.dump(params, f)

    telegram = None
    telegram_chat = os.environ.get('TELEGRAM_CHAT', None)
    telegram_token = os.environ.get('TELEGRAM_TOKEN', None)

    if telegram_chat and telegram_token:
        telegram = Telegram_Driver(token=telegram_token, chat=telegram_chat, path=os.environ.get('TELEGRAM_PATH', './telegram'))

    if telegram:
        telegram.send_message('START: python train_biencoder.py. params: ')
        telegram.send_message(json.dumps(params, indent=4, sort_keys=True))

    cmd = "env CUDA_VISIBLE_DEVICES={0} python train_biencoder.py config.json".format(os.environ.get('CUDA_VISIBLE_DEVICES'))
    execute_command(cmd, logger)
    
    if telegram:
        telegram.send_message('END: python train_biencoder.py.')

if __name__ == '__main__':
    main()