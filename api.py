#!/bin/python3

from flask import Flask, request, jsonify
import os
import sys
import subprocess
from os import urandom

app = Flask(__name__)

apiKey = urandom(30).hex()
if os.getenv('X_API_KEY') is not None:
    apiKey = os.environ['X_API_KEY']
else:
    print("Your X-Api-Key is: " + apiKey)


def commandPass(password):
    return ["echo", "-e", confirmPass(password)]


def commandPureFtp(cmd, username, options):
    cmd = ["pure-pw", cmd, username]
    cmd.extend(options)
    return cmd


def cleanError(output):
    if output.startswith('Error'):
        return output
    cleanErr = output.split('Error')
    cleanErr[0] = ''
    return 'Error'.join(cleanErr).replace('\n', ' ').strip()


def confirmPass(password):
    return password + "\n" + password + "\n"


def printPass(password):
    return "echo -e \"" + password + "\n" + password + "\""


def goodApiKey(headers):
    auth = headers.get("X-Api-Key")
    if auth != apiKey:
        return False
    else:
        return True


def parseLine(line):
    arrLine = line.split(':')
    return [item.strip() for item in arrLine]


def parseInfo(res):
    arrRes = res.split('\n')
    result = {}
    for line in arrRes:
        parsedLine = parseLine(line)
        if (len(parsedLine) > 1):
            result[parsedLine[0].replace(' ', '_')] = parsedLine[1]
        pass
    return result


def jsonToCommandArr(json):
    # print("json", json)
    # print("json", request.json, file=sys.stderr)
    command = []
    if json.get('chroot') is not None and json.get('chroot') == False:
        command.append('-D')
    else:
        command.append('-d')
    if json.get('directory') is not None:
        command.append("/home/ftpusers" + json.get('directory'))
    else:
        folderName = json.get('username').replace('@', '__').replace('.', '_')
        command.append("/home/ftpusers/" + folderName)
    if json.get('download_bandwidth') is not None:
        command.append("-t")
        command.append(json.get('download_bandwidth'))
    if json.get('upload_bandwidth') is not None:
        command.append("-T")
        command.append(json.get('upload_bandwidth'))
    if json.get('max_files_number') is not None:
        command.append("-n")
        command.append(json.get('max_files_number'))
    if json.get('max_files_Mbytes') is not None:
        command.append("-N")
        command.append(json.get('max_files_Mbytes'))
    if json.get('upload_ratio') is not None:
        command.append("-q")
        command.append(json.get('upload_ratio'))
    if json.get('download_ratio') is not None:
        command.append("-Q")
        command.append(json.get('download_ratio'))
    if json.get('allow_client_ip') is not None:
        command.append("-r")
        command.append(json.get('allow_client_ip'))
    if json.get('deny_client_ip') is not None:
        command.append("-R")
        command.append(json.get('deny_client_ip'))
    if json.get('allow_local_ip') is not None:
        command.append("-i")
        command.append(json.get('allow_local_ip'))
    if json.get('deny_local_ip') is not None:
        command.append("-I")
        command.append(json.get('deny_local_ip'))
    if json.get('max_concurrent_sessions') is not None:
        command.append("-y")
        command.append(json.get('max_concurrent_sessions'))
    if json.get('max_concurrent_login_attempts') is not None:
        command.append("-C")
        command.append(json.get('max_concurrent_login_attempts'))
    if json.get('memory_reserve_password_hashing') is not None:
        command.append("-M")
        command.append(json.get('memory_reserve_password_hashing'))
    if json.get('allowed_range_day') is not None:
        command.append("-z")
        command.append(json.get('allowed_range_day'))
    # force commit changes
    command.append("-m")
    #     -D/-d < home directory >
    #     [-c < gecos > ]
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


@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Not found'}), 404


@app.errorhandler(405)
def not_allowed(error):
    return jsonify({'error': 'Method not allowed. The method is not allowed for the requested URL.'}), 405


