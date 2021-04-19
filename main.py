from datetime import datetime
import dropbox
from dropbox.exceptions import ApiError, AuthError
import speedtest
import sys

TOKEN=""
FILENAME = "report.txt"

def file_exists_remotelly(dbx, filename) -> bool:
    path = "/{}".format(filename)
    try:
        dbx.files_get_metadata(path)
        return True
    except:
        return False


def download_file(dbx, filename):
    try:
        metadata, res = dbx.files_download("/{}".format(filename))        
        with open("{}".format(filename), "wb") as f:
            f.write(res.content)
        
    except ApiError as e:
        sys.exit("Error: {}".format(e))


def upload_file(dbx, filename):
    path = "/{}".format(filename)
    try:
        with open("{}".format(filename), "rb") as f:
            res = dbx.files_upload(f.read(), path, mode=dropbox.files.WriteMode.overwrite)

    except ApiError as e:
        sys.exit("Error: {}".format(e))


if __name__ == '__main__':
    if len(TOKEN) == 0:
        sys.exit("Error: Empty Dropbox access token.")

    with dropbox.Dropbox(TOKEN) as dbx:
        try:
            dbx.users_get_current_account()
        except AuthError:
            sys.exit("Error: Invalid access token.")

        st = speedtest.Speedtest()
        st.download(threads=None)
        st.upload(threads=None)
        results = st.results
        result_to_sync = "{}\nDownload: {} Mbps\nUpload: {} Mbps\n\n".format(results.timestamp, results.download*(10**-6), results.upload*(10**-6))

        if file_exists_remotelly(dbx, FILENAME):
            download_file(dbx, FILENAME)
            
            with open("{}".format(FILENAME), "a") as f:
                f.write(result_to_sync)

        else:
            with open("{}".format(FILENAME), "w") as f:
                f.write(result_to_sync)

        upload_file(dbx, FILENAME)