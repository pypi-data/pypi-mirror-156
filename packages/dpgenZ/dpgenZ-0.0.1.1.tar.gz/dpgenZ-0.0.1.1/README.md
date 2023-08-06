
# dpgenZ: Print your buckets and .csv files from Minio
## Powered by FPT Infomation System

# How to install?
```
pip install dpgenZ
```
## or

Windows
```
py -m pip install dpgenZ
```
Linux/Mac OS
```
python3 -m pip install dpgenZ
```


# How to use dpgenZ?

## You can use to one of codes below here:

## Print list buckets in Minio

ACCESS_KEY: Access key in your Minio Services Account.

SECRET_KEY: Secret key in your Minio Services Account.

BUCKET_NAME: Your Bucket name.

OBJECT_NAME: The Object name in your Bucket (This file that only enter file name, do not enter file format).

```
#1

import dpgenZstorage

dpgenZstorage.read_list(ACCESS_KEY, PRIVATE_KEY)



#2

from dpgenZstorage import read_list

read_list(ACCESS_KEY, PRIVATE_KEY)

```


## Print file from Minio

### Print .txt file

```
#1

import dpgenZstorage

dpgenZstorage.readtext(ACCESS_KEY, SECRET_KEY, BUCKET_NAME, OBJECT_NAME)



#2

from dpgenZstorage import readtext

readtext(ACCESS_KEY, SECRET_KEY, BUCKET_NAME, OBJECT_NAME)



# Example:
# Print file from:
#   Access key: dpZ
#   Secret key: dpZcrawl
#   Bucket name: abc
#   Object name: hihi.txt

import dpgenZstorage

dpgenZstorage.readtext('dpZ', 'dpZcrawl', 'abc', 'hihi')

```

### Print .csv file

```
#1

import dpgenZstorage

dpgenZstorage.readcsv(ACCESS_KEY, SECRET_KEY, BUCKET_NAME, OBJECT_NAME)



#2

from dpgenZstorage import readcsv

readcsv(ACCESS_KEY, SECRET_KEY, BUCKET_NAME, OBJECT_NAME)



# Example:
# Print file from:
#   Access key: dpZ
#   Secret key: dpZcrawl
#   Bucket name: abc
#   Object name: hihi.csv

import dpgenZstorage

dpgenZstorage.readcsv('dpZ', 'dpZcrawl', 'abc', 'hihi')

```

### Print .xlsx file

```
#1

import dpgenZstorage

dpgenZstorage.readexcel(ACCESS_KEY, SECRET_KEY, BUCKET_NAME, OBJECT_NAME)



#2

from dpgenZstorage import readexcel

readexcel(ACCESS_KEY, SECRET_KEY, BUCKET_NAME, OBJECT_NAME)



# Example:
# Print file from:
#   Access key: dpZ
#   Secret key: dpZcrawl
#   Bucket name: abc
#   Object name: hihi.xlsx

import dpgenZstorage

dpgenZstorage.readexcel('dpZ', 'dpZcrawl', 'abc', 'hihi')

```

### Print .parquet file

```
#1
import dpgenZstorage

dpgenZstorage.readparquet(ACCESS_KEY, SECRET_KEY, BUCKET_NAME, OBJECT_NAME)



#2
from dpgenZstorage import readparquet

readparquet(ACCESS_KEY, SECRET_KEY, BUCKET_NAME, OBJECT_NAME)



# Example:
# Print file from:
#   Access key: dpZ
#   Secret key: dpZcrawl
#   Bucket name: abc
#   Object name: hihi.parquet

import dpgenZstorage

dpgenZstorage.readparquet('dpZ', 'dpZcrawl', 'abc', 'hihi')

```


## Write file from Minio

ACCESS_KEY: Access key in your Services Account.

SECRET_KEY: Secret key in your Services Account.

BUCKET_NAME_IN: Your Bucket name (INPUT).

OBJECT_NAME_IN: The Object name in your Bucket (INPUT) (This file that only enter file name, do not enter file format).

BUCKET_NAME_OUT: Your Bucket name (OUTPUT).

OBJECT_NAME_OUT: The Object name in your Bucket (OUTPUT) (.csv file) (This file that only enter file name, do not enter file format).

### Write .txt file

```

#1

import dpgenZstorage

dpgenZstorage.writetext(ACCESS_KEY,PRIVATE_KEY,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT)



#2

from dpgenZstorage import writetext

writetext(ACCESS_KEY,PRIVATE_KEY,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT)



# Example:
# Write file from:
#   Access key: dpZ
#   Secret key: dpZcrawl
#   Bucket name: abc
#   Object name: hihi.txt

# Write to:
#   Bucket name: xyz
#   Object name: huhu.csv

import dpgenZstorage

dpgenZstorage.writetext('dpZ', 'dpZcrawl', 'abc', 'hihi', 'xyz', 'huhu')

```

### Write .csv file

```
#1
import dpgenZstorage

dpgenZstorage.writecsv(ACCESS_KEY,PRIVATE_KEY,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT)



#2
from dpgenZstorage import writecsv

writecsv(ACCESS_KEY,PRIVATE_KEY,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT)



# Example:
# Write file from:
#   Access key: dpZ
#   Secret key: dpZcrawl
#   Bucket name: abc
#   Object name: hihi.csv

# Write to:
#   Bucket name: xyz
#   Object name: huhu.csv

import dpgenZstorage

dpgenZstorage.writecsv('dpZ', 'dpZcrawl', 'abc', 'hihi', 'xyz', 'huhu')

```

### Write .xlsx file

```
#1
import dpgenZstorage

dpgenZstorage.writeexcel(ACCESS_KEY,PRIVATE_KEY,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT)



#2
from dpgenZstorage import writeexcel

writeexcel(ACCESS_KEY,PRIVATE_KEY,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT)



# Example:
# Write file from:
#   Access key: dpZ
#   Secret key: dpZcrawl
#   Bucket name: abc
#   Object name: hihi.xlsx

# Write to:
#   Bucket name: xyz
#   Object name: huhu.csv

import dpgenZstorage

dpgenZstorage.writeexcel('dpZ', 'dpZcrawl', 'abc', 'hihi', 'xyz', 'huhu')

```

### Write .parquet file

```
#1
import dpgenZstorage

dpgenZstorage.writeparquet(ACCESS_KEY,PRIVATE_KEY,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT)



#2
from dpgenZstorage import writeparquet

writeparquet(ACCESS_KEY,PRIVATE_KEY,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT)



# Example:
# Write file from:
#   Access key: dpZ
#   Secret key: dpZcrawl
#   Bucket name: abc
#   Object name: hihi.parquet

# Write to:
#   Bucket name: xyz
#   Object name: huhu.csv

import dpgenZstorage

dpgenZstorage.writeparquet('dpZ', 'dpZcrawl', 'abc', 'hihi', 'xyz', 'huhu')

```