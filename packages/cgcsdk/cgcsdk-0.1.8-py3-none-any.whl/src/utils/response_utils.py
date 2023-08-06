import string
import sys
import click
import requests

from src.utils.message_utils import prepare_error_message
from src.telemetry.basic import increment_metric


def response_precheck(response: requests.Response, telemetry: string):
    """Checks if server is available and user is authorized

    :param response: dict object from API response.
    :type response: requests.Response
    """
    if response.status_code == 500:
        message = "Internal Server Error. Please try again or contact support at support@comtegra.pl."
        click.echo(prepare_error_message(message))
        increment_metric(telemetry)
        sys.exit()
    if response.status_code == 403:
        message = "Unauthorized. Please check your API key or secret key."
        click.echo(prepare_error_message(message))
        increment_metric(telemetry)
        sys.exit()
