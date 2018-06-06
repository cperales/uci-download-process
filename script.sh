#!/usr/bin/env bash
echo 'Downloading the classification datasets...'
python download_data.py
echo
echo 'Processing the datasets...'
python convert_data.py
echo
echo 'K folding the datasets...'
python k_folding.py
echo
echo 'Descripting the datasets...'
python data_description.py
echo
echo 'Creating a table in LaTeX with the characteristics...'
python latex_table.py
echo
