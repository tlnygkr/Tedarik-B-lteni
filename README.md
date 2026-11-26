# Tedarik Zinciri Bülteni

Peli satın alma ekibinin sekmeli günlük bülten panosu.
Yayın adresi: https://peli-tedarik-bulteni.tlnygkr-f22.workers.dev/

- `index.html`: pano (sekmeler: Brifing, Göstergeler ve takvim, Ekonomi · Genel bakış, Haberler)
- `data/bulten.json`: bülten görevleri yazar (hafta içi 08:00 ve 17:00)
- `data/piyasa.json`, `gecmis.json`, `rejim.json`, `ozet.json`: Ekonomi Panosu görevi yazar (07:36 ve 16:36)
- `tools/make_email.py`: bülten e-postasını üretir

`index.html` dosyasını elle değiştirmeyin; görevler yalnızca `data/` klasörünü günceller.
