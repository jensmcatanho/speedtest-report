import speedtest

st = speedtest.Speedtest()
st.download(threads=None)
st.upload(threads=None)
results = st.results

print("Download: {} Mbps\nUpload: {} Mbps".format(results.download*(10**-6), results.upload*(10**-6)))