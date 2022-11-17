FROM ubuntu:20.04

ARG USER
ARG UID
ARG GID

RUN ln -fs /usr/share/zoneinfo/US/Eastern /etc/localtime

RUN apt-get update && apt-get install -y software-properties-common apt-utils zsh \
    locales build-essential binutils gcc sudo \
    make wget gdb \
    libz3-dev git curl unzip \
    libboost-all-dev gnupg2  \
    python3 python3-pip python3-venv libcurl4-openssl-dev \
    libc6-dev ncurses-dev xz-utils libssl-dev \
    bc flex libelf-dev bison kernel-wedge zip    

RUN bash -c "$(wget -O - https://apt.llvm.org/llvm.sh)"

RUN apt-get install -y git-core gnupg flex bison gperf build-essential zip curl zlib1g-dev gcc-multilib \
    g++-multilib libc6-dev-i386 lib32ncurses5-dev x11proto-core-dev libx11-dev lib32z-dev \
    libgl1-mesa-dev libxml2-utils xsltproc zip unzip rsync \
    build-essential zlib1g-dev gcc-multilib g++-multilib libc6-dev-i386 libncurses5 \
    lib32ncurses5-dev x11proto-core-dev libx11-dev lib32z1-dev fontconfig

RUN apt-get update && apt-get install -y libssl-dev libreadline-dev libbz2-dev libdb-dev \
    liblzma-dev tk-dev libgdbm-dev uuid-dev

RUN echo "deb http://apt.llvm.org/focal/ llvm-toolchain-focal main" >> /etc/apt/sources.list
RUN echo "deb-src http://apt.llvm.org/focal/ llvm-toolchain-focal main" >>  /etc/apt/sources.list

RUN echo "deb http://apt.llvm.org/focal/ llvm-toolchain-focal-13 main" >>  /etc/apt/sources.list
RUN echo "deb-src http://apt.llvm.org/focal/ llvm-toolchain-focal-13 main" >> /etc/apt/sources.list

RUN echo "deb http://apt.llvm.org/focal/ llvm-toolchain-focal-14 main" >> /etc/apt/sources.list
RUN echo "deb-src http://apt.llvm.org/focal/ llvm-toolchain-focal-14 main" >> /etc/apt/sources.list

RUN apt-key adv --keyserver keyserver.ubuntu.com --recv-keys 15CF4D18AF4F7421

RUN apt-get update && apt-get install -y clang-13
RUN apt-get update && apt-get install -y clang-14

RUN apt-get update && apt-get install -y asciidoctor bison dos2unix flex libtool mingw-w64 \
    pbzip2 python-lxml python-nose python3 texinfo zip ruby-pygments.rb

# llvm build dep
RUN apt-get update && apt-get install -y libeditline-dev ninja-build swig lzma-dev liblzma-dev \
    libxml2-dev libpython3.9-dev lua5.3 libedit-dev liblua5.3-dev

RUN wget -O - https://apt.kitware.com/keys/kitware-archive-latest.asc 2>/dev/null | gpg --dearmor - | sudo tee /etc/apt/trusted.gpg.d/kitware.gpg >/dev/null
RUN apt-add-repository "deb https://apt.kitware.com/ubuntu/ $(lsb_release -cs) main"

RUN apt-get update && apt-get install -y cmake

RUN groupadd -g $GID -o $USER
RUN useradd -m -u $UID -g $GID -o -s /bin/bash $USER
RUN echo "$USER ALL=(ALL) NOPASSWD:ALL" >> /etc/sudoers
# RUN echo PASSWORD | passwd $USER --stdin
RUN usermod -aG sudo $USER

USER $USER
WORKDIR /home/$USER

CMD /bin/bash

