# setup mambaforge
sudo yum install -y zsh tree wget screen git
wget https://github.com/conda-forge/miniforge/releases/latest/download/Mambaforge-Linux-x86_64.sh
sh Mambaforge-Linux-x86_64.sh -b -p $HOME/mambaforge
rm -f Mambaforge-Linux-x86_64.sh
./mambaforge/bin/mamba init
exec /bin/bash

# install packages
mkdir -p src/jupyter
cd src/jupyter
gsutil cp gs://ecker-hanqing-src/jupyter/env.yaml ./
mamba env create -f env.yaml

# startup script

# copy analysis files and mount filestore
sudo mount 10.132.160.226:/eckerhome /mnt/home
cd BICCN
# start jupyter
screen -R jupyter
mamba activate wmb
jupyter-lab --ip=0.0.0.0 --port=8080 --no-browser --NotebookApp.token='USE_YOUR_PW_HERE'
jupyter-notebook --ip=0.0.0.0 --port=8080 --no-browser --NotebookApp.token='USE_YOUR_PW_HERE'

