import tarfile
import io
import sys
from datetime import datetime
import pytz
tz = pytz.timezone('Asia/Kolkata')

archive_size = 1000 # lines
log_dir = '/home/ubuntu/migration/slog/'
def archive_gen():
        log_count = 0
        while True:
                data = yield
                log_count += 1
                log_name = log_dir + str(log_count) + '.tar.gz'
                tar = tarfile.open(log_name, 'w:gz')
                logdata = io.BytesIO()
                logstr = '\n'.join(data)
                logdata.write(logstr.encode('utf-8'))
                logdata.seek(0)
                info = tarfile.TarInfo(name='log')
                info.size = len(logstr)
                tar.addfile(tarinfo=info, fileobj=logdata)
                tar.close()
                t = datetime.utcnow().replace(tzinfo=pytz.utc).astimezone(tz).strftime('%H:%M:%S %Y-%m-%d')

                gist_log = log_dir + 'gist'
                with open(gist_log, 'a') as f:
                        last_line = data[0] if data else 'empty'
                        log_entry = '{}: created {}\n{}\n'.format(t, log_name, last_line)
                        f.write(log_entry)
                        f.close()

def log_gen():
        archiver = archive_gen()
        next(archiver)
        cache = []
        while True:
                data = yield
                if not data:
                        archiver.send(cache)
                else:
                        cache.append(data)
                        if len(cache) >= archive_size:
                                archiver.send(cache)
                                cache = []


log = log_gen()
next(log)
while True:
        l = sys.stdin.readline()
        log.send(l)
        if not l:
                break

