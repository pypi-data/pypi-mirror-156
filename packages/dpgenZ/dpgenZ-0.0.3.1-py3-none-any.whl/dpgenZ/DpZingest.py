from pyspark.sql import SparkSession
import sys
import psycopg2
from minio import Minio
import pandas as pd
from cassandra.cluster import Cluster


class DBStorage:
    """
        Class for fetching data from Minio and storage in Database likes Postgres, Cassandra, HDFS
    """

    def __init__(self, storageapi,
                 storage_access_key,
                 storage_sec_key,
                 user_pg=None,
                 password_pg=None,
                 host_pg=None,
                 port_pg=None,
                 host_sqlsv=None,
                 port_sqlsv=None,
                 user_sqlsv=None,
                 password_sqlsv=None,
                 hdfs_ip=None,
                 hdfs_port=None,
                 user_oracle=None,
                 password_oracle=None,
                 host_oracle=None,
                 port_oracle=None,
                 user_mysql=None,
                 password_mysql=None,
                 host_mysql=None,
                 port_mysql=None,
                 cassandra_cluster=None,
                 cassandra_port=9042):
        """
        :param storageapi: hostname of Minio
        :param storage_access_key: access key of Minio
        :param storage_sec_key: secret key of Minio
        :param user_pg: username of postgres server
        :param password_pg: password of postgres server
        :param host_pg: host of postgres server
        :param port_pg: port of postgres server
        :param host_sqlsv: host of sqlserver
        :param port_sqlsv: port of sqlserver
        :param user_sqlsv: username of sqlserver
        :param password_sqlsv: password of sqlserver
        :param hdfs_ip: ip of hdfs server
        :param hdfs_port: port of hdfs server
        :param user_oracle: username of oracle
        :param password_oracle: password of oracle
        :param host_oracle: hostname of oracle
        :param port_oracle: port of oracle
        :param user_mysql: username of mysql
        :param password_mysql: password of mysql
        :param host_mysql: hostname of mysql
        :param port_mysql: port of mysql
        :param cassandra_cluster: list of ip cassandra cluster
        :param cassandra_port: port of cassandra

        *Note: If you want to store in any database, you need to fill in all the parameters related to that database.
        Example:
            client = DBStorage(
                storageapi='lakedpaapi-fis-mbf-dplat.apps.xplat.fis.com.vn',
                storage_access_key='I5pnix8qE2mtXlXR',
                storage_sec_key='hzADsWEM8DGIIQBrfjNWNNy4j0OG0cSA',
                user_pg='cuongnm',
                password_pg='123456',
                host_pg='127.0.0.1',
                port_pg=5432,
                host_sqlsv='127.0.0.1',
                port_sqlsv=1433,
                user_sqlsv='cuongnm',
                password_sqlsv='123456',
                hdfs_ip='10.15.10.200',
                hdfs_port=9000,
                user_oracle='cuongnm',
                password_oracle='123456',
                host_oracle='127.0.0.1',
                port_oracle=1521,
                user_mysql='cuongnm',
                password_mysql='123456',
                host_mysql='127.0.0.1',
                port_mysql=3306,
                cassandra_cluster=['127.0.0.1', '127.0.0.2'],
                cassndra_port=9042
            )
        """

        # Check postgres input
        check_pg = False
        if (user_pg is not None and password_pg is not None and host_pg is not None and port_pg is not None) \
                or (user_pg is None and password_pg is None and host_pg is None and port_pg is None):
            check_pg = True

        if check_pg == False:
            if user_pg is None:
                print('Error: user_pg must be not None if you want to use Postgres DB')
                sys.exit(0)
            elif password_pg is None:
                print('Error: password_pg must be not None if you want to use Postgres DB')
                sys.exit(0)
            elif host_pg is None:
                print('Error: host_pg must be not None if you want to use Postgres DB')
                sys.exit(0)
            elif port_pg is None:
                print('Error: port_pg must be not None if you want to use Postgres DB')
                sys.exit(0)

        # Check hdfs input
        check_hdfs = False
        if (hdfs_ip is not None or hdfs_port is not None) or (hdfs_ip is None or hdfs_port is None):
            check_hdfs = True

        if check_hdfs == False:
            if hdfs_ip is None:
                print('Error: hdfs_ip must be not None if you want to use HDFS')
                sys.exit(0)
            elif hdfs_port is None:
                print('Error: hdfs_port must be not None if you want to use HDFS')
                sys.exit(0)

        # Check sqlserver input
        check_sqlsv = False
        if (user_sqlsv is not None and password_sqlsv is not None and host_sqlsv is not None and port_sqlsv is not None) \
                or (user_sqlsv is None and password_sqlsv is None and host_sqlsv is None and port_sqlsv is None):
            check_sqlsv = True

        if check_sqlsv == False:
            if user_sqlsv is None:
                print('Error: user_sqlsv must be not None if you want to use SQLServer DB')
                sys.exit(0)
            elif password_sqlsv is None:
                print('Error: password_sqlsv must be not None if you want to use SQLServer DB')
                sys.exit(0)
            elif host_sqlsv is None:
                print('Error: host_sqlsv must be not None if you want to use SQLServer DB')
                sys.exit(0)
            elif port_sqlsv is None:
                print('Error: port_sqlsv must be not None if you want to use SQLServer DB')
                sys.exit(0)

        # Check oracle input
        check_oracle = False
        if (user_oracle is not None and password_oracle is not None and host_oracle is not None and port_oracle is not None) \
                or (user_oracle is None and password_oracle is None and host_oracle is None and port_oracle is None):
            check_oracle = True

        if check_oracle == False:
            if user_oracle is None:
                print('Error: user_oracle must be not None if you want to use Oracle DB')
                sys.exit(0)
            elif password_oracle is None:
                print('Error: password_oracle must be not None if you want to use Oracle DB')
                sys.exit(0)
            elif host_oracle is None:
                print('Error: host_oracle must be not None if you want to use Oracle DB')
                sys.exit(0)
            elif port_oracle is None:
                print('Error: port_oracle must be not None if you want to use Oracle DB')
                sys.exit(0)

        # Check mysql input
        check_mysql = False
        if (user_mysql is not None and password_mysql is not None and host_mysql is not None and port_mysql is not None) \
                or (user_mysql is None and password_mysql is None and host_mysql is None and port_mysql is None):
            check_mysql = True

        if check_mysql == False:
            if user_mysql is None:
                print('Error: user_mysql must be not None if you want to use MySQL DB')
                sys.exit(0)
            elif password_mysql is None:
                print('Error: password_mysql must be not None if you want to use MySQL DB')
                sys.exit(0)
            elif host_mysql is None:
                print('Error: host_mysql must be not None if you want to use MySQL DB')
                sys.exit(0)
            elif port_mysql is None:
                print('Error: port_mysql must be not None if you want to use MySQL DB')
                sys.exit(0)

        # Minio Configuration
        self.endpoint = storageapi
        self.access_key = storage_access_key
        self.secret_key = storage_sec_key

        # Postgres Configuration
        self.user_pg = user_pg
        self.password_pg = password_pg
        self.host_pg = host_pg
        self.port_pg = port_pg

        # SQLServer Configuration
        self.user_sqlsv = user_sqlsv
        self.password_sqlsv = password_sqlsv
        self.host_sqlsv = host_sqlsv
        self.port_sqlsv = port_sqlsv

        # HDFS Configuration
        self.hdfs_ip = hdfs_ip
        self.hdfs_port = hdfs_port

        # Oracle Configuration
        self.user_oracle = user_oracle
        self.password_oracle = password_oracle
        self.host_oracle = host_oracle
        self.port_oracle = port_oracle

        # MySQL Configuration
        self.user_mysql = user_mysql
        self.password_mysql = password_mysql
        self.host_mysql = host_mysql
        self.port_mysql = port_mysql

        # Cassandra Configuration
        self.cluster = cassandra_cluster
        self.cassandra_port = cassandra_port

        # Minio Connection
        try:
            self.client_minio = Minio(
                endpoint=self.endpoint,
                access_key=self.access_key,
                secret_key=self.secret_key,
                secure=False
            )
        except Exception as e:
            print("Error:", str(e))
            sys.exit(0)

        # Spark Session
        try:
            self.spark_connection = SparkSession.builder.appName("Minio to DB") \
                .config("spark.submit.deployMode", 'client') \
                .config("spark.driver.memory", '8g') \
                .config("spark.driver.maxResultSize", '8g') \
                .config("spark.executor.memory", '8g') \
                .config("spark.executor.cores", '1') \
                .config("spark.executor.instances", '1') \
                .config("spark.sql.shuffle.partitions", '400') \
                .config("spark.sql.execution.arrow.enabled", "true") \
                .config("spark.hadoop.fs.s3a.endpoint", 'http://' + self.endpoint) \
                .config("spark.hadoop.fs.s3a.access.key", self.access_key) \
                .config("spark.hadoop.fs.s3a.secret.key", self.secret_key) \
                .config("spark.hadoop.fs.s3a.path.style.access", "true") \
                .config("spark.hadoop.fs.s3a.impl", "org.apache.hadoop.fs.s3a.S3AFileSystem") \
                .config("fs.s3a.connection.ssl.enabled", "false") \
                .config("spark.sql.catalog.myCatalog", "com.datastax.spark.connector.datasource.CassandraCatalog") \
                .config("spark.cassandra.connection.host", "cassandra") \
                .enableHiveSupport().getOrCreate()

        except Exception as e:
            print('Error:', str(e))
            sys.exit(0)


    def split_bucket_and_folder(self, bucket_or_folder):
        """
        Split bucket name and folder path if bucket_or_folder is a folder path
        :param bucket_or_folder: bucket name or folder path
        :return: bucket, folder_path
        Example:
            bucket_name: bucket_1
            folder_path: bucket1/folder_1/folder_2/.../folder_n
        """

        bucket = ''
        folder = ''

        if '/' not in bucket_or_folder:
            bucket = bucket_or_folder
        else:
            index = 0
            for i in bucket_or_folder:
                if i != '/':
                    index += 1
                else:
                    break

            bucket = bucket_or_folder[:index]

            folder = bucket_or_folder[index + 1:]

        return bucket, folder


    def get_object_list(self, bucket_or_folder):
        """
        Get object list in folder or bucket
        :param bucket_or_folder: bucket or folder path in Minio
        :return: objects list
        """

        bucket, folder = self.split_bucket_and_folder(bucket_or_folder)

        objects = self.client_minio.list_objects(bucket, recursive=True)

        list_obj = list(objects)
        tmp_remove = list()

        if len(folder) != 0:
            for object in list_obj:
                if folder not in object.object_name:
                    tmp_remove.append(object)

        for i in tmp_remove:
            list_obj.remove(i)

        return list_obj


    def check_columns(self, bucket_or_folder, delimiter=','):
        """
        Get columns information in csv files in Minio
        :param bucket_or_folder: bucket name or link folder in a bucket in Minio
        :param filetype: type of file, eg: csv
        :param delimiter: delimiter in csv file
        :return: True if columns in all files are same
                and False if not
        """

        bucket, folder = self.split_bucket_and_folder(bucket_or_folder)

        objects = self.get_object_list(bucket_or_folder)

        columns = list()
        check_first = True  # Check first object in bucket

        for object in objects:
            data = self.client_minio.get_object(
                bucket_name=bucket,
                object_name=object.object_name
            )

            try:
                df = pd.read_csv(data, delimiter=delimiter, header=0, nrows=0)
            except Exception as e:
                print("Error:", str(e))
                sys.exit(0)

            columns_df = list(df.columns)

            if check_first == True:
                columns = columns_df
                check_first = False
            else:
                if columns != columns_df:
                    print('Error: Columns in', object.object_name, 'are different from previous columns')
                    return False

        if len(columns) == 0:
            print("Bucket doesn't have any files or file doesn't have records")
            return False

        return True


    def read_data_from_Minio(self, object_path, delimiter=','):
        """
        Read data from object in Minio
        :param object_path: object path in Minio
        :param filetype: type of file, eg: csv
        :param delimiter: delimiter in csv file
        :return: spark dataframe of csv file
        """

        try:
            df = self.spark_connection.read.options(header=True, delimiter=delimiter).csv('s3a://%s' % object_path)
            return df

        except Exception as e:
            print('Error in', object_path + ' :', str(e))
            sys.exit(0)


    def store_to_postgres(self, bucket_or_folder, database, table, delimiter=','):
        """
        Storing data in Postgres from Minio

        :param bucket_or_folder: bucket name or folder path in Minio
        :param database: database name in Postgres
        :param table: table name in Postgres
        :param delimiter: delimiter in csv file
        :return:
        """

        if self.check_columns(bucket_or_folder, delimiter) == False:
            print('Check columns !!!')
            sys.exit()

        # try:
        #     conn = psycopg2.connect(
        #         host=self.host_pg,
        #         user=self.user_pg,
        #         password=self.password_pg,
        #         port=self.port_pg,
        #         database=database,
        #     )
        # except Exception as e:
        #     print('Error:', str(e))
        #     sys.exit(0)

        # cursor = conn.cursor()
        #
        # """
        #     Create table if not exists in database
        # """
        #
        # sql = 'CREATE TABLE IF NOT EXISTS %s (' % table
        #
        # for column in columns:
        #     sql += column + ' VARCHAR,'
        #
        # sql = sql[:-1] + ')'
        #
        # cursor.execute(sql)
        # cursor.close()
        # conn.commit()

        # Insert data
        bucket, folder = self.split_bucket_and_folder(bucket_or_folder)
        objects = self.get_object_list(bucket_or_folder)

        for object in objects:
            object_path = '%s/%s' % (bucket, object.object_name)

            df = self.read_data_from_Minio(object_path, delimiter)

            try:
                df.write.format("jdbc").option("url", "jdbc:postgresql://%s:%s/%s" %
                                               (self.host_pg, self.port_pg, database)) \
                    .option("dbtable", table) \
                    .option("user", self.user_pg) \
                    .option("password", self.password_pg) \
                    .option("driver", "org.postgresql.Driver").mode("append").save()

            except Exception as e:
                print("Error:", str(e))
                sys.exit(0)


    def storage_to_hdfs(self, bucket_or_folder, location, delimiter=','):
        """
        Storing data in HDFS from Minio

        :param bucket_or_folder: bucket or folder path in Minio
        :param delimiter: delimiter of csv file
        :param location: location to save in hdfs
        :return:
        """

        if self.check_columns(bucket_or_folder, delimiter) == False:
            print('Check columns !!!')
            sys.exit()

        # Insert data
        bucket, folder = self.split_bucket_and_folder(bucket_or_folder)
        objects = self.get_object_list(bucket_or_folder)

        for object in objects:
            object_path = '%s/%s' % (bucket, object.object_name)

            csv_df = self.read_data_from_Minio(object_path, delimiter)

            # destination in hdfs
            destination =  'hdfs://' + self.hdfs_ip + ':' + self.hdfs_port + location

            try:
                csv_df.write.mode('append').orc(destination)
            except Exception as e:
                print('Error:', str(e))
                sys.exit(0)


    def storage_to_cassandra(self, bucket_or_folder, keyspace, table, delimiter=','):
        """
        Storing data in Cassandra from Minio

        :param bucket_or_folder: bucket or folder path in Minio
        :param delimiter: delimiter in csv file
        :param keyspace: keyspace in Cassandra
        :param table: table in Cassandra
        :return:
        """

        if self.check_columns(bucket_or_folder, delimiter) == False:
            print('Check columns !!!')
            sys.exit()

        # cluster = Cluster(self.cluster, self.cassandra_port)
        # session = cluster.connect()

        # keyspace_rows = session.execute("SELECT keyspace_name FROM system.schema_keyspaces")
        #
        # # Create keyspace if not exists
        # check_keyspace = False
        # for row in keyspace_rows:
        #     if keyspace in row[0]:
        #         check_keyspace = True
        #
        # if check_keyspace == False:
        #     session.execute("CREATE KEYSPACE %s WITH replication = {'class': 'SimpleStrategy', 'replication_factor': '2'" % keyspace)
        #
        # session.set_keyspace(keyspace)

        # # Create table if not exists
        # sql = "CREATE TABLE IF NOT EXISTS %s (" % table
        # for column in columns:
        #     sql += column + ' text,'
        #
        # sql = sql[:-1] + ')'
        #
        # session.execute(sql)

        # Insert data
        bucket, folder = self.split_bucket_and_folder(bucket_or_folder)
        objects = self.get_object_list(bucket_or_folder)

        for object in objects:
            object_path = '%s/%s' % (bucket, object.object_name)

            csv_df = self.read_data_from_Minio(object_path, delimiter)

            try:
                csv_df.write.format("org.apache.spark.sql.cassandra").mode('append').options(table=table, keyspace=keyspace).save()
            except Exception as e:
                print("Error:", object_path, str(e))


    def storage_to_sqlserver(self, bucket_or_folder, database, table, delimiter=','):
        """
        Storing data in SQLServer from Minio

        :param bucket_or_folder: bucket name or folder path in Minio
        :param database: database name in SQLServer
        :param table: table name in SQLServer
        :param delimiter: delimiter in csv file
        :return:
        """

        if self.check_columns(bucket_or_folder, delimiter) == False:
            print('Check columns !!!')
            sys.exit()

        bucket, folder = self.split_bucket_and_folder(bucket_or_folder)
        objects = self.get_object_list(bucket_or_folder)

        for object in objects:
            object_path = '%s/%s' % (bucket, object.object_name)

            df = self.read_data_from_Minio(object_path, delimiter)

            try:
                df.write.format("jdbc")\
                    .option("url", "jdbc:sqlserver://%s:%s;databaseName={%s}" % (self.host_sqlsv, self.port_sqlsv, database)) \
                    .option("dbtable", table) \
                    .option("user", self.user_sqlsv) \
                    .option("password", self.password_sqlsv) \
                    .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver").mode("append")\
                    .save()

            except Exception as e:
                print("Error:", str(e))
                sys.exit(0)


    def storage_to_oracle(self, bucket_or_folder, service_name, table, delimiter=','):
        """
        Storing data in Oracle from Minio

        :param bucket_or_folder: bucket name or folder path in Minio
        :param service_name: service name in Oracle
        :param table: table name in Oracle
        :param delimiter: delimiter in csv file
        :return:
        """

        if self.check_columns(bucket_or_folder, delimiter) == False:
            print('Check columns !!!')
            sys.exit()

        bucket, folder = self.split_bucket_and_folder(bucket_or_folder)
        objects = self.get_object_list(bucket_or_folder)

        for object in objects:
            object_path = '%s/%s' % (bucket, object.object_name)

            df = self.read_data_from_Minio(object_path, delimiter)

            try:
                df.write.format("jdbc") \
                    .option("url",
                            "jdbc:oracle:thin//%s:%s/%s" % (self.host_oracle, self.port_oracle, service_name)) \
                    .option("dbtable", table) \
                    .option("user", self.user_oracle) \
                    .option("password", self.password_oracle) \
                    .option("driver", "oracle.jdbc.driver.OracleDriver").mode("append") \
                    .save()

            except Exception as e:
                print("Error:", str(e))
                sys.exit(0)


    def storage_to_mysql(self, bucket_or_folder, database, table, delimiter=','):
        """
        Storing data in MySQL from Minio

        :param bucket_or_folder: bucket name or folder path in Minio
        :param database: database name in MySQL
        :param table: table name in MySQL
        :param delimiter: delimiter in csv file
        :return:
        """

        if self.check_columns(bucket_or_folder, delimiter) == False:
            print('Check columns !!!')
            sys.exit()

        bucket, folder = self.split_bucket_and_folder(bucket_or_folder)
        objects = self.get_object_list(bucket_or_folder)

        for object in objects:
            object_path = '%s/%s' % (bucket, object.object_name)

            df = self.read_data_from_Minio(object_path, delimiter)

            try:
                df.write.format("jdbc") \
                    .option("url",
                            "jdbc:mysql://%s:%s/%s" % (self.host_mysql, self.port_mysql, database)) \
                    .option("dbtable", table) \
                    .option("user", self.user_mysql) \
                    .option("password", self.password_mysql) \
                    .option("driver", "com.mysql.jdbc.Driver").mode("append") \
                    .save()

            except Exception as e:
                print("Error:", str(e))
                sys.exit(0)
