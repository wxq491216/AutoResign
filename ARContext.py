import os
from biplist import *
import xml.dom.minidom
import ResignFileManager
import ResignCore
import re

class ARContext:

    #constructor
    def __init__(self, path, configuration):
        self.configuration = configuration
        self.workspace = path
        self.originalIpa = os.path.abspath(os.path.join(os.path.curdir, 'Resource/BookReader.ipa'))
        self.configFile = 'config.xml'
        self.book = 'Book/book.txt'
        self.ipaInfo = []
        self.output = 'out/'
        self.appPath = 'out/Payload/damoyao.app/'
        self.certificates = ResignCore.exploreCertificates()
        self.provision = 'mobileprovision/{}.mobileprovision'

    def readConfig(self):
        DOMTree = xml.dom.minidom.parse(self.configFile)
        collection = DOMTree.documentElement
        ipas = collection.getElementsByTagName('app')
        for ipa in ipas:
            folderName = ipa.getAttribute('folder')
            bundleName = ipa.getElementsByTagName('bundleName')[0].childNodes[0].data
            bundleId = ipa.getElementsByTagName('bundleId')[0].childNodes[0].data
            cert = ipa.getElementsByTagName('cert')[0].childNodes[0].data
            dataeyeId = ipa.getElementsByTagName('dataeye')[0].childNodes[0].data
            dic = {'folder':folderName, 'bundleName':bundleName, 'bundleId':bundleId, 'cert':cert, 'dataeye':dataeyeId}
            self.ipaInfo.append(dic)

    def unzipIpa(self):
        ResignCore.unzip(self.originalIpa, self.output)

    def generalEntitlements(self, identify, provisionPath):
        entitlementPath = os.path.join(self.workspace, 'Entitlements.plist')
        ResignCore.generalEntitlements(provisionPath, identify, entitlementPath)

    def removeCodesignFile(self):
        codesignFolder = os.path.join(self.appPath, '_CodeSignature')
        ResignFileManager.removeDir(codesignFolder)

    def updateProvisionFile(self, provisionPath):
        destPath = os.path.join(self.appPath, 'embedded.mobileprovision')
        ResignFileManager.removeFile(destPath)
        ResignFileManager.copyFile(provisionPath, destPath)

    def modifyIpaInfo(self, info):
        bundleName = info['bundleName']
        bundleId = info['bundleId']
        dataeyeId = info['dataeye']
        infoPlist = os.path.join(self.appPath, 'Info.plist')
        plist = readPlist(infoPlist)
        plist['CFBundleIdentifier'] = bundleId
        plist['CFBundleDisplayName'] = bundleName
        plist['dataeye'] = dataeyeId
        writePlist(plist, infoPlist)


    def modifyResource(self, resourceDir):
        iconDir = os.path.join(self.workspace, resourceDir, 'Icon')
        launchImageDir = os.path.join(self.workspace, resourceDir, 'LaunchImage')
        ResignFileManager.copyDir(iconDir, self.appPath)
        ResignFileManager.copyDir(launchImageDir, self.appPath)

        sourceTxtFile = os.path.join(self.workspace, resourceDir, 'book.txt')
        targetTxtFile = os.path.join(self.appPath, 'book.txt')
        ResignFileManager.copyFile(sourceTxtFile, targetTxtFile)

    def codesign(self, cert, bundleId):
        entitlementPath = os.path.join(self.workspace, 'Entitlements.plist')
        currCert = ''
        type = ''
        if self.configuration == 'product' or self.configuration == 'adhoc':
            type = 'iPhone Distribution'
        elif self.configuration == 'developer':
            type = 'iPhone Developer'
        else:
            return
        for item in self.certificates:
            if cert in item and type in item:
                currCert = item
                break
        if len(currCert) > 0:
            ResignCore.codesign(self.appPath, bundleId, currCert, entitlementPath)

    def packageIpa(self, ipaName):
        name = ipaName + '.ipa'
        outPath = os.path.join(self.workspace, 'ipa', name)
        os.chdir(self.output)
        ResignCore.zip('./Payload', outPath)
        os.chdir(self.workspace)

    def resign(self):
        for item in self.ipaInfo:
            folder = item['folder']
            if os.path.exists(folder):
                teamIdentify = item['cert']
                bundleId = item['bundleId']
                applicationIdentify = teamIdentify + '.' + bundleId
                provisionPath = self.provision.format(teamIdentify)
                print applicationIdentify
                self.removeCodesignFile()
                self.generalEntitlements(applicationIdentify, provisionPath)
                self.updateProvisionFile(provisionPath)
                self.modifyIpaInfo(item)
                self.modifyResource(folder)
                self.codesign(teamIdentify, bundleId)
                self.packageIpa(folder)


    def validResignDir(self):
        valid = ResignFileManager.hasFile(self.workspace, self.configFile)
        return valid

    def cleanOutputDir(self):
        ResignFileManager.removeDir(self.output)

    def clearWorkSpace(self):
        ResignFileManager.removeDir(self.output)
        ipaDir = os.path.join(self.workspace, 'ipa')
        ResignFileManager.removeDir(ipaDir)
        os.makedirs(self.output)
        os.makedirs(ipaDir)


    def startWork(self):
        os.chdir(self.workspace)
        self.clearWorkSpace()
        self.readConfig()
        self.unzipIpa()
        self.resign()


