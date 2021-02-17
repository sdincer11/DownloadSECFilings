import os
os.system('python -m venv venv && venv\\Scripts\\activate.bat && pip install pipreqs && pipreqs "' + os.getcwd() +'" && pip install -r requirements.txt')
import urllib.request as urllib
import pandas as pd
# SEC EDGAR system saves all the URL links for each filing under quarterly folders. These files storing
# the URL information are called "master" files.
# 1) You need to call for the "createMasterFile" function if you want to keep the master file updated.
#   createMasterFile generates a TXT file under the folder provided as the input.
# 2) You need to call for the "downloadSECFilings" function if you want to download specific filings that are filed
#   within dateStart and dateFinish. The "downloadSECFilings" function first creates a folder structure
#   , such as "folderPath/10-K/1000015000/"  where 1000015000 represents the CIK number (firm identifier)
#   and downloads each file to the corresponding path with a file specific name
def createMasterFile(localFolderPath,startYear,endYear):
    # Master file is a txt file that includes all indexing (URL address)  information for filings
    # since the EDGAR system was introduced.
    # The following code updates the master file quarterly, but it is also possible to create the Master file
    # on the daily basis.
    localFolderPath = localFolderPath +'/' if localFolderPath[-1]!='/' else localFolderPath
    outFile = localFolderPath + 'master ' + str(startYear) + '-' + str(endYear) + '.txt'
    baseURL = 'https://www.sec.gov/Archives/edgar/full-index/'
    years = list(range(startYear, endYear + 1))
    for year in years:
        for qtr in [1,2,3,4]:
            year = str(year)
            qtr = 'QTR' + str(qtr)
            indexURL = baseURL + '/'.join([year, qtr, 'master.idx'])
            targetURL = localFolderPath + year + qtr + '.idx'
            try:
                urllib.urlretrieve(indexURL,targetURL)
                try:
                    with open(targetURL,mode='r') as fileReader:
                        lines = [line.replace('\n','') for line in fileReader.readlines()]
                    if os.path.exists(outFile):
                        with open(outFile, mode='a') as fileWriter:
                            for lineNumber, line in enumerate(lines):
                                 if '.txt' in line:
                                    fileWriter.write('|'.join([line,year,qtr.replace('QTR','')]) + '\n')

                    else:
                        with open(outFile, mode='a') as fileWriter:
                            for lineNumber, line in enumerate(lines):
                                if 'CIK|' in line:
                                    fileWriter.write('|'.join([line,'Year','Qtr']) + '\n')
                                elif '.txt' in line:
                                    fileWriter.write('|'.join([line,year,qtr.replace('QTR','')]) + '\n')
                except Exception as e:
                    with open(localFolderPath + 'master processing errors.txt', mode='a') as file:
                        file.write('Issue occurred while processing ' + year + qtr + '.idx' + '\n')
                    print(e)
                    pass
                try:
                # Remove the downloaded file from the hard-drive after processing it
                    if os.path.exists(targetURL):
                        os.remove(targetURL)
                except:
                    pass
            except:
                with open(localFolderPath + 'master downloading errors.txt',mode='a') as file:
                    file.write('Issue occurred while downloading ' + year + qtr +'.idx' + '\n')
                pass
def getLocalFilePath(delimiter,*args):
    try:
        name = delimiter.join(args)
    except:
        name = 'N/A'
    return name
def downloadSECFiling(url,downloadPath,logFilePath):
    try:
        urllib.urlretrieve(url, downloadPath)
    except Exception as e:
        print(e)
        with open(logFilePath, mode='a') as file:
            file.write(url+'\n')


def downloadSECFilings(localFolderPath, formTypesList, dateStart, dateFinish, edgarMasterFilePath=None):
    localFolderPath = localFolderPath[:,-1] if localFolderPath[-1] == '/' else localFolderPath
    baseURL = 'https://www.sec.gov/Archives/'
    if os.path.isdir(localFolderPath):
        if dateStart < dateFinish:
            if os.path.exists(edgarMasterFilePath):
                dF = pd.read_csv(edgarMasterFilePath,delimiter='|')
                dF = dF[ dF['Form Type'].str.contains('|'.join(formTypesList))]
                dF['Form Type'] = dF['Form Type'].str.replace('/',' ')
                dF['Date Filed Pandas Date'] = (pd.to_datetime(dF['Date Filed'],format='%Y-%m-%d',errors='ignore')).apply(lambda x: x.year*10000 + x.month*100 + x.day)
                dF = dF[ dF['Date Filed Pandas Date'].between(dateStart,dateFinish)]
                if len(dF)>0:
                    dF['CIK'] = dF['CIK'].apply(lambda x: str(x).ljust(10, '0'))
                    dF['URL'] = dF['Filename'].apply(lambda x: baseURL + x)
                    dF['Year-Qtr'] = (dF['Year']*100 + dF['Qtr'] ).astype(str)
                    dF['AccessionID'] = dF['Filename'].apply(lambda x: x.split('/')[-1] if len(x.split('/'))>0 else 'N/A')
                    folders = dF[['Year-Qtr','Form Type','CIK']].drop_duplicates().values
                    dF['Local Downloadpath'] = dF.apply(lambda x: getLocalFilePath('/',localFolderPath,x['Form Type'],x['CIK'],x['Year-Qtr']), axis=1)
                    dF['Local Filename'] = dF.apply(lambda x: getLocalFilePath('_', x['CIK'], x['Form Type'], x['Date Filed'], x['AccessionID']), axis=1)
                    dF['Local Filepath'] = dF.apply(lambda x: getLocalFilePath('/', x['Local Downloadpath'], x['Local Filename']), axis=1)
                    for folder in folders:
                        qtr_folder = folder[0]
                        form_folder = folder[1]
                        cik_folder = str(folder[2])
                        if not os.path.exists('/'.join([localFolderPath, form_folder, cik_folder, qtr_folder])):
                            os.makedirs('/'.join([localFolderPath , form_folder, cik_folder, qtr_folder]))
                    dF.iloc.apply(lambda x: downloadSECFiling(x['URL'], x['Local Filepath'],localFolderPath + '/filing dowload errors.txt'),axis=1)
            else:
                print('You did not specify a valid value for an existing file located at "edgarMasterFilePath". We are downloading the master file first')
                createMasterFile(localFolderPath, int(dateStart/100), int(dateFinish/100))
        else:
            print('Please make sure that dateFinish exceeds dateStart in your function call.')
    else:
        print('Please make sure that you specified a valid folder path to which filings will be downloaded.')
