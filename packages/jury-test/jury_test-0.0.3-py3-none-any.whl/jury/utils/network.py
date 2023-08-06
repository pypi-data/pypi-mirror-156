def is_port_in_use(port: int) -> bool:
    import socket
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0


from_port = 30000


def get_free_port():
    global from_port
    from_port += 1
    while is_port_in_use(from_port):
        from_port += 1
    return from_port


if __name__ == '__main__':
    print(get_free_port())
    for i in range(100):
        print(get_free_port())
