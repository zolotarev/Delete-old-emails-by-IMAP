import imaplib
import datetime
import config


def connect_imap():
    m = imaplib.IMAP4_SSL(config.MAIL_SERVER, config.MAIL_PORT)  # server to connect to
    print("{0} Connecting to mailbox via IMAP...".format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
    m.login(config.USERNAME, config.PASSWORD)
    imaplib._MAXLINE = 100000000000

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
            # m.store("1:{0}".format(no_msgs_del), '+X-GM-LABELS', '\\Trash')  # move to trash
            num = 1
            step = 1000
            while num < int(no_msgs_del):
                try:
                    # m.store(num, '+FLAGS', '\\Deleted')
                    start = num
                    if num + step > int(no_msgs_del):
                        num = int(no_msgs_del)
                        end = int(no_msgs_del)
                    else:
                        end = num + step
                        num += step
                    #m.store("{0}:{1}".format(start, end), '+FLAGS', '\\Deleted')
                    print("{0}:{1}".format(start, end))
                    m.store("{0}:{1}".format(start, end), '+X-GM-LABELS', '\\Trash')  # move to trash
                    print("Deleted messages #{0}..{1} of {2}".format(start, end, no_msgs_del))
                except Exception:
                    print("Deleting message #{0} error:\n{1}".format(num, Exception.with_traceback()))
            print("Deleted {0} messages.".format(no_msgs_del))
        else:
            print("- Nothing to remove.")
    else:
        print("- Nothing to remove.")

    return


def empty_folder(m, folder, do_expunge=True):
    print("- Empty '{0}' & Expunge all mail...".format(folder))
    m.select(folder)  # select all trash
    try:
        m.store("1:*", '+FLAGS', '\\Deleted')  # Flag all Trash as Deleted
    except Exception:
        print('Folder {0} not found'.format(folder))

    if do_expunge:  # See Gmail Settings -> Forwarding and POP/IMAP -> Auto-Expunge
        m.expunge()  # not need if auto-expunge enabled
    else:
        print("Expunge was skipped.")
    return


def disconnect_imap(m):
    print("{0} Done. Closing connection & logging out.".format(datetime.datetime.today().strftime("%Y-%m-%d %H:%M:%S")))
    m.close()
    m.logout()
    print("All Done.")
    return


if __name__ == '__main__':
    config.MAIL_SERVER = input("MAIL_SERVER [" + config.MAIL_SERVER + "]: ") or config.MAIL_SERVER
    config.MAIL_PORT = int(input("MAIL_PORT [" + str(config.MAIL_PORT) + "]: ") or config.MAIL_PORT)
    config.USERNAME = input("USERNAME [" + config.USERNAME + "]: ") or config.USERNAME
    config.PASSWORD = input("PASSWORD [" + config.PASSWORD + "]: ") or config.PASSWORD
    config.MAX_DAYS = int(input("MAX_DAYS [" + str(config.MAX_DAYS) + "]: ") or config.MAX_DAYS)

    m_con = connect_imap()
    # print(m_con.list()[1])
    for i in m_con.list()[1]:
        folder = i.decode().split(' "/" ')
        print(folder[0] + " = " + folder[1])
        move_to_trash_before_date(m_con, folder[1], config.MAX_DAYS)

    try:
      empty_folder(m_con, '[Gmail]/&BBoEPgRABDcEOAQ9BDA-', do_expunge=True)  # can send do_expunge=False, default True
    except Exception:
      print("Can't empy trash. Error:\n{0}".format(Exception.with_traceback()))
    try:
      empty_folder(m_con, '[Gmail]/Trash', do_expunge=True)  # can send do_expunge=False, default True
    except Exception:
      print("Can't empy trash. Error:\n{0}".format(Exception.with_traceback()))
    disconnect_imap(m_con)
