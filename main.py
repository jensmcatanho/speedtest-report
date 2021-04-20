import argparse
from datetime import datetime
import dropbox
from dropbox.exceptions import ApiError, AuthError
import os
import pandas
from pathlib import Path
import pytz
import speedtest
import sys


def file_exists_remotelly(dbx: dropbox.Dropbox, remote_report_file_path: str) -> bool:
    try:
        dbx.files_get_metadata(remote_report_file_path)
        return True

    except:
        return False


def download_file(dbx: dropbox.Dropbox, local_report_file_path: Path, remote_report_file_path: str):
    try:
        metadata, response = dbx.files_download(remote_report_file_path)
        with local_report_file_path.open(mode='wb') as report_file:
            report_file.write(response.content)
        
    except ApiError as e:
        sys.exit(f"Error: {e}")


def upload_file(dbx: dropbox.Dropbox, local_report_file_path: Path, remote_report_file_path: str):
    try:
        with local_report_file_path.open(mode='rb') as report_file:
            upload_result = dbx.files_upload(report_file.read(), remote_report_file_path, mode=dropbox.files.WriteMode.overwrite)

    except ApiError as e:
        sys.exit(f"Error: {e}")


def write_results_to_xlsx(results: speedtest.SpeedtestResults, local_report_file_path: Path):
    now = current_time()
    timestamp = now.strftime("%d-%m-%Y %H:%M:%S")
    sheet_name = now.strftime("%Y-%m")

    if local_report_file_path.exists():
        data_frame = pandas.read_excel(local_report_file_path, sheet_name=sheet_name)
        data_frame.loc[len(data_frame)] = [timestamp, bits_per_second_to_megabits_per_second(results.download), bits_per_second_to_megabits_per_second(results.upload)]
    else:
        data = {"Timestamp": [timestamp],
                "Download (Mbps)": [bits_per_second_to_megabits_per_second(results.download)],
                "Upload (Mbps)": [bits_per_second_to_megabits_per_second(results.upload)]}
        data_frame = pandas.DataFrame(data, columns=["Timestamp", "Download (Mbps)", "Upload (Mbps)"])

    with pandas.ExcelWriter(local_report_file_path) as writer:
        data_frame.to_excel(writer, sheet_name=sheet_name, index=False, float_format="%.2f")


def bits_per_second_to_megabits_per_second(bits_per_second: float) -> float:
    return bits_per_second * 0.000001


def current_time() -> datetime:
    tz = pytz.timezone('Brazil/East')
    return datetime.now(tz)


def parse_arguments() -> (Path, str, str, float, bool):
    parser = argparse.ArgumentParser()
    parser.add_argument('--local-path', type=str, required=True)
    parser.add_argument('--remote-path', type=str, required=True)
    parser.add_argument('--access-token', type=str, required=True)
    parser.add_argument('--timeout', default=10, type=float, required=False)
    parser.add_argument('--secure', default=False, type=bool, required=False)
    args = parser.parse_args()

    return Path(args.local_path), args.remote_path, args.access_token, args.timeout, args.secure


def speed_test(timeout, secure):
    st = speedtest.Speedtest(timeout=timeout, secure=secure)
    st.download(threads=None)
    st.upload(threads=None)

    return st.results

if __name__ == '__main__':
    local_path, remote_path, access_token, timeout, secure = parse_arguments()

    with dropbox.Dropbox(access_token) as dbx:
        try:
            dbx.users_get_current_account()
        except AuthError:
            sys.exit("Error: Invalid access token.")

        if file_exists_remotelly(dbx, remote_path):
            download_file(dbx, local_path, remote_path)

        results = speed_test(timeout, secure)

        write_results_to_xlsx(results, local_path)
        upload_file(dbx, local_path, remote_path)