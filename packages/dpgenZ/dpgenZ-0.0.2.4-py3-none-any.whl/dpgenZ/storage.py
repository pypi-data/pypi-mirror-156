from importlib.resources import read_text
from minio import Minio
import pandas as pd
from io import BytesIO
import os

class Storage:
    
    def __init__(self,ACCESS_KEY, PRIVATE_KEY):
        self.access_key=ACCESS_KEY,
        self.private_key=PRIVATE_KEY
        self.client=Minio(
            "apilakedpa.apps.xplat.fis.com.vn",
            access_key=ACCESS_KEY,
            secret_key=PRIVATE_KEY,
            secure = True            
        )


    def readcsv(self,BUCKET_NAME,OBJECT_NAME,delimiter=','):

        obj = self.client.get_object(BUCKET_NAME,OBJECT_NAME+'.csv')

        df = pd.read_csv(obj, delimiter=delimiter)

        return df


    def writecsv(self,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT,delimiter=','):

        obj = self.client.get_object(BUCKET_NAME_IN, OBJECT_NAME_IN+'.csv')

        df = pd.read_csv(obj, delimiter=delimiter)

        csv = df.to_csv().encode('utf-8')

        self.client.put_object(
        BUCKET_NAME_OUT,
        OBJECT_NAME_OUT+'.csv',
        data=BytesIO(csv),
        length=len(csv),
        content_type='example.csv'
    )

    def readtext(self,BUCKET_NAME,OBJECT_NAME):

        obj = self.client.get_object(BUCKET_NAME,OBJECT_NAME+'.txt')

        de = pd.read_table(obj)

        return de


    def writetext(self,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT):


        obj = self.get_object(BUCKET_NAME_IN, OBJECT_NAME_IN+'.txt')

        df = pd.read_table(obj)

        csv = df.to_csv().encode('utf-8')

        self.client.put_object(
        BUCKET_NAME_OUT,
        OBJECT_NAME_OUT+'.csv',
        data=BytesIO(csv),
        length=len(csv),
        content_type='example.txt'
        )


    def readexcel(self, BUCKET_NAME, OBJECT_NAME):
        a = self.client.presigned_get_object(BUCKET_NAME, OBJECT_NAME+'.xlsx')
        df = pd.read_excel(a)
        return df


    def writeexcel(self,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT):


        b = self.client.presigned_get_object(BUCKET_NAME_IN,OBJECT_NAME_IN+'.xlsx')
        d = pd.read_excel(b)
        csv = d.to_csv().encode('utf-8')
        self.client.put_object(
        BUCKET_NAME_OUT,
        (OBJECT_NAME_OUT + ".csv"),
        data=BytesIO(csv),
        length=len(csv),
        content_type='example.txt'
        )    

    def readparquet(self, BUCKET_NAME, OBJECT_NAME):

        e=self.client.presigned_get_object(BUCKET_NAME,OBJECT_NAME+'.parquet')
        df = pd.read_parquet(e)
        return df

    def writeparquet(self,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT):


        b = self.client.presigned_get_object(BUCKET_NAME_IN,OBJECT_NAME_IN+'.parquet')
        d = pd.read_parquet(b)
        csv = d.to_csv().encode('utf-8')
        self.client.put_object(
        BUCKET_NAME_OUT,
        (OBJECT_NAME_OUT + ".csv"),
        data=BytesIO(csv),
        length=len(csv),
        content_type='example.txt'
        )        