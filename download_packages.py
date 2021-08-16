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

    

# update file paths from URL to local
import urllib.request, os

text_path = r'E:\air_gapped_mgrs_arcgis\arcgis-mgrs-air-gapped.txt'
local_path = r"E:/"
text_file = text_path.split('\\')[-1]

with open(text_path, 'r') as txt_file:
    contents = txt_file.readlines()

with open(f"{local_path}{text_file}", 'a') as new_text_file:
    for i in contents:
        if 'https://' in i:
            url = i.strip('\n')
            file_name = os.path.join(local_path,url.split('/')[-1])
            print(file_name)
            new_text_file.write(f"{file_name}\n")
        else:
            print(i)
            new_text_file.write(i)
