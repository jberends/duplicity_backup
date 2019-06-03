import click


def echo_success(text, nl=True):
    """
    Write to the console as a success (Cyan bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, fg='cyan', bold=True, nl=nl)


def echo_failure(text, nl=True):
    """
    Write to the console as a failure (Red bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, fg='red', bold=True, nl=nl)


def echo_warning(text, nl=True):
    """
    Write to the console as a warning (Yellow bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, fg='yellow', bold=True, nl=nl)


def echo_waiting(text, nl=True):
    """
    Write to the console as a waiting (Magenta bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, fg='magenta', bold=True, nl=nl)


def echo_info(text, nl=True):
    """
    Write to the console as a informational (bold).

    :param text: string to write
    :param nl: add newline
    """
    click.secho(text, bold=True, nl=nl)
