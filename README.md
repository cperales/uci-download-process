# UCI download/process software repository
#### Open source Python repository for downloading, processing, folding and describing supervised machine learning datasets from UCI and others raw repositories


This Github repository is a set of scripts for downloading supervised machine learning
 datasets from [UCI Machine Learning Repository](http://archive.ics.uci.edu/ml/datasets.html), and process them into a common format. Originally, it was a fork of Julia repository [JackDunnNZ/uci-data](https://github.com/JackDunnNZ/uci-data), from which configuration files were extracted. The UCI ML repository is a useful source for machine learning datasets for testing and benchmarking, but the format of datasets is not consistent. This means effort is required in order to make use of new datasets since they need to be read differently.

The main goal of this repository is to process the datasets into a format to be read
from [PyRidge](https://github.com/cperales/PyRidge), where each row of final data is as follows:

    attribute_1 attribute_2 ... attribute_n class

This makes it easy to switch out datasets in ML problems, which is great when automating things.

## Converting to common format

The datasets are not checked in to git in order to minimise the size of the repository and to avoid rehosting the data. As such, the script downloads any missing datasets directly from UCI as it runs.

## Running the code

There are two ways of running the code. Easy/obscure way is to run
first the `install_requirements.sh` script, using `bash`

```bash
bash install_requirements.sh
```

Which install the Python 3 requirements from `requirements.txt`. Packages necessaries for this library:

- numpy
- pandas
- sklearn
- rarfile
- PyLaTeX


After that, the main script

```bash
bash script.sh
```

However, it is recommended to use a virtual environment for Python 3, which can be
done easily following an explanation
[here](https://github.com/cperales/PyRidge#how-to-install-it-within-a-virtual-environment). In this virtual enviroment, previous requirements must be installed. Then, you just have to run the scripts in the main directory

```bash
python download_data.py
python process_data.py
python fold_data.py
python describe_data.py
```

The data will be downloaded, processed, k-folded and described,
in that order. Customizable parameters, such as folders to process and number of folds, are found in `parameter_config.ini`:
    
    [DOWNLOAD]
    config_folders = datafiles/regression,datafiles/classification
    raw_folder = raw_data
    remove_older = True
    
    [PROCESS]
    config_folders = datafiles/regression,datafiles/classification
    processed_folder = processed_data
    remove_older = True
    
    [FOLD]
    processed_folders = processed_data/regression,processed_data/classification
    data_folder = data
    remove_older = True
    n_fold = 10
    
    [DESCRIBE]
    data_folders = data/regression,data/classification
    description_folder = description
    remove_older = True

## Citation policy

> Perales-González, Carlos, (2020). UCI download-process, v1.3, GitHub repository, https://github.com/cperales/uci-download-process

    @misc{UCI-download-process,
      author = {Carlos, Perales-González},
      title = {UCI download/process},
      year = {2020},
      publisher = {GitHub},
      journal = {GitHub repository},
      howpublished = {\url{https://github.com/cperales/uci-download-process}},
      tag = {1.3}
    }
