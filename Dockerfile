FROM debian:buster as Builder

RUN apt-get update \
	&& apt-get -y install \
		git \
		wget \
		build-essential \
		llvm \
		llvm-dev \
		gcc-multilib \
		g++-multilib \
		cmake \
		automake \
		autogen \
		pkg-config \
		sed \
		clang \
		libxml2-dev \
		patch \
        libfreetype6-dev \
        libfontconfig1-dev \
        libssl-dev \
		zlib1g-dev \
        libopenjp2-7-dev \
        libjpeg-dev \
        libcairo2-dev \
		python \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

RUN mkdir -p /build/linux_x64 && mkdir -p /build/data
#RUN cd /build/ \
#	&& wget -O poppler.tar.xz https://poppler.freedesktop.org/poppler-21.06.1.tar.xz \
#	&& mkdir poppler \
#	&& tar -xf poppler.tar.xz -C poppler --strip-components=1

ENV COMMON_OPTIONS \
		-DCMAKE_BUILD_TYPE=release \
        -DBUILD_SHARED_LIBS=OFF \
		-DBUILD_GTK_TESTS=OFF \
		-DBUILD_QT4_TESTS=OFF \
		-DBUILD_QT5_TESTS=OFF \
		-DBUILD_CPP_TESTS=OFF \
		-DENABLE_SPLASH=OFF \
		-DENABLE_CPP=OFF \
		-DENABLE_GLIB=OFF \
		-DENABLE_GTK_DOC=OFF \
		-DENABLE_QT4=OFF \
		-DENABLE_QT5=OFF \
		-DENABLE_LIBOPENJPEG=openjpeg2 \
		-DENABLE_CMS=none \
		-DENABLE_LIBCURL=OFF \
		-DENABLE_ZLIB=OFF \
		-DENABLE_DCTDECODER=libjpeg \
		-DENABLE_ZLIB_UNCOMPRESS=OFF \
        -DENABLE_LIBJPEG=ON \
		-DSPLASH_CMYK=OFF \
		-DWITH_JPEG=ON \
		-DWITH_PNG=ON \
		-DWITH_TIFF=OFF \
		-DWITH_NSS3=OFF \
		-DWITH_Cairo=ON \
        -DWITH_OPENJPEG=ON \
		-DWITH_FONTCONFIGURATION_FONTCONFIG=OFF \
        -DPOPPLER_DATADIR=/opt/bin/ \
        -DTESTDATADIR=/build/test

RUN cd /build/linux_x64 \
	&& cmake /build/poppler \
			-DCMAKE_CXX_FLAGS="-std=c++11 -Os" \
			-DCMAKE_EXE_LINKER_FLAGS="-pthread" \
			${COMMON_OPTIONS} \
    && make

#RUN mkdir /build/pdftools \
#	&& cd /build/pdftools \
#	&& cp -v /build/linux_x64/utils/pdf* .

#RUN cd /build/ \
#	&& wget -O poppler-data.tar.gz https://poppler.freedesktop.org/poppler-data-0.4.10.tar.gz \
#	&& mkdir poppler-data \
#	&& tar -xf poppler-data.tar.gz -C poppler-data --strip-components=1 \
#	&& cd pdftools \
#	&& mkdir -p poppler-data \
#	&& cd poppler-data \
#	&& cp -r ../../poppler-data/cidToUnicode ./ \
#	&& cp -r ../../poppler-data/cMap ./ \
#	&& cp -r ../../poppler-data/nameToUnicode ./ \
#	&& cp -r ../../poppler-data/unicodeMap ./ \
#	&& cp -r ../../poppler-data/COPYING ./ \
#	&& cp -r ../../poppler-data/COPYING.adobe ./ \
#	&& cp -r ../../poppler-data/COPYING.gpl2 ./ \
#	&& cd .. \
#	&& ls -l \
#	&& tar -cvzf ../pdftools.tar.gz *

FROM public.ecr.aws/lambda/python:3.8

#RUN yum install -y file-devel git-core tar poppler-utils

#COPY --from=Builder /build/pdftools.tar.gz .
#RUN mkdir -p /opt/bin
#RUN tar xf pdftools.tar.gz -C /opt/bin/
#RUN ls /opt/bin/

ADD ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
RUN yum remove -y git-core && yum clean all
#ADD riskstream riskstream
ADD api api
CMD ["app.handler"]
