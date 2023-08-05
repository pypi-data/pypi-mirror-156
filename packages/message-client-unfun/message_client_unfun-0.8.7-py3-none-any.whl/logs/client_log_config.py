import sys
import logging
sys.path.append('../')
client_format = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(client_format)
handler.setLevel(logging.ERROR)
file_client = logging.FileHandler("client.log", encoding='utf-8')
file_client.setFormatter(client_format)


logger = logging.getLogger('client')
logger.addHandler(handler)
logger.addHandler(file_client)
logger.setLevel(logging.DEBUG)


if __name__ == '__main__':
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')

