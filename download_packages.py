# standard library

import urllib.request

with open(r'E:\arcgis-mgrs-air-gapped.txt', 'r') as txt_file:
    contents = txt_file.readlines()  

for i in contents:
    if 'https://' in i:
        url = i.strip('\n')
        file_name = f"E:\\{url.split('/')[-1]}"
        print(url, file_name)
        urllib.request.urlretrieve(url, file_name)



# requires requests
import requests, os

specs_path = r'E:\miniconda_specs.txt'
download_path = r'E:\pkgs'

with open(specs_path,'r') as spec_text:
    specs = spec_text.readlines()
    urls = [i.strip() for i in specs if "https://" in i]

for url in urls:
    r = requests.get(url, allow_redirects=True)
    file_name = url.split('/')[-1]
    file_dest = os.path.join(download_path,file_name)
    print(file_dest)
    open(file_dest, 'wb').write(r.content)
