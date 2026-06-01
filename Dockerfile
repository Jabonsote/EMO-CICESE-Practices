FROM continuumio/miniconda3:24.11.3-0

WORKDIR /app

COPY environment.yml .
RUN conda env create -f environment.yml

COPY requirements.txt .
RUN /opt/conda/envs/emo-cicese/bin/pip install --no-cache-dir -r requirements.txt

COPY . .

SHELL ["conda", "run", "-n", "emo-cicese", "/bin/bash", "-c"]
CMD ["jupyter", "notebook", "--ip=0.0.0.0", "--port=8888", "--no-browser", "--allow-root"]
