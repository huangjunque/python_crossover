#!/usr/bin/python
#!coding=utf=8

import json
import urllib2
import time
import commands
import sys
import os

def getRemoteInfo(url):
    try:
        request = urllib2.Request(url)
        r = urllib2.urlopen(request,timeout=3)
        resp = r.read()
    except:
        return False
    return resp

def exec_shell(cmd,resp=False):
    (status, output) = commands.getstatusoutput(cmd)
    if not resp:
        return status
    else:
        return output

def report(status,project,msg):
    instance_hostname = exec_shell("hostname",True)
    report_msg = {"instanceName":instance_hostname,"status":status,"appName":project,"msg":msg}
    report_body = json.dumps(report_msg)
    url = "http://xx.xx.xx.xx:xx/app/report"
    req = urllib2.Request(url=url,data=report_body)
    res = urllib2.urlopen(req)

class service(object):
    def __init__(self,project):
        self.project = project

        getVersionUrl = "http://10.100.4.85/autosc/%s/version"%appName
        onlineVersion = getRemoteInfo(getVersionUrl).split('\n')[0]

        getAppInfoUrl = "http://10.100.4.85/autosc/%s/appInfo"%project
        appInfoResp = getRemoteInfo(getAppInfoUrl)

        if not onlineVersion or not appInfoResp:
            report("Failed",self.project,"getRemote Info Error!")
            sys.exit()

        appInfo = json.loads(appInfoResp)

        self.version = onlineVersion
        self.checkFile = appInfo["checkFile"]
        self.appPort = appInfo["appPort"]
        self.checkUrl = appInfo["checkUrl"]
        self.coDeploy = appInfo["coDeploy"]

    def offlice(self):
        if os.path.exists(self.checkFile):
            offlineCmd = "mv %s %s.bak"%(self.checkFile,self.checkFile)
            exec_shell(offlineCmd)

    def update(self):
        unarchiveDir = self.coDeploy["unarchiveDir"]
        workDir = self.coDeploy["workDir"]
        compressType = self.coDeploy["compressType"]

        getCode = 1
        depCode = 1

        if self.project in ["abc","bba","ddc","ffg","tinker"]
            getCode = exec_shell("cd /tmp/ && wget http://10.100.4.85/tinker/%s"%(self.version))
        else:
            getCode = exec_shell("cd /tmp/ && wget http://10.100.4.85/%s/%s"%(self.project,self.version))
        if  getCode:
            return "getCode error"

        if compressType == "zip": 
            exec_shell("mkdir /tmp/%s"%self.project)
            exec_shell("unzip /tmp/%s -d /tmp/%s/"%(self.version,self.project)
            if os.path.exists(workDir):
                exec_shell("mv %s %s.bak"%(workDir,workDir))
            depCode = exec_shell("mv /tmp/%s/%s %s"%(self.project,unarchiveDir,workDir))
        elif compressType == "tar":
            depCode = exec_shell("tar -xf /tmp/%s -C %s"%(self.version,self.coDeploy["workDir"]))
        if depCode:
            return "depCode error" 
        exec_shell("supervisorctl restart %s:*"%self.project)
        return True

    def check(self):
        process_status = 0 
        for port in self.appPort:
            url = "http://127.0.0.1:%s%s"%(port,self.checkUrl)
            req = urllib2.Request(url)
            try:
                r = urllib2.urlopen(req)
            except:
                pass
            else:
                process_status += 1
        if process_status == len(self.appPort):
            return True
        else:
            return False
    
    def online(self):
        onlineCmd = "echo 'ok' > %s"%self.checkFile
        exec_shell("/etc/init.d/nginx restart")
        exec_shell(onlineCmd)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        appName = sys.argv[1]
    else:
        report("Failed",appName,"appName error")
        sys.exit()

    service = service(appName)

    service.offline()
    time.sleep(20)
    updateSt = service.update()
    if not updateSt == True:
        report("Failed",appName,"%s == %s"%(service.version, updateSt))
        sys.exit()
    time.sleep(30)
    if not service.check():
        checkStatus = service.check()
        if not checkStatus:
            report("Failed",appName,"urlCheck Error!")
            sys.exit()
    service.online()
    report("Successed",appName,service.version)
