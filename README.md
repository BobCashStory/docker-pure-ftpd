Docker Pure-ftpd Server
============================
https://hub.docker.com/r/cashstory/pureftpd-api/

[![Build Status](https://travis-ci.org/stilliard/docker-pure-ftpd.svg?branch=master)](https://travis-ci.org/stilliard/docker-pure-ftpd)
[![Docker Build Status](https://img.shields.io/docker/build/cashstory/pureftpd-api.svg)](https://hub.docker.com/r/cashstory/pureftpd-api/)
[![Docker Pulls](https://img.shields.io/docker/pulls/cashstory/pureftpd-api.svg)](https://hub.docker.com/r/cashstory/pureftpd-api/)
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fstilliard%2Fdocker-pure-ftpd.svg?type=shield)](https://app.fossa.io/projects/git%2Bgithub.com%2Fstilliard%2Fdocker-pure-ftpd?ref=badge_shield)


----------------------------------------

#### Check out our [basic example workflow](https://github.com/stilliard/docker-pure-ftpd/wiki/Basic-example-walk-through) & our [slightly more advanced workflow with tls & an auto created user](https://github.com/stilliard/docker-pure-ftpd/wiki/Advanced-example-walk-through-with-TLS-&-automatic-user-account).

----------------------------------------

Pull down latest version with docker:
```bash
docker pull cashstory/pureftpd-api
```

**Often needing to run as `sudo`, e.g. `sudo docker pull cashstory/pureftpd-api`**

----------------------------------------

**If you want to make changes, my advice is to either change the run command when running it or extend this image to make any changes rather than forking the project.**  
This is because rebuilding the entire docker image via a fork can be *very* slow as it rebuilds the entire pure-ftpd package from source. 

To change the command run on start you could use the `command:` option if using `docker-compose`, or with [`docker run`](https://docs.docker.com/engine/reference/run/) directly you could use:

```
docker run --rm -d --name ftpd_server -p 21:21 -p 30000-30099:30000-30099 cashstory/pureftpd-api:hardened bash /run.sh -c 30 -C 10 -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -R -P localhost -p 30000:30059 -e "X_API_KEY=YOURKEY"
```

To extend it you can create a new project with a `DOCKERFILE` like so:

```
FROM cashstory/pureftpd-api

# e.g. you could change the defult command run:
CMD /run.sh -c 30 -C 10 -l puredb:/etc/pure-ftpd/pureftpd.pdb -E -j -R -P $PUBLICHOST -p 30000:30059
```

*Then you can build your own image, `docker build --rm -t my-pure-ftp .`, where my-pure-ftp is the name you want to build as*

----------------------------------------

Starting it 
------------------------------

`docker run -d --name ftpd_server -p 21:21 -p 30000-30099:30000-30099 -e "PUBLICHOST=localhost" cashstory/pureftpd-api:hardened`

*Or for your own image, replace cashstory/pureftpd-api with the name you built it with, e.g. my-pure-ftp*

You can also pass ADDED_FLAGS as an env variable to add additional options such as --tls to the pure-ftpd command.  
e.g. ` -e "ADDED_FLAGS=--tls=2" `


Operating it
------------------------------

`docker exec -it ftpd_server /bin/bash`

Setting runtime FTP user
------------------------------

To create a user on the ftp container, use the following environment variables: `FTP_USER_NAME`, `FTP_USER_PASS` and `FTP_USER_HOME`.

`FTP_USER_HOME` is the root directory of the new user.

Example usage:

`docker run -e FTP_USER_NAME=bob -e FTP_USER_PASS=12345 -e FTP_USER_HOME=/home/bob cashstory/pureftpd-api`

If you wish to set the `UID` & `GID` of the FTP user, use the `FTP_USER_UID` & `FTP_USER_GID` environment variables.

Using different passive ports
------------------------------

To use passive ports in a different range (*eg*: `10000-10009`), use the following setup:

`docker run -e FTP_PASSIVE_PORTS=10000:10009 --expose=10000-10009 -p 21:21 -p 10000-10009:10000-10009`

You may need the `--expose=` option, because default passive ports exposed are `30000` to `30009`.

Example usage once inside
------------------------------

Create an ftp user: `e.g. bob with chroot access only to /home/ftpusers/bob`
```bash
pure-pw useradd bob -f /etc/pure-ftpd/pureftpd.passwd -m -u ftp -d /home/ftpusers/bob
```
*No restart should be needed.*

*If you have any trouble with volume permissions due to the **uid** or **gid** of the created user you can change the **-u** flag for the uid you would like to use and/or specify **-g** with the group id as well. For more information see issue [#35](https://github.com/stilliard/docker-pure-ftpd/issues/35#issuecomment-325583705).*

More info on usage here: https://download.pureftpd.org/pure-ftpd/doc/README.Virtual-Users

Example usage using api
------------------------------

To add user
curl -X POST --header "X-api-key:YOURAPIKEY" -F 'username=davidwalsh' -F 'password=toto' localhost:5000/user/add

To get user info
curl -X GET --header "X-api-key:YOURAPIKEY" -F 'username=davidwalsh' localhost:5000/user/info

To delete user
curl -X POST --header "X-api-key:YOURAPIKEY" -F 'username=davidwalsh' -F 'password=toto' localhost:5000/user/del

To get user info
curl -X GET --header "X-api-key:YOURAPIKEY" -F 'username=davidwalsh' -F 'password=toto' localhost:5000/user/info

To update user
curl -X PUT --header "X-api-key:YOURAPIKEY" -F 'username=davidwalsh' -F 'directory=toto' localhost:5000/user/edit

all allowed config for `add` and `edit`, to understand better check https://download.pureftpd.org/pub/pure-ftpd/doc/README.Virtual-Users
```
{
chroot: boolean,
directory: string,
download_bandwidth: number,
upload_bandwidth: number,
max_files_number: number,
max_files_Mbytes: number,
upload_ratio: number,
download_ratio: number,
allow_client_ip: string,
deny_client_ip: string,
allow_local_ip: string,
deny_local_ip: string,
max_concurrent_sessions: number,
max_concurrent_login_attempts: number,
memory_reserve_password_hashing: number,
allowed_range_day: string,
}
```

Test your connection
-------------------------
From the host machine:
```bash
ftp -p localhost 21
```

-------------------------

Docker compose
-------------------------
Docker compose can help you simplify the orchestration of your containers.   
We have a simple [example of the docker compose](https://github.com/stilliard/docker-pure-ftpd/blob/master/docker-compose.yml).  
& here's a [more detailed example using wordpress](https://github.com/stilliard/docker-pure-ftpd/wiki/Docker-stack-with-Wordpress-&-FTP) with ftp using this image.

-------------------------

Max clients
-------------------------
By default we set 50 max clients at once, but you can increase this by using the following environment variable `FTP_MAX_CLIENTS`, e.g. to `FTP_MAX_CLIENTS=500` and then also increasing the number of public ports opened from `FTP_PASSIVE_PORTS=30000:30099` `FTP_PASSIVE_PORTS=30000:30199`. You'll also want to open those ports when running docker run.
In addition you can specify the maximum connections per ip by setting the environment variable `FTP_MAX_CONNECTIONS`. By default the value is 5.

All Pure-ftpd flags available:
--------------------------------------
https://linux.die.net/man/8/pure-ftpd

Logs
-------------------------
To get verbose logs add the following to your `docker run` command:
```
-e "ADDED_FLAGS=-d -d"
```

Then if you exec into the container you could watch over the log with `tail -f /var/log/messages`

Want a transfer log file? add the following to your `docker run` command:
```bash
-e "ADDED_FLAGS=-O w3c:/var/log/pure-ftpd/transfer.log"
```

----------------------------------------

Tags available for different versions
--------------------------------------

**Latest versions**

- `latest` - latest working version
- `jessie-latest` - latest but will always remain on debian jessie
- `hardened` - latest + [more secure/hardened defaults](https://github.com/stilliard/docker-pure-ftpd/issues/10)

**Previous version before tags were introduced**

- `wheezy-1.0.36` - incase you want to roll back to before we started using debian jessie

**Specific pure-ftpd versions**

- `jessie-1.x.x` - jessie + specific versions, e.g. jessie-1.0.36
- `hardened-1.x.x` - hardened + specific versions

*Check the tags on github for available versions, feel free to submit issues and/or pull requests for newer versions*

Usage of specific tags: 
`sudo docker pull cashstory/pureftpd-api:hardened-1.0.36`

**An arm64 build is also available here:** https://hub.docker.com/r/zhabba/pure-ftpd-arm64 *- Thanks @zhabba*

----------------------------------------

Our default pure-ftpd options explained
----------------------------------------

```
/usr/sbin/pure-ftpd # path to pure-ftpd executable
-c 50 # --maxclientsnumber (no more than 50 people at once)
-C 5 # --maxclientsperip (no more than 5 requests from the same ip)
-l puredb:/etc/pure-ftpd/pureftpd.pdb # --login (login file for virtual users)
-E # --noanonymous (only real users)
-j # --createhomedir (auto create home directory if it doesnt already exist)
-R # --nochmod (prevent usage of the CHMOD command)
-P $PUBLICHOST # IP/Host setting for PASV support, passed in your the PUBLICHOST env var
-p 30000:30099 # PASV port range (100 ports for 50 max clients)
-tls 1 # Enables optional TLS support
```

For more information please see `man pure-ftpd`, or visit: https://www.pureftpd.org/

Why so many ports opened?
---------------------------
This is for PASV support, please see: [#5 PASV not fun :)](https://github.com/stilliard/docker-pure-ftpd/issues/5)

----------------------------------------

Docker Volumes
--------------
There are a few spots onto which you can mount a docker volume to configure the
server and persist uploaded data. It's recommended to use them in production. 

  - `/home/ftpusers/` The ftp's data volume (by convention). 
  - `/etc/pure-ftpd` A directory containing the single `pureftpd.passwd`
    file which contains the user database (i.e., all virtual users, their
    passwords and their home directories). This is read on startup of the
    container and updated by the `pure-pw useradd -f /etc/pure-
    ftpd/pureftpd.passwd ...` command.
  - `/etc/ssl/private/` A directory containing a single `pure-ftpd.pem` file
    with the server's SSL certificates for TLS support. Optional TLS is
    automatically enabled when the container finds this file on startup.

Keep user database in a volume
------------------------------
You may want to keep your user database through the successive image builds. It is possible with Docker volumes.

Create a named volume:
```
docker volume create --name my-db-volume
```

Specify it when running the container:
```
docker run -d --name ftpd_server -p 21:21 -p 30000-30099:30000-30099 -e "PUBLICHOST=localhost" -v my-db-volume:/etc/pure-ftpd cashstory/pureftpd-api:hardened
```

When an user is added, you need to use the password file which is in the volume:
```
pure-pw useradd bob -f /etc/pure-ftpd/pureftpd.passwd -m -u ftp -d /home/ftpusers/bob
```
(Thanks to the -m option, you don't need to call *pure-pw mkdb* with this syntax).


Changing a password
---------------------
e.g. to change the password for user "bob":
```
pure-pw passwd bob -f /etc/pure-ftpd/pureftpd.passwd -m
```

----------------------------------------
Development (via git clone)
```bash
# Clone the repo
git clone https://github.com/stilliard/docker-pure-ftpd.git
cd docker-pure-ftpd
# Build the image
make build
# Run container in background:
make run
# enter a bash shell inside the container:
make enter
# test that it's all working with
make test
```

TLS
----

If you want to enable tls (for ftps connections), you need to have a valid
certificate. You can get one from one of the certificate authorities that you'll
find when googling this topic. The certificate (containing private key and
certificate) needs to be at:

```
/etc/ssl/private/pure-ftpd.pem
```

Use docker volumes to get the certificate there at runtime. The container will
automatically enable optional TLS when it detect the file at this location.

You can also self-sign a certificate, which is certainly the easiest way to
start out. Self signed certificates come with certain drawbacks, but it might
be better to have a self signed one than none at all.

Here's how to create a self-signed certificate from within the container:

```bash
mkdir -p /etc/ssl/private
openssl dhparam -out /etc/ssl/private/pure-ftpd-dhparams.pem 2048
openssl req -x509 -nodes -newkey rsa:2048 -sha256 -keyout \
    /etc/ssl/private/pure-ftpd.pem \
    -out /etc/ssl/private/pure-ftpd.pem
chmod 600 /etc/ssl/private/*.pem
```

Automatic TLS certificate generation
------------------------------

If `ADDED_FLAGS` contains `--tls` and file `/etc/ssl/private/pure-ftpd.pem` does not exists
it is possible to generate self-signed certificate if `TLS_CN`, `TLS_ORG` and `TLS_C` are set.

Keep in mind that if no volume is set for `/etc/ssl/private/` directory generated
certificates won't be persisted and new ones will be generated on each start.

You can also pass `-e "TLS_USE_DSAPRAM=true"` for faster generated certificates
though this option is not recommended for production.

Credits
-------------
Thanks for the help on stackoverflow with this!
https://stackoverflow.com/questions/23930167/installing-pure-ftpd-in-docker-debian-wheezy-error-421

Also thanks to all the awesome contributors that have made this project amazing!
https://github.com/stilliard/docker-pure-ftpd/graphs/contributors

## License
[![FOSSA Status](https://app.fossa.io/api/projects/git%2Bgithub.com%2Fstilliard%2Fdocker-pure-ftpd.svg?type=large)](https://app.fossa.io/projects/git%2Bgithub.com%2Fstilliard%2Fdocker-pure-ftpd?ref=badge_large)
