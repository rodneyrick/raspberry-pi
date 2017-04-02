import os
import csv
import datetime
import twitter
import json
import subprocess
import pytz
import random

def getFilename(abs_path):
    filename = "%s/%s/%s.csv" % (abs_path, 'logs', datetime.datetime.now().strftime('%Y%m'))

    first_line = None
    if not os.path.exists(filename):
        first_line = ['message', 'date', 'download', 'upload', 'ping', 'timestamp_company', 'lat', 'lon', 'host',
                      'latency', 'sponsor', 'name', 'url']

    out_file = open(filename, 'a')
    writer = csv.writer(out_file)

    if first_line is not None:
        writer.writerow(first_line)

    out_file.close()
    return filename

def test_internet(abs_path, datetime_test_connection, connection_speedy_tolerance=15.0):
    isSendMessage = False
    filename = getFilename(abs_path)
    out_file = open(filename, 'a')
    writer = csv.writer(out_file)

    #PI
    out_put = None
    try:
        process = subprocess.Popen(['speedtest-cli', '--json'], stdout=subprocess.PIPE)
        stdout, stderr = process.communicate()
        out_put = json.loads(stdout.decode("utf-8"))

        try:
            out_put['download'] = out_put['download'] / (1000 * 1000)
            out_put['upload'] = out_put['upload'] / (1000 * 1000)

            log_msg = 'OK'
            if out_put['download'] < connection_speedy_tolerance:
                log_msg = 'DownSpeedy'
                isSendMessage = True

            writer.writerow([log_msg,
                             datetime_test_connection,
                             '{:.2f}'.format(out_put['download']),
                             '{:.2f}'.format(out_put['upload']),
                             out_put['ping'],
                             out_put['timestamp'],
                             out_put['server']['lat'],
                             out_put['server']['lon'],
                             out_put['server']['host'],
                             out_put['server']['latency'],
                             out_put['server']['sponsor'],
                             out_put['server']['name'],
                             out_put['server']['url']])
        except Exception as e:
            isSendMessage = False
            writer.writerow(['WithoutConnection', datetime_test_connection, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

        out_file.close()

        return isSendMessage, out_put, filename

    except Exception as e:
        writer.writerow(['Error-speedtest-cli', datetime_test_connection, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])

def which_message(data):
    random.seed(datetime.datetime.now())
    start_messages = ["Hey", "Oi", "Aqui oh!", "Um minuto de sua atenção", "Alô? É da", "Juditeee!!!"]

    message = random.choice(start_messages)

    messages = [

        "{} @NEToficial, conexão ruim! Sponsor: {}, Veloc. Download: {:.2f} Mb".format(
            message,
            data['server']['sponsor'],
            data['download']),

        "{} @NEToficial, seu Host: {} precisa de atenção! Download: {:.2f} Mb".format(message,
            data['server']['host'], data['download']),

        "{} @NEToficial, host: {} precisa de atenção! Latência: {:.2f}s, Download: {:.2f} Mb".format(message,
                                                                                                     data['server']['host'],
                                                                                                     data['server']['latency'],
                                                                                                     data['download']),

        "{} @NEToficial, cidade #SJC bairro #JardimDasIndustrias! Download: {:.2f} Mb".format(message,
                                                                                              data['download'])
    ]

    message = random.choice(messages)
    if len(message) > 140:
        message = "Hey @NEToficial! Download: {:.2f} Mb".format(data['download'])

    return message

def twitter_connection():
    # connect to twitter
    TOKEN = ""
    TOKEN_KEY = ""
    CON_SEC = ""
    CON_SEC_KEY = ""

    my_auth = twitter.OAuth(TOKEN, TOKEN_KEY, CON_SEC, CON_SEC_KEY)
    twit = twitter.Twitter(auth=my_auth)
    return twit

def send2twitter(data, filename, datetime_test_connection):
    twit = twitter_connection()
    try:
        tweet = which_message(data)
        twit.statuses.update(status=tweet)
    except Exception as e:
        out_file = open(filename, 'a')
        writer = csv.writer(out_file)
        writer.writerow(['Error-TwitterConnection', datetime_test_connection, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0])
        out_file.close()


if __name__ == '__main__':
    abs_path = '/home/pi/internet_connection_metrics'
    
    connection_speedy_tolerance = 10.0
    datetime_test_connection = datetime.datetime.now(tz=pytz.timezone("America/Sao_Paulo"))

    isSendMessage, data, filename = test_internet(abs_path, datetime_test_connection, connection_speedy_tolerance)

    if isSendMessage:
        send2twitter(data, filename, datetime_test_connection)

