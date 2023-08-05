import sys
import logging.handlers

sys.path.append('../')
server_format = logging.Formatter('%(asctime)s %(levelname)s %(filename)s %(message)s')

handler = logging.StreamHandler(sys.stderr)
handler.setFormatter(server_format)
handler.setLevel(logging.ERROR)
file_server = logging.handlers.TimedRotatingFileHandler("server.log", encoding='utf-8', interval=1, when='D')
file_server.setFormatter(server_format)

logger = logging.getLogger('server')
logger.addHandler(handler)
logger.addHandler(file_server)
logger.setLevel(logging.DEBUG)

if __name__ == '__main__':
    logger.critical('Критическая ошибка')
    logger.error('Ошибка')
    logger.debug('Отладочная информация')
    logger.info('Информационное сообщение')
