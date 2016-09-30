import os
import json
from plistlib import *
import re

def generalEntitlements(profilePath, applicationIdentify, entitlementPath):
    generalCmd = "security cms -D -i " + profilePath
    out = execCmd(generalCmd)
    plist = readPlistFromString(out)
    entitlementData = plist['Entitlements']
    entitlementData['application-identifier'] = applicationIdentify
    del entitlementData['com.apple.developer.team-identifier']
    del entitlementData['keychain-access-groups']
    writePlist(entitlementData, entitlementPath)


def exploreCertificates():
    certCmd = "security find-identity -v -p codesigning"
    out = execCmd(certCmd)
    list = out.split('\n')
    certs = []
    for item in list:
        try:
            temp = re.findall("(\".+?\")", item)[0]
            certs.append(temp)
        except Exception, e:
            print e
    return certs

def zip(zipPath, outPath):
    path, file = os.path.split(outPath)
    if not os.path.exists(path):
        os.makedirs(path)
    zipCmd = "zip -qry " + outPath + " " + zipPath
    execCmd(zipCmd)

def unzip(zipPath, outPath):
    unzipCmd = "unzip -q " + zipPath + " -d " + outPath
    execCmd(unzipCmd)

def codesign(path, bundleId, certificate, entitlement):
    arguments = ""
    last = os.path.basename(os.path.normpath(path))
    if last.endswith("app"):
        #arguments = "-f -s " + certificate + " -i " + bundleId + " --entitlements " + entitlement + " " + path
        arguments = "-f -s " + certificate + " " + path + " --entitlements=" + entitlement
    elif last.endswith("framework"):
        arguments = "-f -s " + certificate + " " + path
    codesignCmd = "codesign " + arguments
    out = execCmd(codesignCmd)
    print out

def verifyCodesign(path):
    verifyCmd = "codesign -v " + path
    result = execCmd(verifyCmd)
    if len(result) == 0:
        return True
    else:
        return False

def execCmd(cmd):
    print cmd
    r = os.popen(cmd)
    return r.read()