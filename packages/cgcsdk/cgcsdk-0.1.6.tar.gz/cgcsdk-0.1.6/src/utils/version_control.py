import os
import subprocess
import sys
import requests
import click
import pkg_resources


from dotenv import load_dotenv
from src.utils.prepare_headers import get_api_url_and_prepare_headers_version_control
from src.utils.message_utils import prepare_error_message


env_file = pkg_resources.resource_filename("src", ".env")
load_dotenv(dotenv_path=env_file, verbose=True)

MAJOR_VERSION = int(os.getenv("MAJOR_VERSION"))
MINOR_VERSION = int(os.getenv("MINOR_VERSION"))


def check_version():
    """Checks if Client version is up to date with Server version."""
    url, headers = get_api_url_and_prepare_headers_version_control()
    try:
        res = requests.get(
            url,
            headers=headers,
            timeout=10,
        )
    except requests.exceptions.ReadTimeout:
        message = "Connection timed out. Try again or contact us at support@comtegra.pl"
        click.echo(prepare_error_message(message))
        exit()

    if res.status_code != 200:

        message = "Something went wrong. Try again or contact us at support@comtegra.pl"
        click.echo(prepare_error_message(message))
        exit()

    data = res.json()
    if (
        data["server_version"]["major"] != MAJOR_VERSION
        or data["server_version"]["minor"] != MINOR_VERSION
    ):
        message = "You are using outdated version of cgcsdk. Do you want to update to the latest version now?"
        click.echo(message)
        while True:
            anwser = input("(Y/N): ").lower()
            if anwser == "y" or anwser == "yes":
                subprocess.check_call(
                    [sys.executable, "-m", "pip", "install", "--upgrade", "cgcsdk"]
                )
                break
            elif anwser == "n" or anwser == "no":
                exit()


def get_version():
    """Returns version of cgcsdk."""
    return f"{MAJOR_VERSION}.{MINOR_VERSION}"
