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