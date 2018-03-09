import argparse


def main(address, port):
    print(address, port)
    pass


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Serve PyShared')
    parser.add_argument('address', type=str, nargs='?', default='127.0.0.1')
    parser.add_argument('port', type=int, nargs='?', default=0)
    args = parser.parse_args()
    main(**vars(args))
