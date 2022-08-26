import imaplib
import datetime

MAIL_SERVER = 'imap.gmail.com'
MAIL_PORT = 993
USERNAME = 'zolotarev@its.bz'
PASSWORD = 'Heruvima80'
MAX_DAYS = 365  # Deletes messages older than days


def connect_imap():
    m = imaplib.IMAP4_SSL(MAIL_SERVER, MAIL_PORT)  # server to connect to
    print("{0} Connecting to mailbox via IMAP...".format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
    m.login(USERNAME, PASSWORD)

    return m


def move_to_trash_before_date(m, folder, days_before):
    try:
        no_of_msgs = int(m.select(folder)[1][0])
    except Exception:
        print("Folder not found {0}", folder)
        return Exception
    print("- Found a total of {1} messages in '{0}'.".format(folder, no_of_msgs))

    before_date = (datetime.date.today() - datetime.timedelta(days_before)).strftime(
        "%d-%b-%Y")  # date string, 04-Jan-2013
    typ, data = m.search(None, '(BEFORE {0})'.format(before_date))  # search pointer for msgs before before_date

    if data != ['']:  # if not empty list means messages exist
        if len(data[0].decode().split()) > 1:
            no_msgs_del = data[0].decode().split()[-1]  # last msg id in the list
            print("- Marked {0} messages for removal with dates before {1} in '{2}'.".format(no_msgs_del, before_date,
                                                                                             folder))
            #m.store("1:{0}".format(no_msgs_del), '+X-GM-LABELS', '\\Trash')  # move to trash
            for num in data[0].decode().split():
                try:
                    m.store(num, '+FLAGS', '\\Deleted')
                    print("Deleted message #{0} of {1}".format(num, no_msgs_del))
                except Exception:
                    print("Deleting message #{0} error:\n{1}".format(num, Exception))
            print("Deleted {0} messages.".format(no_msgs_del))
        else:
            print("- Nothing to remove.")
    else:
        print("- Nothing to remove.")

    return


def empty_folder(m, folder, do_expunge=True):
    print("- Empty '{0}' & Expunge all mail...".format(folder))
    m.select(folder)  # select all trash
    m.store("1:*", '+FLAGS', '\\Deleted')  # Flag all Trash as Deleted
    if do_expunge:  # See Gmail Settings -> Forwarding and POP/IMAP -> Auto-Expunge
        m.expunge()  # not need if auto-expunge enabled
    else:
        print("Expunge was skipped.")
    return


def disconnect_imap(m):
    print("{0} Done. Closing connection & logging out.".format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
    m.close()
    m.logout()
    # print "All Done."
    return


if __name__ == '__main__':
    m_con = connect_imap()
    for i in m_con.list()[1]:
        l = i.decode().split(' "/" ')
        print(l[0] + " = " + l[1])
        move_to_trash_before_date(m_con, l[1], MAX_DAYS)

    empty_folder(m_con, '[Gmail]/Trash', do_expunge=True)  # can send do_expunge=False, default True

    disconnect_imap(m_con)