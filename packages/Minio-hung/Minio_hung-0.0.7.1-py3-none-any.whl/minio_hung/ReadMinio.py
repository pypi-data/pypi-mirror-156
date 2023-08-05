from importlib.resources import read_text
from minio import Minio
import pandas as pd
from io import BytesIO
import os

def readcsv(ACCESS_KEY,PRIVATE_KEY,BUCKET_NAME,OBJECT_NAME):
    client = Minio(
        "apilakedpa.apps.xplat.fis.com.vn",
        access_key=ACCESS_KEY,
        secret_key=PRIVATE_KEY,
        secure = True
        )

    obj = client.get_object(BUCKET_NAME,OBJECT_NAME+'.csv')

    de = pd.read_csv(obj)

    print(de)

def writecsv(ACCESS_KEY,PRIVATE_KEY,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT):
    client = Minio(
        "apilakedpa.apps.xplat.fis.com.vn",
        access_key=ACCESS_KEY,
        secret_key=PRIVATE_KEY,
        secure = True
        )

    obj = client.get_object(BUCKET_NAME_IN, OBJECT_NAME_IN+'.csv')

    df = pd.read_csv(obj)

    csv = df.to_csv().encode('utf-8')

    client.put_object(
    BUCKET_NAME_OUT,
    OBJECT_NAME_OUT+'.csv',
    data=BytesIO(csv),
    length=len(csv),
    content_type='example.csv'
)

def readtext(ACCESS_KEY,PRIVATE_KEY,BUCKET_NAME,OBJECT_NAME):
    client = Minio(
        "apilakedpa.apps.xplat.fis.com.vn",
        access_key=ACCESS_KEY,
        secret_key=PRIVATE_KEY,
        secure = True
        )

    obj = client.get_object(BUCKET_NAME,OBJECT_NAME+'.txt')

    df = pd.read_table(obj)

    print(df)

def writetext(ACCESS_KEY,PRIVATE_KEY,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT):
    client = Minio(
        "apilakedpa.apps.xplat.fis.com.vn",
        access_key=ACCESS_KEY,
        secret_key=PRIVATE_KEY,
        secure = True
        )

    obj = client.get_object(BUCKET_NAME_IN, OBJECT_NAME_IN+'.txt')

    df = pd.read_table(obj)

    csv = df.to_csv().encode('utf-8')

    client.put_object(
    BUCKET_NAME_OUT,
    OBJECT_NAME_OUT+'.csv',
    data=BytesIO(csv),
    length=len(csv),
    content_type='example.txt'
    )

def read_list(ACCESS_KEY, PRIVATE_KEY):
    client = Minio(
        "apilakedpa.apps.xplat.fis.com.vn",
        access_key=ACCESS_KEY,
        secret_key=PRIVATE_KEY,
        secure = True
        )

    a = client.list_buckets()    
    print(a)

def readexcel(ACCESS_KEY, PRIVATE_KEY, BUCKET_NAME, OBJECT_NAME):
    client = Minio(
        "apilakedpa.apps.xplat.fis.com.vn",
        access_key=ACCESS_KEY,
        secret_key=PRIVATE_KEY,
        secure = True
        )

    a = client.presigned_get_object(BUCKET_NAME, OBJECT_NAME+'.xlsx')
    c = pd.read_excel(a)
    print(c)

def writeexcel(ACCESS_KEY,PRIVATE_KEY,BUCKET_NAME_IN,OBJECT_NAME_IN,BUCKET_NAME_OUT,OBJECT_NAME_OUT):
    client = Minio(
        "apilakedpa.apps.xplat.fis.com.vn",
        access_key=ACCESS_KEY,
        secret_key=PRIVATE_KEY,
        secure = True
        )

    b = client.presigned_get_object(BUCKET_NAME_IN,OBJECT_NAME_IN+'.xlsx')
    d = pd.read_excel(b)
    csv = d.to_csv().encode('utf-8')
    client.put_object(
    BUCKET_NAME_OUT,
    (OBJECT_NAME_OUT + ".csv"),
    data=BytesIO(csv),
    length=len(csv),
    content_type='example.txt'
    )    