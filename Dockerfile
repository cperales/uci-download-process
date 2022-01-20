FROM python:3.9

RUN pip install -U pip
RUN pip install coveralls PyYAML coveralls
RUN pip install joblib==1.1.0 \
    numpy==1.22.1 \
    ordered-set==4.0.2 \
    pandas==1.3.5 \
    PyLaTeX==1.4.1 \
    python-dateutil==2.8.2 \
    pytz==2021.3 \
    rarfile==4.0 \
    scikit-learn==1.0.2 \
    scipy==1.7.3 \
    six==1.16.0 \
    sklearn==0.0 \
    threadpoolctl==3.0.0

RUN apt update -y && apt install -y texlive-latex-extra lmodern
COPY . . 
RUN coverage run describe_data.py
