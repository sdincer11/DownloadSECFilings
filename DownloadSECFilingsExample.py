from DownloadSECFilings import *
# SEC EDGAR system saves all the URL links for each filing under quarterly folders. These files storing
# the URL information are called "master" files.
# 1) You need to call for the "createMasterFile" function if you want to keep the master file updated.
#   createMasterFile generates a TXT file under the folder provided as the input.
# 2) You need to call for the "downloadSECFilings" function if you want to download specific filings that are filed
#   within dateStart and dateFinish. The "downloadSECFilings" function first creates a folder structure
#   , such as "folderPath/10-K/1000015000/"  where 1000015000 represents the CIK number (firm identifier)
#   and downloads each file to the corresponding path with a file specific name
# YOU CAN SEE A SAMPLE CALL BELOW to download all 10-Ks reported between January 1st 2000 and June 30, 2001.
# WARNING : YOU NEED TO MAKE SURE THAT YOU HAVE ENOUGH HARD DRIVE SPACE BEFORE YOU DOWNLOAD THE FILINGS.
createMasterFile('C:/path to your folder where you want to download the filings to', 2000, 2001)
downloadSECFilings('C:/path to your folder where you want to download the filings to',
                   formTypesList=['10-K'],
                   dateStart=20000101,
                   dateFinish=20010630,
                   )
