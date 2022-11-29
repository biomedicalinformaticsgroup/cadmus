#!/bin/bash

# this script aims to set up edirect for use in cadmus
# first check if edirect is present in the home directory 
echo checking if edirect is already installed
check=$(ls ~/ | grep -c edirect)
if (($check ==0)); then 
echo edirect not installed, begining download
yes | sh -c "$(curl -fsSL ftp://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh)"
echo "export PATH=\$PATH:\$HOME/edirect" >> $HOME/.bash_profile
echo "export NCBI_API_KEY=$1" >> $HOME/.bash_profile
echo install finished
else 
echo edirect already installed
exit;
fi
