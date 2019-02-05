#!/usr/bin/env python3
# coding: utf-8
# Copyright 2016 Abram Hindle, https://github.com/tywtyw2002, and https://github.com/treedust
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Do not use urllib's HTTP GET and POST mechanisms.
# Write your own HTTP GET and POST
# The point is to understand what you have to send and get experience with it

import sys
import socket
import time
import re
# you may use urllib to encode data appropriately
import urllib.parse

def help():
    print("httpclient.py [GET/POST] [URL]\n")

class HTTPResponse(object):
    def __init__(self, code=200, body=""):
        self.code = code
        self.body = body
        self.socket = None
class HTTPClient(object):
    #def get_host_port(self,url):

    def connect(self, host, port):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((host, port))
        return None

    def general_parser(self, data):
        parseData = data.replace("/r","")
        parseData = data.split("\n")
        return parseData

    def get_code(self, data):
        statusCode = int(data[0].split(" ")[1]) #returns status code of response.
        return statusCode

    def get_headers(self,data, urlPath):
        htmlTagIndex = data.find("\r\n\r\n")
        if(htmlTagIndex == -1):
            htmlTagIndex = 0
        header = data[:htmlTagIndex]
        header += "\nLocation: "+urlPath
        return header

    def get_body(self, data):
        body = ""
        htmlTagIndex = data.find("\r\n\r\n")
        body = data[htmlTagIndex:]
        return body
    
    def sendall(self, data):
        self.socket.sendall(data.encode('utf-8'))
        
    def close(self):
        self.socket.close()

    # read everything from the socket
    def recvall(self):
        buffer = bytearray()
        done = False
        while not done:
            part = self.socket.recv(1024)
            if (part):
                buffer.extend(part)
            else:
                done = not part
        decodedBody = buffer.decode('utf-8')
        return decodedBody

    def GET(self, url, args=None):
        domainName, urlPath, urlQuery, port = self.parseURL(url)
        self.connect(domainName, port)
        header = "GET "+urlPath+" HTTP/1.0\r\nHost: "+domainName+"\r\nAccept: */*\r\n\r\n"
        self.sendall(header)
        #print("###GET DATA SENT###\nDomain: {}\nPath: {}\nQuery: {}\nPort: {}\nHeader: {}\n".format(domainName, urlPath, urlQuery, port, header))
        print("###GET DATA SENT###\n"+header)
        returnData = self.recvall()
        parseData = self.general_parser(returnData)
        statusCode = self.get_code(parseData)
        htmlBody = self.get_body(returnData)
        htmlHeader = self.get_headers(returnData, urlPath)
        fullHtml = htmlHeader + htmlBody
        print("###GET DATA RECIEVED###\n"+returnData)
        self.close()
        return HTTPResponse(statusCode, fullHtml)

    def parseURL(self, url):
        domain = url
        path = ""
        query = ""
        slashIndex = url.find("//")
        if(slashIndex != -1):
            domain = url[slashIndex+2:]
        pathStartIndex = domain.find("/")
        if(pathStartIndex != -1):
            path = domain[pathStartIndex:]
        if(path == ""):
            path = "/"
        queryIndex = path.find("?")
        if(queryIndex != -1):
            query = path[queryIndex:]
            path = path[:queryIndex]
        if(pathStartIndex != -1):
            domain = domain[:pathStartIndex]
        try:
            port = int(domain.split(":")[1])
            domain = domain.split(":")[0]
        except:
            port = 80
        return domain, path, query, port

    def parsePostArgs(self, args):
        postBody = ""
        if(args == None):
            postBody = ""
        else:
            for key in args.keys():
                postBody += "{}={}&".format(key, args[key])
        return postBody, len(postBody)
        
    def POST(self, url, args=None):
        #start_time = time.time()
        postBody, postBodyLen = self.parsePostArgs(args)
        domainName, urlPath, urlQuery, port = self.parseURL(url)
        self.connect(domainName, port)
        fakeUserAgent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36'
        header = "POST {} HTTP/1.0\nHost: {}\nConnection: keep-alive\nAccept: */*\nOrigin: {}\nUser-Agent: {}\nAccept-Encoding: gzip, deflate\nAccept-Language: en-US;q=0.9\nContent-Type: application/x-www-form-urlencoded; charset=UTF-8\nContent-Length: {}\r\n\r\n{}".format(urlPath+urlQuery,domainName,url,fakeUserAgent,postBodyLen,postBody)
        self.sendall(header)
        returnData = self.recvall()
        print("###POST DATA SENT###\n"+header)
        #print("#####SENT DATA#####: \n"+header)
        parseData = self.general_parser(returnData)
        statusCode = self.get_code(parseData)
        htmlBody = self.get_body(returnData)
        htmlHeader = self.get_headers(returnData, urlPath)
        print("###POST DATA RECIEVED###: \n"+returnData)
        fullHtml = htmlBody
        self.close()
        return HTTPResponse(statusCode, fullHtml)

    def command(self, url, command="GET", args=None):
        if (command == "POST"):
            return self.POST( url, args )
        else:
            return self.GET( url, args )
    
if __name__ == "__main__":
    client = HTTPClient()
    command = "GET"
    if (len(sys.argv) <= 1):
        help()
        sys.exit(1)
    elif (len(sys.argv) == 3):
        print(client.command( sys.argv[2], sys.argv[1] ))
    else:
        print(client.command( sys.argv[1] ))
