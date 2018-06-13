#!/usr/bin/env bash
echo 'Downloading the classification datasets...'
python download_data.py
echo
echo 'Processing the datasets...'
python process_data.py
echo
echo 'K folding the datasets...'
python fold_data.py
echo
echo 'Describing the datasets (CSV, LaTeX and PDF)...'
python describe_data.py
echo
echo 'DONE!'

