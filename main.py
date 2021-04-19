from datetime import datetime
import dropbox
from dropbox.exceptions import ApiError, AuthError
import os
import pandas
import pytz
import speedtest
import sys

TOKEN=""
FILENAME = "report.xlsx"

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


def write_results_to_xlsx(results):
    now = current_time()
    timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
    sheet_name = now.strftime("%Y-%m")

    if os.path.isfile(FILENAME):
        data_frame = pandas.read_excel(FILENAME, sheet_name=sheet_name)
        data_frame.loc[len(data_frame)] = [timestamp, bits_per_second_to_megabits_per_second(results.download), bits_per_second_to_megabits_per_second(results.upload)]
    else:
        data = {"Timestamp": [timestamp],
                "Download (Mbps)": [bits_per_second_to_megabits_per_second(results.download)],
                "Upload (Mbps)": [bits_per_second_to_megabits_per_second(results.upload)]}
        data_frame = pandas.DataFrame(data, columns=["Timestamp", "Download (Mbps)", "Upload (Mbps)"])

    with pandas.ExcelWriter(FILENAME) as writer:
        data_frame.to_excel(writer, sheet_name=sheet_name, index=False, float_format="%.2f")


def bits_per_second_to_megabits_per_second(bits_per_second):
    return bits_per_second * 0.000001


def current_time():
    tz = pytz.timezone('Brazil/East')
    return datetime.now(tz)


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

        if file_exists_remotelly(dbx, FILENAME):
            download_file(dbx, FILENAME)

        write_results_to_xlsx(st.results)
        upload_file(dbx, FILENAME)