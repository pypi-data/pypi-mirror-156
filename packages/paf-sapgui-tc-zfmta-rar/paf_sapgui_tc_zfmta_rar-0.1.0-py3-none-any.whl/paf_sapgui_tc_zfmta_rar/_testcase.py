import os
import sys
from typing import NoReturn

from paf_sapgui_component_session import session, window
from paf_sapgui_component_session import options
import paf_sapgui_eltrans_zfmta_rar
from paf_sapgui_eltrans_zfmta_rar import selection_screen
from paf_tool_email import Email
import paf_tool_configuration as config_package

import pendulum


def execute(mode: str) -> NoReturn:
    print("Starting testcase \'ZFMTA_RAR\'")

    preparations()
    login()

    check(mode)

    # gAllgemein.Elemente.Sitzung_beenden()


def check(mode: str) -> NoReturn:
    paf_sapgui_eltrans_zfmta_rar.open()
    selection_screen.belegart('o')

    if mode.lower() in {'monat', 'month', 'm'}:
        selection_screen.datum_von(pendulum.now().subtract(months=1).start_of('month').format('dd.mm.yyyy'))
        selection_screen.datum_bis(pendulum.now().subtract(months=1).end_of('month').format('dd.mm.yyyy'))
        selection_screen.status_des_rai('60')
    else:
        selection_screen.status_des_rai('20')

    selection_screen.zaehlen(click=True)

    text_from_window = window.get_contents(1)
    text_from_window = text_from_window[text_from_window.index(':') + 1:]
    error_count = int(text_from_window)

    config = config_package.get('apps', 'ZfmtaRar')
    signature = config_package.get('signatures', 'ses_allgemein')
    mail_sending_credentials = config_package.credentials('sendMails')

    email = Email()
    email.reply_address(config["Email"]["Receivers"]["ReplyTo"])
    email.sender(config["Email"]["Sender"])
    email.login_credentials(username=mail_sending_credentials.user, password=mail_sending_credentials.password)

    if error_count != 0:
        print(f'Check with mode \'{mode}\' results in an error. Sending a message.')

        email_text = f'{config["Email"]["Error"]["Address"]}{config["Email"]["Error"]["Text"]}{signature}'

        email.content(subject=config['Email']['Error']['Subject'], text=email_text.replace('PRUEFUNG', mode))
        for recipient in config["Email"]["Receivers"]["Error"]:
            email.receiver(recipient)

        # Prot.Info("E-Mail mit Fehlerinformationen versendet");
    else:
        print(f'No errors found using check for mode \'{mode}\'. Sending protocol.')
        email_text = f'{config["Email"]["Protocol"]["Address"]}{config["Email"]["Protocol"]["Text"]}{signature}'

        email.content(subject=config['Email']['Protocol']['Subject'], text=email_text.replace('PRUEFUNG', mode))
        for recipient in config["Email"]["Receivers"]["Protocol"]:
            email.receiver(recipient)

    email.send()


def preparations() -> NoReturn:
    print("Preparing the testcase")


def login() -> NoReturn:
    login_credentials = config_package.credentials(credentials_name='SapWspCkoeste1')
    session.set_session_data(user_name=login_credentials.user, password=login_credentials.password,
                             system_name=options.sap_systems.WSP, client='010')

    session.create()


if __name__ == "__main__":
    try:
        if len(sys.argv) <= 1:
            raise ValueError('You have to provide at least one argument (Monat, Month, m, Woche, Week, w)')
        execute(sys.argv[1])
    except Exception as ex:
        # send prot mail
        pass
