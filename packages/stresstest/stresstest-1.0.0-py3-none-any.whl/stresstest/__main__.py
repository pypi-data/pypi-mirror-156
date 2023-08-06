import argparse

from stresstest.runner import Runner


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--dont-send", help="don't send collected data to server", action="store_true"
    )
    args = parser.parse_args()

    runner = Runner()
    runner.run(dont_send=args.dont_send)


if __name__ == "__main__":
    main()
