FROM tobix/wine:stable

ENV WINEDEBUG -all
ENV WINEPREFIX /opt/wineprefix

COPY wine-init.sh SHA256SUMS.txt keys.gpg /tmp/helper/
COPY mkuserwineprefix /opt/

# Prepare environment
RUN xvfb-run sh /tmp/helper/wine-init.sh

ARG PYTHON_VERSION=3.10.6
ARG UPX_VERSION=3.96

RUN umask 0 && cd /tmp/helper && \
  curl -LOOO \
    https://www.python.org/ftp/python/${PYTHON_VERSION}/python-${PYTHON_VERSION}-amd64.exe{,.asc} \
    https://github.com/upx/upx/releases/download/v${UPX_VERSION}/upx-${UPX_VERSION}-win64.zip \
  && \
  gpgv --keyring ./keys.gpg python-${PYTHON_VERSION}-amd64.exe.asc python-${PYTHON_VERSION}-amd64.exe && \
  sha256sum -c SHA256SUMS.txt && \
  xvfb-run sh -c "\
    wine python-${PYTHON_VERSION}-amd64.exe /quiet TargetDir=C:\\Python310 \
      Include_doc=0 InstallAllUsers=1 PrependPath=1; \
    wineserver -w" && \
  unzip upx*.zip && \
  mv -v upx*/upx.exe ${WINEPREFIX}/drive_c/windows/ && \
  cd .. && rm -Rf helper

RUN apt-get -y update && apt-get install -y \
  git \
  vim

# Install some python software
RUN umask 0 && xvfb-run sh -c "\
  wine pip install --no-warn-script-location pyinstaller; \
  wineserver -w"

# 6. Repo
RUN git clone https://github.com/steingartlab/biologic.git
WORKDIR /biologic
RUN umask 0 && xvfb-run sh -c "wine pip install -r requirements.txt"

ENTRYPOINT umask 0 && xvfb-run sh -c "wine python app.py"