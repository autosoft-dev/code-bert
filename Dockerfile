FROM python:3.6-slim-buster as builder

RUN apt-get update && apt-get install -y \
  xz-utils \
  build-essential \
  curl \
  && rm -rf /var/lib/apt/lists/* \
  && curl -SL http://releases.llvm.org/9.0.0/clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-18.04.tar.xz \
  | tar -xJC . && \
  mv clang+llvm-9.0.0-x86_64-linux-gnu-ubuntu-18.04 clang_9.0.0 && \
  echo 'export PATH=/clang_9.0.0/bin:$PATH' >> ~/.bashrc && \
  echo 'export LD_LIBRARY_PATH=/clang_9.0.0/lib:$LD_LIBRARY_PATH' >> ~/.bashrc

RUN apt-get update && \
apt-get install -y \
python3 \
python3-pip \
build-essential \
libssl-dev \
libffi-dev \
python3-dev \
git

WORKDIR /usr/src/app

RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip wheel --no-cache-dir --no-deps --wheel-dir /usr/src/app/wheels -r requirements.txt

FROM python:3.6-slim-buster

COPY --from=builder /usr/src/app/wheels /wheels
COPY --from=builder /usr/src/app/requirements.txt .
RUN pip install --upgrade pip
RUN pip install --no-cache /wheels/*

WORKDIR /usr/src/app

COPY code_bert  /usr/src/app/code_bert/
COPY libs /usr/src/app/libs/
COPY queries /usr/src/app/queries/
COPY Model /usr/src/app/Model/
COPY setup.py /usr/src/app/
COPY entrypoint.sh /usr/src/app/entrypoint.sh

RUN pip install -e .

ENTRYPOINT ["/usr/src/app/entrypoint.sh"]
