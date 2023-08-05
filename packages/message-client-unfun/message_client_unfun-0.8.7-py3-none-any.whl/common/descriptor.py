import logging
import sys

if sys.argv[0].find('client') == -1:
    logger = logging.getLogger('server')
else:
    logger = logging.getLogger('client')


class Port:
    """Класс - дескриптор для номера порта.Позволяет использовать только порты с 1023 по 65536.При попытке установить
    неподходящий номер порта генерирует исключение."""

    def __set__(self, instance, port):
        if not 1023 < port < 65536:
            logger.critical(
                f'Попытка запуска сервера с указанием неподходящего порта {port}. Допустимы адреса с 1024 до 65535.')
            exit(1)
        instance.__dict__[self.name] = port

    def __set_name__(self, owner, name):
        self.name = name
