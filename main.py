from argparse import ArgumentParser
import os

from aiohttp.web import run_app

from app.web.app import setup_app

MICROSERVISES = [
    "admin-api",
    "vk-poller",
    "vk-worker"
]


def get_service_type() -> str:
    parser = ArgumentParser(description="System for choosing a microservice")
    parser.add_argument('-s', '--servise', choices=MICROSERVISES, default="admin-api")

    namespase = parser.parse_args()

    return namespase.servise


if __name__ == "__main__":
    service = get_service_type()

    run_app(
        port=8080,
        app=setup_app(
            config_path=os.path.join(
                os.path.dirname(os.path.realpath(__file__)), "config.yml"
            ),
            service=service
        ),
    )


