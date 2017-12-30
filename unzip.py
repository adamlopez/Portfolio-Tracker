
import requests as req, zipfile, io
r = req.get(r'https://www.ecb.europa.eu/stats/eurofxref/eurofxref-hist.zip?82a3f6f1218fcfac4242624c0b826f50')
z = zipfile.ZipFile(io.BytesIO(r.content))
z.extractall()

print(z)
