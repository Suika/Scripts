from guerrillamail import GuerrillaMailSession
import subprocess
import string
import os
import sys
import random
import names
from time import sleep
from lxml import html
FNULL = open(os.devnull, 'w')

def genMegaAccount(numAccounts=1):
    for i in range(numAccounts):
        session = GuerrillaMailSession()
        password = ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(10))
        pre_email_count = len(session.get_email_list())
        verify_link = subprocess.check_output(
            ["megatools", "reg", "-n", names.get_full_name(), "-e", session.email_address, "-p", password, "--register",
             "--scripted"]).decode("utf-8").replace("@LINK@\n", "{}")
        while pre_email_count == len(session.get_email_list()): sleep(1)
        verify_command = (verify_link.format(
            html.fromstring(session.get_email(session.get_email_list()[0].guid).body).xpath(
                "//a[contains(@href, 'confirm')]/@href")[0])).split()
        if "successfull" in subprocess.check_output(verify_command).decode("utf-8"):
            print(":".join([session.email_address, password]))

if __name__ == '__main__':
    try:
        genMegaAccount(int(sys.argv[1]))
    except:
        genMegaAccount()
