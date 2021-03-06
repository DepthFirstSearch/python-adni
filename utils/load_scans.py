import xml.etree.ElementTree as ET
import glob
import os
import csv
import inspect


class Scan:
    def __init__(self, subject, imageID, seriesID, gender, age, group, FAQ, MMSE, CDR, tracer, manufacturer, path):
        self.subject = subject
        self.imageID = imageID
        self.seriesID =seriesID
        self.gender = gender
        self.age = age
        self.group = group
        self.FAQ = FAQ
        self.MMSE = MMSE
        self.CDR = CDR
        self.tracer = tracer
        self.manufacturer = manufacturer
        self.path = path


def _build_path(base, subject, preprocessing, date, imageID, ext):
    preprocessing = preprocessing.replace(' ', '_')
    date = date.replace(' ', '_')
    date = date.replace(':', '_')
    path = os.path.join(base, subject, preprocessing, date, imageID, '*.' + ext)
    path = glob.glob(path)
    assert len(path) == 1, \
        "There are %d scans in directory: %s" % (len(path), path)
    return path[0]


def _parse_scan_info(base, filename, ext):
    xml = ET.parse(filename)
    root = xml.getroot()
    nodeSubject = root.find('project').find('subject')
    nodeVisit = nodeSubject.find('visit')
    nodeStudy = nodeSubject.find('study')
    nodeSeries = nodeStudy.find('series')
    nodeSeriesLevelMeta = nodeSeries.find('seriesLevelMeta')
    nodeDerivedProduct = nodeSeriesLevelMeta.find('derivedProduct')
    nodeProtocolTerm = nodeSeriesLevelMeta.find('relatedImageDetail').find('originalRelatedImage').find('protocolTerm')
    subject = nodeSubject.find('subjectIdentifier').text
    assert subject is not None, \
        "Could not find subject in: %s" % filename
    gender = nodeSubject.find('subjectSex').text
    assert gender is not None, \
        "Could not find gender in: %s" % filename
    age = nodeStudy.find('subjectAge').text
    assert age is not None, \
        "Could not find age in: %s" % filename
    age = float(age)
    for subjectInfo in nodeSubject.findall('subjectInfo'):
        if subjectInfo.attrib['item'] == 'DX Group':
            group = subjectInfo.text
            break
    assert group is not None, \
        "Could not find group in: %s" % filename
    CDR = -1
    for assessment in nodeVisit.findall('assessment'):
        if assessment.attrib['name'] == 'CDR':
            CDR = float(assessment.find('component').find('assessmentScore').text)
            break
    MMSE = -1
    for assessment in nodeVisit.findall('assessment'):
        if assessment.attrib['name'] == 'MMSE':
            MMSE = float(assessment.find('component').find('assessmentScore').text)
            break
    FAQ = -1
    for assessment in nodeVisit.findall('assessment'):
        if assessment.attrib['name'] == 'Functional Assessment Questionnaire':
            FAQ = float(assessment.find('component').find('assessmentScore').text)
            break
    assert group is not None, \
        "Could not find group in: %s" % filename
    manufacturer = None
    tracer = None
    for protocol in nodeProtocolTerm.findall('protocol'):
        if protocol.attrib['term'] == 'Manufacturer':
            manufacturer = protocol.text
        if protocol.attrib['term'] == 'Radiopharmaceutical':
            tracer = protocol.text
        if manufacturer is not None and tracer is not None:
            break
    assert manufacturer is not None, \
        "Could not find manufacturer in: %s" % filename
    assert tracer is not None, \
        "Could not find tracer in: %s" % filename
    imageID = nodeDerivedProduct.find('imageUID').text
    assert imageID is not None, \
        "Could not find image ID in: %s" % filename
    imageID = 'I' + imageID
    preprocessing = nodeDerivedProduct.find('processedDataLabel').text
    date = nodeSeries.find('dateAcquired').text
    path = _build_path(base, subject, preprocessing, date, imageID, ext)
    seriesID = nodeSeries.find('seriesIdentifier').text
    return Scan(subject, imageID, seriesID, gender, age, group, FAQ, MMSE, CDR, tracer, manufacturer, path)


def conversions(scans):
    missing = {}
    missing['I80978'] = 3.0
    missing['I118431'] = 0.0
    missing['I290403'] = 1.0
    missing['I323920'] = 0.0
    missing['I403815'] = 0.0
    missing['I349178'] = 25.0
    missing['I139900'] = 12.0
    missing['I135500'] = 5.0
    missing['I43049'] = 8.0
    path = os.path.join(os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe()))), 'conversions')
    conv = {}
    with open(path, 'rb') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            if row[1] == 'EMCI' and row[2] == 'Normal':
                conv[row[0]] = 'discard'
            elif row[1] == 'MCI' and row[2] == 'Normal':
                conv[row[0]] = 'discard'
            elif row[1] == 'LMCI' and row[2] == 'Normal':
                conv[row[0]] = 'discard'
            elif row[1] == 'AD' and row[2] == 'Normal':
                conv[row[0]] = 'discard'
            elif row[1] == 'Normal' and row[2] == 'AD':
                conv[row[0]] = 'discard'
            elif row[1] == 'EMCI' and row[2] == 'AD':
                conv[row[0]] = 'discard'
            else:
                conv[row[0]] = row[2]
    for scan in scans:
        if scan.imageID in conv:
            scan.group = conv[scan.imageID]
        if scan.imageID in missing:
            scan.FAQ = missing[scan.imageID]
    return scans


def load_scans(directory, ext='npy'):
    files = glob.glob(os.path.join(directory, '*.xml'))
    scans = []
    for f in files:
        scans.append(_parse_scan_info(directory, f, ext))
    scans = conversions(scans)
    return scans

