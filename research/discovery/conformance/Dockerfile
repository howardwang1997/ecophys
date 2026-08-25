ARG BASE_IMAGE
FROM ${BASE_IMAGE}

COPY oci_probe.py /usr/local/bin/ecomd-dx-oci-probe
ENTRYPOINT ["python", "/usr/local/bin/ecomd-dx-oci-probe"]
