Docker Pure-ftpd Server with API
============================
https://hub.docker.com/r/cashstory/pureftpd-api/

Based on [stilliard pure ftpd](https://github.com/stilliard/docker-pure-ftpd) thanks to his work !
And [Chaperone](https://github.com/garywiz/chaperone) to manage our APi and pure-ftpd.


----------------------------------------

Starting it 
------------------------------

`docker-compose up ftpd_server`

----------------------------------------

Setting runtime FTP options
------------------------------

To check all available options go to [stilliard README](https://github.com/stilliard/docker-pure-ftpd/blob/master/README.md)
Keep in your mind, change docker command will not affect ftp command since now the image run with chaperon to manage both API and ftp process
Fork this repo and edit chaperone conf instead.

The only env option in our docker-compose we provide in addition to stilliard image is
 `X_API_KEY` => if you don't provide it it will be auto created when you run the container.
Don't do it in production it will change at each restart.
 
----------------------------------------

Operating it though API
------------------------------

To add user
curl -X POST --header "X-api-key:YOURAPIKEY" -F 'username=davidwalsh' -F 'password=toto' localhost:5000/user/add

To get user info
curl -X GET --header "X-api-key:YOURAPIKEY" -F 'username=davidwalsh' localhost:5000/user/info

To get list all username
curl -X GET --header "X-api-key:YOURAPIKEY" localhost:5000/user/list

To delete user
curl -X POST --header "X-api-key:YOURAPIKEY" -F 'username=davidwalsh' localhost:5000/user/del

To delete user and keep is folder
curl -X POST --header "X-api-key:YOURAPIKEY" -F 'username=davidwalsh' -F 'archive=true' localhost:5000/user/del

To update user
curl -X PUT --header "X-api-key:YOURAPIKEY" -F 'username=davidwalsh' -F 'directory=toto' localhost:5000/user/edit

To update user password
curl -X PUT --header "X-api-key:YOURAPIKEY" -F 'username=davidwalsh' -F 'password=toto' localhost:5000/user/password

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

----------------------------------------

Our default pure-ftpd options explained
----------------------------------------

they differ from the original repo, we add more secure option, and some sharing options to have facility in volume sharing.
```
/usr/sbin/pure-ftpd # path to pure-ftpd executable
-c 50 # no more than 50 people at once (Speed optimisation)
-C 5 # no more than 5 requests from the same ip (Speed optimisation)
-E # Anonymous logins are prohibited (Security)
-H # avoids host names resolution (Speed optimisation)
-j # --createhomedir (auto create home directory if it doesnt already exist)
-k 90 # Don't allow uploads if the partition is more than 95% full (Security)
-l puredb:/etc/pure-ftpd/pureftpd.pdb # --login (login file for virtual users)
-P $PUBLICHOST # IP/Host setting for PASV support, passed in your the PUBLICHOST env var
-p 30000:30099 # PASV port range (100 ports for 50 max clients)
-R # Disallow users usage of the CHMOD command. (Security)
-U 113:002 # set umask to allow shared volume to work (Facility)
-X # users can't *read* files and directories beginning with a dot (Security)
-Z # protect customers against common mistakes, bad chmod (Security)
-tls 1 # Enables optional TLS support (Security)
```

For more information please see `man pure-ftpd`, or visit: https://www.pureftpd.org/

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

----------------------------------------

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

----------------------------------------

Automatic TLS certificate generation
------------------------------

If `ADDED_FLAGS` contains `--tls` and file `/etc/ssl/private/pure-ftpd.pem` does not exists
it is possible to generate self-signed certificate if `TLS_CN`, `TLS_ORG` and `TLS_C` are set.

Keep in mind that if no volume is set for `/etc/ssl/private/` directory generated
certificates won't be persisted and new ones will be generated on each start.
