ARG CUDA=10.1
ARG UBUNTU_VERSION=18.04

FROM nvidia/cuda${ARCH:+-$ARCH}:${CUDA}-base-ubuntu${UBUNTU_VERSION} as base

# Needed for string substitution
SHELL ["/bin/bash", "-c"]

## ARCH and CUDA are specified again because the FROM directive resets ARGs
## (but their default value is retained if set previously)
ARG ARCH
ARG CUDA
ARG UBUNTU_VERSION
ARG CUDNN=8.8.1.3-1
ARG CUDNN_MAJOR_VERSION=8
ARG LIB_DIR_PREFIX=x86_64
ARG LIBNVINFER=8.6.0.12-1
ARG LIBNVINFER_MAJOR_VERSION=8

# There appears to be a regression in libcublas10=10.2.2.89-1 which
# prevents cublas from initializing in TF. See
# https://github.com/tensorflow/tensorflow/issues/9489#issuecomment-562394257
ARG BUILD_DEPS="\
  build-essential \
  cuda-command-line-tools-${CUDA} \
  libcublas10=10.2.1.243-1 \
  cuda-nvrtc-${CUDA} \
  cuda-cufft-${CUDA} \
  cuda-curand-${CUDA} \
  cuda-cusolver-${CUDA} \
  cuda-cusparse-${CUDA} \
  curl \
  git \
  wget \
  libcudnn8=${CUDNN}+cuda12.0 \
  libfreetype6-dev \
  libhdf5-serial-dev \
  libzmq3-dev \
  python3 \
  python3-pip \
  pkg-config \
  software-properties-common \
  unzip"

ARG RUNTIME_DEPS="\
  tzdata \
  cuda-command-line-tools-${CUDA} \
  libcublas10=10.2.1.243-1 \
  cuda-nvrtc-${CUDA} \
  cuda-cufft-${CUDA} \
  cuda-curand-${CUDA} \
  cuda-cusolver-${CUDA} \
  cuda-cusparse-${CUDA} \
  libcudnn8=${CUDNN}+cuda12.0 \
  libfreetype6 \
  libhdf5-100 \
  libzmq5 \
  software-properties-common \
  ttf-mscorefonts-installer \
  curl \
  wget \
  unzip \
  netcat \
  gosu \
  bash"

# For CUDA profiling, TensorFlow requires CUPTI.
ENV LD_LIBRARY_PATH=/usr/local/cuda-10.1/extras/CUPTI/lib64:/usr/local/cuda-10.1/lib64:$LD_LIBRARY_PATH \
  RUNTIME_DEPS=${RUNTIME_DEPS} \
  BUILD_DEPS=${BUILD_DEPS} \
  PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  PYTHONIOENCODING=UTF-8 \
  PIP_DISABLE_PIP_VERSION_CHECK=1 \
  PATH="/install/bin:${PATH}" \
  LANG=C.UTF-8 \
  LC_ALL=C.UTF-8
# See http://bugs.python.org/issue19846

WORKDIR /home/root/app

FROM base as build

COPY ai_platform/aiplatform_requirements.txt .

# Pick up some TF dependencies
# Install TensorRT if not building for PowerPC
# Link the libcuda stub to the location where tensorflow is searching for it and reconfigure
# dynamic linker run-time bindings
RUN mkdir /install && \
  apt-get update && apt-get install -y --no-install-recommends $( echo "${BUILD_DEPS}" | sed "s/-${CUDA} /-${CUDA/./-} /g" ) && \
  if [[ "${ARCH}" != "ppc64le" ]] ; then apt-get install -y --no-install-recommends libnvinfer${LIBNVINFER_MAJOR_VERSION}=${LIBNVINFER}+cuda12.0 libnvinfer-plugin${LIBNVINFER_MAJOR_VERSION}=${LIBNVINFER}+cuda12.0 ; fi && \
  python3 -m pip --no-cache-dir install --upgrade pip setuptools && \
  pip install --no-cache-dir --prefix=/install -r aiplatform_requirements.txt && \
  ln -s /usr/local/cuda-${CUDA}/lib64/stubs/libcuda.so /usr/local/cuda-10.1/lib64/stubs/libcuda.so.1 && \
  echo "/usr/local/cuda-${CUDA}/lib64/stubs" > /etc/ld.so.conf.d/z-cuda-stubs.conf && \
  ldconfig && \
  apt-get autoremove -y && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

FROM base

ARG DEBIAN_FRONTEND=noninteractive

RUN apt-get update \
  && SUDO_FORCE_REMOVE=yes apt-get remove --purge -y $( echo "${BUILD_DEPS}" | sed "s/-${CUDA} /-${CUDA/./-} /g" ) \
  && apt-get autoremove -y \
  && echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections \
  && apt-get install -y --no-install-recommends $( echo "${RUNTIME_DEPS}" | sed "s/-${CUDA} /-${CUDA/./-} /g" ) \
  && ln -s /usr/local/cuda-${CUDA}/lib64/stubs/libcuda.so /usr/local/cuda-${CUDA}/lib64/stubs/libcuda.so.1 \
  && echo "/usr/local/cuda-${CUDA}/lib64/stubs" > /etc/ld.so.conf.d/z-cuda-stubs.conf \
  && ldconfig \
  && ln -s $(which python3) /usr/local/bin/python \
  && rm -rf /usr/share/man \
  && apt-get clean \
  && rm -rf /var/lib/apt/lists/*
# Some TF tools expect a "python" binary

#COPY --from=builder /wheels /wheels
COPY --from=build /install /usr/local

COPY ai_platform/aiplatform_app.py ai_platform/settings.py .
COPY bothub/shared bothub/shared
COPY bothub/__init__.py bothub

ARG DOWNLOAD_MODELS
#Install torch with cuda 10.1
RUN if [ "${DOWNLOAD_MODELS}" = "pt_br-BERT" ]; then \
        pip install --no-cache-dir torch==1.6.0+cu101 torchvision==0.7.0+cu101 -f https://download.pytorch.org/whl/torch_stable.html; \
    fi ; \
    if [ ${DOWNLOAD_MODELS} ]; then \
        python3.6 bothub/shared/utils/scripts/download_models.py ${DOWNLOAD_MODELS}; \
    fi

ENTRYPOINT ["python3.6", "aiplatform_app.py"]

