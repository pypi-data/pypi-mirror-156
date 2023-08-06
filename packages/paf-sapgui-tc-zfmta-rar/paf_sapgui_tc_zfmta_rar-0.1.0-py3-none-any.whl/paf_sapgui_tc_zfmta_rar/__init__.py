import os
import sys
from typing import NoReturn

from paf_sapgui import session, window, field, transaction, button
from paf_sapgui.session import types
from paf_sapgui_eltrans import zfmta_rar
from paf_tools import email, configuration

import pendulum
import contextlib


def main(mode: str) -> NoReturn:
    print("Starting testcase \'ZFMTA_RAR\'")

    preparations()
    login()

    check(mode)

    # gAllgemein.Elemente.Sitzung_beenden()


def check(mode: str) -> NoReturn:
    transaction.open("zfmta_rar")
    zfmta_rar.SelectionScreen().belegart().value("o")

    if mode.lower() in {'monat', 'month', 'm'}:
        zfmta_rar.SelectionScreen().datum_von().value(
            pendulum.now().subtract(months=1).start_of('month').format('dd.mm.yyyy'))
        zfmta_rar.SelectionScreen().datum_bis().value(
            pendulum.now().subtract(months=1).end_of('month').format('dd.mm.yyyy'))
        zfmta_rar.SelectionScreen().status_des_rai().value("60")
    else:
        zfmta_rar.SelectionScreen().status_des_rai().value("20")
    zfmta_rar.SelectionScreen().zaehlen().click()

    text_from_window = window.get_contents(1)
    text_from_window = text_from_window[text_from_window.index(':') + 1:]
    error_count = int(text_from_window)

    config = configuration.get('apps', 'ZfmtaRar')
    signature = configuration.get('signatures', 'ses_allgemein')
    mail_sending_credentials = configuration.credentials('sendMails')

    email_message = email.Email()
    email_message.reply_address(config["Email"]["Receivers"]["ReplyTo"])
    email_message.sender(config["Email"]["Sender"])
    email_message.login_credentials(username=mail_sending_credentials.user, password=mail_sending_credentials.password)

    if error_count != 0:
        print(f'Check with mode \'{mode}\' results in an error. Sending a message.')

        email_text = f'{config["Email"]["Error"]["Address"]}{config["Email"]["Error"]["Text"]}{signature}'

        email_message.content(subject=config['Email']['Error']['Subject'], text=email_text.replace('PRUEFUNG', mode))
        for recipient in config["Email"]["Receivers"]["Error"]:
            email_message.receiver(recipient)

        # Prot.Info("E-Mail mit Fehlerinformationen versendet");
    else:
        print(f'No errors found using check for mode \'{mode}\'. Sending protocol.')
        email_text = f'{config["Email"]["Protocol"]["Address"]}{config["Email"]["Protocol"]["Text"]}{signature}'

        email_message.content(subject=config['Email']['Protocol']['Subject'], text=email_text.replace('PRUEFUNG', mode))
        for recipient in config["Email"]["Receivers"]["Protocol"]:
            email_message.receiver(recipient)

    email_message.send()


def preparations() -> NoReturn:
    print("Preparing the testcase")


def login() -> NoReturn:
    login_credentials = configuration.credentials(credentials_name='SapWspCkoeste1')
    session.session_data(user=login_credentials.user, password=login_credentials.password,
                         system=types.SapSystems.WSP, client='010')

    session.create()


if __name__ == "__main__":
    if len(sys.argv) <= 1:
        print("You have to provide at least one argument (Monat, Month, m, Woche, Week, w)")
        exit(1)
    main(sys.argv[1])
