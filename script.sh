#!/usr/bin/env bash
echo 'Downloading the classification datasets...'
python3 download_data.py
echo
echo 'Processing the datasets...'
python3 process_data.py
echo
echo 'K folding the datasets...'
python3 fold_data.py
echo
echo 'Describing the datasets (CSV, LaTeX and PDF)...'
python3 describe_data.py
echo
echo 'DONE!'

