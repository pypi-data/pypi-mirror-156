from random import shuffle


def pick_proxy(proxies=[]):
    # None means self server
    proxies.append(None)

    temp_proxies = proxies.copy()
    shuffle(temp_proxies)
    while True:
        try:
            yield temp_proxies.pop()
        except IndexError:
            temp_proxies = proxies.copy()
            shuffle(temp_proxies)
            yield temp_proxies.pop()
