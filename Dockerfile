# 1. Base image
FROM ubuntu:20.04

# Timezone Set
ENV TZ=America/New_York
RUN ln -snf /usr/share/zoneinfo/$TZ /etc/localtime \
    && echo $TZ > /etc/timezone

###################

# 2. Supporting Linux packages
RUN apt-get update && apt-get install -y \
    gnupg2 \
    software-properties-common \
    wget \
    git

###################

# 3. Wine
RUN dpkg --add-architecture i386 && \
    wget -nc -O /usr/share/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key && \
    wget -nc -P /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/focal/winehq-focal.sources

RUN apt-get update && apt-get install -y \
    winehq-stable \
    winetricks

###################

# 4. Python
ARG PYTHON_VERSION=3.7.9
ARG PYINSTALLER_VERSION=4.0

ENV WINEPREFIX /wine
# xvfb settings
ENV DISPLAY :0 winecfg
RUN set -x \
    && echo 'Xvfb $DISPLAY -screen 0 1024x768x24 &' >> /root/.bashrc
# RUN set -x \
#     && ( Xvfb :0 -screen 0 1024x768x16 & ) \
#     && sleep 5

# windows 10 environment
RUN set -x \
    && winetricks -q win10


RUN set -x \
    && for msifile in `echo core dev exe lib path pip tcltk tools`; do \
    wget -nv "https://www.python.org/ftp/python/3.7.9/amd64/${msifile}.msi"; \
    wine msiexec /i "${msifile}.msi" /qb TARGETDIR=C:/Python37; \
    rm ${msifile}.msi; \
    done \
    && cd /wine/drive_c/Python37 \
    && echo 'wine '\''C:\Python37\python.exe'\'' "$@"' > /usr/bin/python \
    && echo 'wine '\''C:\Python37\Scripts\easy_install.exe'\'' "$@"' > /usr/bin/easy_install \
    && echo 'wine '\''C:\Python37\Scripts\pip.exe'\'' "$@"' > /usr/bin/pip \
    && echo 'wine '\''C:\Python37\Scripts\pyinstaller.exe'\'' "$@"' > /usr/bin/pyinstaller \
    && echo 'wine '\''C:\Python37\Scripts\pyupdater.exe'\'' "$@"' > /usr/bin/pyupdater \
    && echo 'assoc .py=PythonScript' | wine cmd \
    && echo 'ftype PythonScript=c:\Python37\python.exe "%1" %*' | wine cmd \
    && while pgrep wineserver >/dev/null; do echo "Waiting for wineserver"; sleep 1; done \
    && chmod +x /usr/bin/python /usr/bin/easy_install /usr/bin/pip /usr/bin/pyinstaller /usr/bin/pyupdater \
    && rm -rf /tmp/.wine-*

# # ###################
ENV WINEARCH win64
ENV DEBIAN_FRONTEND noninteractive
ENV WINEDEBUG fixme-all
ENV DISPLAY :0
RUN set -x \
    && echo 'Xvfb $DISPLAY -screen 0 1024x768x24 &' >> /root/.bashrc
# # WORKDIR /wine
# # # 5. Drivers. Download and install
# RUN wget https://www.biologic.net/wp-content/uploads/2019/09/ec-lab-oem-package-setup.exe \
#     && wine ec-lab-oem-package-setup.exe

# # ###################

# 6. Repo
RUN git clone https://github.com/steingartlab/biologic.git
WORKDIR /biologic
RUN wine pip install -r requirements.txt

RUN ls

# # ###################

# # # 7. Run app
ENTRYPOINT ["wine"]
CMD ["python app.py"] 