from threading import Thread


def start_thread(target, args):
    Thread(target=target, args=args).start()
