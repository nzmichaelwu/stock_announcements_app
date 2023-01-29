# syntax=docker/dockerfile:1

FROM python:3.7-slim-buster

# Install system libraries
RUN apt-get update && apt-get install -y \
  apache2-utils \
  curl \
  expect \
  gdebi-core \
  gnupg \
  gnupg1 \
  gnupg2 \
  libcurl4-gnutls-dev \
  libsasl2-dev \
  python-dev \
  libldap2-dev \
  libssl-dev \
  nginx \
  protobuf-compiler \
  ssh \
  sssd \
  sssd-tools \
  supervisor \
  sudo \
  syslog-ng \
  tk \
  tzdata \
  unzip \
  vim \
  wget \
  xvfb \
  ## Remove temporary files.
  && rm -rf /var/log/* /var/lib/apt/lists/* \
  # Config ssh
  && mkdir -p /var/run/sshd /var/log/sshd var/log/lastlog/ \
  && sed -i 's/#PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config \
  && sed -i 's/#ChallengeResponseAuthentication.*/ChallengeResponseAuthentication no/' /etc/ssh/sshd_config

COPY ./authorized_keys /root/.ssh/authorized_keys

# Set timezone to Sydney
ENV TZ=Australia/Sydney
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime && echo $TZ > /etc/timezone

# set working directory
WORKDIR /usr/src/backend

# add and install requirements
COPY ./requirements.txt /usr/src/backend/requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# # add entrypoint.sh
# COPY ./entrypoint.sh /usr/src/backend/entrypoint.sh
# RUN chmod +x /usr/src/backend/entrypoint.sh

# add app
COPY . /usr/src/backend

# ENTRYPOINT ["/usr/src/backend/entrypoint.sh"]

EXPOSE 1234

CMD ["gunicorn", "app:app", "--bind", "0.0.0.0:1234", "--workers=4", "--timeout=240"]

# Run app
# CMD ["python", "/usr/src/backend/app.py"]
