#Stage 1 : builder debian image
FROM debian:stretch as builder

# properly setup debian sources
ENV DEBIAN_FRONTEND noninteractive
RUN echo "deb http://http.debian.net/debian stretch main\n\
	deb-src http://http.debian.net/debian stretch main\n\
	deb http://http.debian.net/debian stretch-updates main\n\
	deb-src http://http.debian.net/debian stretch-updates main\n\
	deb http://security.debian.org stretch/updates main\n\
	deb-src http://security.debian.org stretch/updates main\n\
	" > /etc/apt/sources.list

# install package building helpers
# rsyslog for logging (ref https://github.com/stilliard/docker-pure-ftpd/issues/17)
RUN apt-get -y update && \
	apt-get -y --force-yes --fix-missing install dpkg-dev debhelper && \
	apt-get -y build-dep pure-ftpd

# Build from source - we need to remove the need for CAP_SYS_NICE and CAP_DAC_READ_SEARCH
RUN mkdir /tmp/pure-ftpd/ && \
	cd /tmp/pure-ftpd/ && \
	apt-get source pure-ftpd && \
	cd pure-ftpd-* && \
	./configure --with-tls | grep -v '^checking' | grep -v ': Entering directory' | grep -v ': Leaving directory' && \
	sed -i '/CAP_SYS_NICE,/d; /CAP_DAC_READ_SEARCH/d; s/CAP_SYS_CHROOT,/CAP_SYS_CHROOT/;' src/caps_p.h && \
	dpkg-buildpackage -b -uc | grep -v '^checking' | grep -v ': Entering directory' | grep -v ': Leaving directory'


#Stage 2 : actual pure-ftpd image
FROM debian:stretch

# feel free to change this ;)
LABEL maintainer "Martin Donadieu <martindonadieu@gmail.com>"

# install dependencies
# FIXME : libcap2 is not a dependency anymore. .deb could be fixed to avoid asking this dependency
ENV DEBIAN_FRONTEND noninteractive
RUN apt-get -y update && \
	apt-get  --no-install-recommends --yes install \
	openbsd-inetd \
	rsyslog \
	lsb-base \
	libc6 \
	libcap2 \
	libpam0g \
	libssl1.1 \
	openssl \
	python3 \
	python3-setuptools \
	python3-pip && \
	pip3 install Flask chaperone && \
	# Create folder for chaperone
	mkdir -p /etc/chaperone.d

COPY --from=builder /tmp/pure-ftpd/*.deb /tmp/pure-ftpd/

# install the new deb files
RUN dpkg -i /tmp/pure-ftpd/pure-ftpd-common*.deb &&\
	dpkg -i /tmp/pure-ftpd/pure-ftpd_*.deb && \
	rm -Rf /tmp/pure-ftpd 

# Prevent pure-ftpd upgrading
RUN apt-mark hold pure-ftpd pure-ftpd-common

# setup ftpgroup and ftpuser
RUN groupadd ftpgroup &&\
	useradd -g ftpgroup -d /home/ftpusers -s /dev/null ftp

# configure rsyslog logging
RUN echo "" >> /etc/rsyslog.conf && \
	echo "#PureFTP Custom Logging" >> /etc/rsyslog.conf && \
	echo "ftp.* /var/log/pure-ftpd/pureftpd.log" >> /etc/rsyslog.conf && \
	echo "Updated /etc/rsyslog.conf with /var/log/pure-ftpd/pureftpd.log"


# Copy chaperone config
COPY confs/chaperone.conf /etc/chaperone.d/chaperone.conf

# copy api
COPY api.py /bin/api.py
RUN chmod u+x /bin/api.py

# setup run/init file
COPY run_pure_ftpd.sh /usr/local/bin/run_pure_ftpd.sh
RUN chmod u+x /usr/local/bin/run_pure_ftpd.sh

# default publichost, you'll need to set this for passive support
ENV PUBLICHOST localhost

# couple available volumes you may want to use
VOLUME ["/home/ftpusers", "/etc/pure-ftpd"]

# startup
ENTRYPOINT ["chaperone"]

EXPOSE 5000 21 30000-30099
