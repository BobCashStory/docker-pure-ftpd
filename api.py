#!/bin/python3

from flask import Flask, request, jsonify
import os
import subprocess
from os import urandom

app = Flask(__name__)

apiKey = urandom(30).hex()
if os.getenv('X_API_KEY') is not None:
    apiKey = os.environ['X_API_KEY']
else:
    print("Your X-Api-Key is: " + apiKey)


def goodApiKey(headers):
    auth = headers.get("X-Api-Key")
    if auth != apiKey:
        return False
    else:
        return True


def parseLine(line):
    arrLine = line.split(':')
    return [arrLine[0].strip(), arrLine[1].strip()]


def parseInfo(res):
    arrRes = res.split('\n')
    result = {}
    for line in arrRes:
        parsedLine = parseLine(line)
        result[parsedLine[0]] = parsedLine[1]
        pass
    return result


def jsonToComand(json):
    command = ''
    if json['chroot'] is not None and json['chroot'] == True:
        command = '-d '
    else:
        command = '-D '
    if json['directory is not None'] is not None:
        command += json['directory'] + " "
    else:
        command += json['username'] + " "
    if json['download_bandwidth'] is not None:
        command += "-t " + json['download_bandwidth'] + " "
    if json['upload_bandwidth'] is not None:
        command += "-T " + json['upload_bandwidth'] + " "
    if json['max_files_number'] is not None:
        command += "-n " + json['max_files_number'] + " "
    if json['max_files_Mbytes'] is not None:
        command += "-N " + json['max_files_Mbytes'] + " "
    if json['upload_ratio'] is not None:
        command += "-q " + json['upload_ratio'] + " "
    if json['download_ratio'] is not None:
        command += "-Q " + json['download_ratio'] + " "
    if json['allow_client_ip'] is not None:
        command += "-r " + json['allow_client_ip'] + " "
    if json['deny_client_ip'] is not None:
        command += "-R " + json['deny_client_ip'] + " "
    if json['allow_local_ip'] is not None:
        command += "-i " + json['allow_local_ip'] + " "
    if json['deny_local_ip'] is not None:
        command += "-I " + json['deny_local_ip'] + " "
    if json['max_concurrent_sessions'] is not None:
        command += "-y " + json['max_concurrent_sessions'] + " "
    if json['max_concurrent_login_attempts'] is not None:
        command += "-C " + json['max_concurrent_login_attempts'] + " "
    if json['memory_reserve_password_hashing'] is not None:
        command += "-M " + json['memory_reserve_password_hashing'] + " "
    if json['allowed_range_day'] is not None:
        command += "-z " + json['allowed_range_day'] + " "
    # force commit changes
    command += "-m"
    # -D/-d < home directory > [-c < gecos > ]
    #     [-t < download bandwidth >] [-T < upload bandwidth > ]
    #     [-n < max number of files >] [-N < max Mbytes > ]
    #     [-q < upload ratio >] [-Q < download ratio > ]
    #     [-r < allow client ip > / < mask >] [-R < deny client ip > / < mask > ]
    #     [-i < allow local ip > / < mask >] [-I < deny local ip > / < mask > ]
    #     [-y < max number of concurrent sessions > ]
    #     [-C < max number of concurrent login attempts > ]
    #     [-M < total memory (in MB) to reserve for password hashing > ]
    #     [-z < hhmm > - < hhmm > ] [-m]
    return command


@app.route('/user/del', methods=['POST'])
def delUser():
    if goodApiKey(request.headers):
        if (request.form['username'] is None):
            return jsonify({"message": "ERROR: missing username"}), 401
        command = "pure-pw userdel " + request.form['username']
        os.system(command)
        return jsonify({"message": "OK: Deleted"}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route('/user/edit', methods=['PUT'])
def editUser():
    if goodApiKey(request.headers):
        if (request.form['username'] is None):
            return jsonify({"message": "ERROR: missing username/password"}), 401
        username = request.form['username']
        options = jsonToComand(request.form)
        command = "pure-pw usermod " + username + " " + options
        os.system(command)
        return jsonify({"message": "OK: Edited"}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route('/user/password', methods=['POST'])
def setUserPwd():
    if goodApiKey(request.headers):
        if (request.form['username'] is None or request.form['password'] is None):
            return jsonify({"message": "ERROR: missing username/password"}), 401
        password = request.form['password']
        username = request.form['username']
        command = "echo \"" + password + "\n" + password + \
            "\n\" | pure-pw passwd " + username
        os.system(command)
        return jsonify({"message": "OK: Updated"}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route('/user/info', methods=['GET'])
def getUser():
    if goodApiKey(request.headers):
        if (request.form['username'] is None):
            return jsonify({"message": "ERROR: missing username"}), 401
        command = "pure-pw show " + request.form['username']
        result = subprocess.check_output([command])
        jsonResult = parseInfo(result)
        return jsonify(jsonResult), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route('/user/add', methods=['POST'])
def addUser():
    if goodApiKey(request.headers):
        if (request.form['username'] is None or request.form['password'] is None):
            return jsonify({"message": "ERROR: missing username/password"}), 401
        password = request.form['password']
        username = request.form['username']
        options = jsonToComand(request.form)
        command = "echo \"" + password + "\n" + password + \
            "\n\" | pure-pw useradd " + username + " -u ftpuser -j " + options
        os.system(command)
        return jsonify({"message": "OK: Created"}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0')
