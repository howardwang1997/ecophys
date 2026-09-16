ARG BASE_IMAGE=sha256:2e32f7d302adc1c37428355c1e646897c0c53f4fd60b6a551245fb90ee129f91
FROM ${BASE_IMAGE}
ENV OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=1 MKL_NUM_THREADS=1 \
    NUMEXPR_NUM_THREADS=1 PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 PYTHONPATH=/opt
COPY wheels /wheels
COPY requirements.lock /requirements.lock
RUN python -m pip install --no-index --no-cache-dir --require-hashes \
    --find-links=/wheels -r /requirements.lock && rm -rf /wheels
COPY model.py runner.py /opt/response_dx/
COPY oci_probe.py /opt/response_dx/oci_probe.py
ENTRYPOINT ["python", "-m", "response_dx.runner"]
