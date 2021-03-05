sudo pip3 uninstall -y iMesh-Dashboard
sudo rm -r dist/
python3 setup.py sdist bdist_wheel --universal
sudo pip3 install ./dist/iMesh-Dashboard-*.tar.gz