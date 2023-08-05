import sys
import logging
import socket
sys.path.append('../')

if sys.argv[0].find('client') == -1:

    logger = logging.getLogger('server')
else:

    logger = logging.getLogger('client')


def log(func_to_log):
    """���������, ����������� ����������� ������� �������.��������� ������� ���� debug, �������������������� � �����
    ���������� ��������, ��������� � �������� ���������� �������, � ������, ���������� �������."""

    def log_saver(*args, **kwargs):
        logger.debug(
            f'The function {func_to_log.__name__} with parameters was called {args} , {kwargs}. '
            f'Calling from a module {func_to_log.__module__}')
        ret = func_to_log(*args, **kwargs)
        return ret

    return log_saver


def login_required(func):
    """���������, �����������, ��� ������ ����������� �� �������.���������, ��� ������������ ������ ������ ��������� �
    ������ �������������� ��������.�� ����������� �������� �������-������� �� �����������. ���� ������ �� �����������,
    ���������� ���������� TypeError"""

    def checker(*args, **kwargs):
        from project.server_dist.server.core import MessageProcessor
        from project.client_dist.common.variables import ACTION, PRESENCE
        if isinstance(args[0], MessageProcessor):
            found = False
            for arg in args:
                if isinstance(arg, socket.socket):
                    for client in args[0].names:
                        if args[0].names[client] == arg:
                            found = True

            for arg in args:
                if isinstance(arg, dict):
                    if ACTION in arg and arg[ACTION] == PRESENCE:
                        found = True
            if not found:
                raise TypeError
        return func(*args, **kwargs)

    return checker
