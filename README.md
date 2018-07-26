# djangoSite
django api for COSFIRE

**First install COSFIRE:**
```sh
cd djangoSite/COSFIRE-develop/
python3 setup.py install --user
```
**install django:**
```sh
pip3 install django
```

**run django with:**
```sh
cd djangoSite/mysite/
python3 manage.py runserver
```

### git cmd Reminders ###

**Obtaining files:**   
git clone -b develop https://github.com/XX.git 

**update local files:**   
git pull origin develop

**Creating a new branch:**   
git checkout -b newBranch develop

**pushing to github:**   
git status  
git add folderName/* (or: git add -A)  
git commit -m "I just did some change"   
git push origin branchName 

**remove a file:** 
git rm fileName  
