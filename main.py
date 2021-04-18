import dropbox
from dropbox.exceptions import ApiError, AuthError
import speedtest
import sys

TOKEN=""

if __name__ == '__main__':
    if len(TOKEN) == 0:
        sys.exit("Error: Empty Dropbox access token.")

    with dropbox.Dropbox(TOKEN) as dbx:
        try:
            dbx.users_get_current_account()
        except AuthError:
            sys.exit("Error: Invalid access token.")

        try:
            metadata, res = dbx.files_download("/Hello_World.txt")        
            with open("Hello_World.txt", "wb") as f:
                f.write(res.content)
            
        except ApiError as e:
            sys.exit("Error: {}".format(e))

#    st = speedtest.Speedtest()
#    st.download(threads=None)
#    st.upload(threads=None)
#    results = st.results

#    print("Download: {} Mbps\nUpload: {} Mbps".format(results.download*(10**-6), results.upload*(10**-6)))

