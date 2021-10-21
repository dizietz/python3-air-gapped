# Use this to download miniconda 4.9.2
https://repo.anaconda.com/miniconda/

# Use this for reference
https://david-e-warren.me/blog/anaconda-python-on-air-gapped-computers/

# Change the specs.text to point to local install directories

$ conda create --name myenv python=3.6.7
$ conda activate myenv
$ conda install -c esri arcgis
$ conda install -c conda-forge mgrs
$ conda install -c conda-forge shapely

$ conda list --explicit > /path/for/spec_file.txt

$ cat /path/for/spec_file.txt | grep "^http" | xargs -I xxx wget -P /path/for/pkgs xxx 

$ cat spec_file.txt

# This file may be used to create an environment using:
# $ conda create --name <env> --file <this file>
# platform: linux-64
@EXPLICIT
pkgs/pillow-6.2.1-py36hd70f55b_1.tar.bz2
pkgs/python-3.6.7-h357f687_1006.tar.bz2
pkgs/pip-19.3.1-py36_0.tar.bz2

$ conda create --name myenv --file /path/to/spec_file.txt

$ conda activate myenv
