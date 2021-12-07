- Setup
```
cd proj_folder
```

- Run virtual environment
```
. venv/bin/activate
```

- Install Flask 
```
pip install Flask
```

- Setup Environment variable
```
source .env
```

- Run Server
```
python server.py
```

- Command to run ln2sql inside server.py
```
import os 

command = "python3 -m ln2sql.ln2sql.main -d database_store/olympics.sql -l lang_store/english.csv -j output.json -i 'what is the region with GDP is 2000'"
os.system(command)
```