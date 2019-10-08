FROM python:3.6-alpine

# Build-time metadata as defined at http://label-schema.org
ARG BUILD_DATE
ARG VCS_REF
ARG VERSION=1.0.49
ARG URL=https://download.pureftpd.org/pub/pure-ftpd/releases/pure-ftpd-$VERSION.tar.gz
LABEL maintainer "Martin Donadieu <martindonadieu@gmail.com>"
LABEL org.label-schema.build-date=$BUILD_DATE \
	org.label-schema.name="pure-ftpd and Python supervised api" \
	org.label-schema.description="Provides pure-ftpd with Python api to manage vitural users." \
	org.label-schema.url="https://cashstory.com" \
	org.label-schema.vcs-ref=$VCS_REF \
	org.label-schema.vcs-url="https://github.com/BobCashStory/python-git" \
	org.label-schema.vendor="Cashstory, Inc." \
	org.label-schema.version=$VERSION \
	org.label-schema.schema-version="1.0"

ENV TZ 					Europe/Paris
ENV PUBLIC_HOST 		localhost
ENV MIN_PASV_PORT 		30000
ENV MAX_PASV_PORT 		30099
ENV FTP_MAX_CLIENTS		50
ENV FTP_MAX_CONNECTIONS 5

# Install Git
RUN apk update && \
	apk add --no-cache \
	bash \
	# dep for pure-ftpd
	openssl \
	# Install dep uwsgi
	# python3-dev build-base linux-headers pcre-dev \
	# Install tzdata for cron job
	tzdata && \
	# Install uwsgi
	# pip3 install uwsgi \	
	# Install Flask for api 
	pip3 install Flask \
	escapism \
	# Install chaperone to manage services	
	chaperone && \
	# Create folder for chaperone
	mkdir -p /etc/chaperone.d && \
	# Build and install pure-ftpd	
	set -ex && \
	apk add --no-cache --virtual .build-deps \
	build-base \
	curl \
	openssl-dev \
	tar && \
	cd /tmp && \
	curl -sSL $URL | tar xz --strip 1 && \
	./configure --prefix=/usr \
	--sysconfdir=/etc/pure-ftpd \
	--with-throttling \
	--with-puredb \
	--with-peruserlimits \
	--with-ratios \
	--with-tls \
	--without-inetd && \
	make install-strip && \
	cd .. && \
	rm -rf /tmp/* && \
	apk del .build-deps && \
	rm -rf /tmp/* /var/tmp/* /var/cache/apk/*

# Copy chaperone config
COPY confs/chaperone.conf /etc/chaperone.d/chaperone.conf

# copy api
COPY api.py /bin/api.py
RUN chmod u+x /bin/api.py

# setup run/init file
COPY run_pure_ftpd.sh /usr/local/bin/run_pure_ftpd.sh
RUN chmod u+x /usr/local/bin/run_pure_ftpd.sh

VOLUME ["/home/ftpusers", "/etc/pure-ftpd"]

# startup
ENTRYPOINT ["/usr/local/bin/chaperone"]

EXPOSE 5000 21 $MIN_PASV_PORT-$MAX_PASV_PORT