@app.errorhandler(500)
def not_working(error):
    return jsonify({'error': 'Something wrong happen'}), 500


@app.route('/user/del', methods=['POST'])
def delUser():
    if goodApiKey(request.headers):
        if (request.json.get('username') is None):
            return jsonify({"message": "ERROR: missing username"}), 401
        username = request.json.get('username')
        options = jsonToCommandArr(request.json)
        pureCmd = commandPureFtp('userdel', username, options)
        try:
            subprocess.check_output(
                pureCmd, universal_newlines=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print("Your error: " + cleanError(e.output), file=sys.stderr)
            return jsonify({"message": "ERROR: command", "code": e.returncode, "err": cleanError(e.output)}), 400
        return jsonify({"message": "OK: Deleted"}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route('/user/edit', methods=['PUT'])
def editUser():
    if goodApiKey(request.headers):
        if (request.json.get('username') is None):
            return jsonify({"message": "ERROR: missing username/password"}), 401
        username = request.json.get('username')
        options = jsonToCommandArr(request.json)
        pureCmd = commandPureFtp('usermod', username, options)
        try:
            subprocess.check_output(
                pureCmd, universal_newlines=True, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print("Your error: " + cleanError(e.output), file=sys.stderr)
            return jsonify({"message": "ERROR: command", "code": e.returncode, "err": cleanError(e.output)}), 400
        return jsonify({"message": "OK: Edited"}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route('/user/password', methods=['POST'])
def setUserPwd():
    if goodApiKey(request.headers):
        if (request.json.get('username') is None or request.json.get('password') is None):
            return jsonify({"message": "ERROR: missing username/password"}), 401
        password = request.json.get('password')
        username = request.json.get('username')
        pureCmd = commandPureFtp('passwd', username, ['-m'])
        passpass = confirmPass(password)
        try:
            subprocess.check_output(
                pureCmd, universal_newlines=True, input=passpass, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print("Your error: " + cleanError(e.output), file=sys.stderr)
            return jsonify({"message": "ERROR: command", "code": e.returncode, "err": cleanError(cleanError(e.output))}), 400
        return jsonify({"message": "OK: password updated"}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route('/user/info', methods=['GET'])
def getUser():
    if goodApiKey(request.headers):
        if (request.json.get('username') is None):
            return jsonify({"message": "ERROR: missing username"}), 401
        pureCmd = commandPureFtp(
            'show', request.json.get('username'), [])
        try:
            result = subprocess.check_output(
                pureCmd, universal_newlines=True, stderr=subprocess.STDOUT)
            jsonResult = parseInfo(result)
            return jsonify(jsonResult), 200
        except subprocess.CalledProcessError as e:
            print("Your error: " + cleanError(e.output), file=sys.stderr)
            return jsonify({"message": "ERROR: command", "code": e.returncode, "err": cleanError(e.output)}), 400
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


@app.route('/user/add', methods=['POST'])
def addUser():
    if goodApiKey(request.headers):
        if (request.json.get('username') is None or request.json.get('password') is None):
            return jsonify({"message": "ERROR: missing username/password"}), 401
        password = request.json.get('password')
        username = request.json.get('username')
        options = jsonToCommandArr(request.json)
        options.append('-u')
        options.append('ftp')
        pureCmd = commandPureFtp('useradd', username, options)
        passpass = confirmPass(password)
        try:
            subprocess.check_output(
                pureCmd, universal_newlines=True, input=passpass, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            print("Your error: " + cleanError(e.output), file=sys.stderr)
            return jsonify({"message": "ERROR: command", "code": e.returncode, "err": cleanError(e.output)}), 400
        return jsonify({"message": "OK: Created"}), 200
    else:
        return jsonify({"message": "ERROR: Unauthorized"}), 401


if __name__ == '__main__':
    app.run(host='0.0.0.0')
