
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


ACCESS_KEY: Access key in your Minio Services Account.

SECRET_KEY: Secret key in your Minio Services Account.

BUCKET_NAME: Your Bucket name.

OBJECT_NAME: The Object name in your Bucket (This file that only enter file name, do not enter file format).


## Print file from Minio

### Example:

Print file from:
   Access key: dpZ
   Secret key: dpZcrawl
   Bucket name: abc
   Object name: hihi.txt

### Print .txt file

```

import dpgenZ

a = dpgenZ.Storage(ACCESS_KEY, SECRET_KEY)

a.readtext(BUCKET_NAME, OBJECT_NAME)

a


# Example:

import dpgenZ

a = dpgenZ.Storage('dpZ', 'dpZcrawl')

a.readtext('abc', 'hihi')

a

```

### Print .csv file

```

import dpgenZ

a = dpgenZ.Storage(ACCESS_KEY, SECRET_KEY)

a.readcsv(BUCKET_NAME, OBJECT_NAME)

a


# Example:

import dpgenZ

a = dpgenZ.Storage('dpZ', 'dpZcrawl')

a.readcsv('abc', 'hihi')

a

```

### Print .xlsx file

```

import dpgenZ

a = dpgenZ.Storage(ACCESS_KEY, SECRET_KEY)

a.readexcel(BUCKET_NAME, OBJECT_NAME)

a


# Example:

import dpgenZ

a = dpgenZ.Storage('dpZ', 'dpZcrawl')

a.readexcel('abc', 'hihi')

a

```

### Print .parquet file

```

import dpgenZ

a = dpgenZ.Storage(ACCESS_KEY, SECRET_KEY)

a.readparquet(BUCKET_NAME, OBJECT_NAME)

a


# Example:

import dpgenZ

a = dpgenZ.Storage('dpZ', 'dpZcrawl')

a.readparquet('abc', 'hihi')

a

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