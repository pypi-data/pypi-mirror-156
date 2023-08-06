import sys
from cassandra.cluster import Cluster


class dpZdb:
    """
    Interact with multiple database types with dataframe in Spark
    When call this class will automatically create a Spark Session
    :param spark_name: spark app 's name
    :return: :class: `dpZdb` <dpZdb> object
    """

    def __init__(self, spark,
            storageapi=None,
            storage_access_key=None,
            storage_sec_key=None,
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

        self.spark = spark

        # Check minio input
        check_minio = False
        if (storageapi is not None and storage_sec_key is not None and storage_access_key is not None) \
                or (storageapi is None and storage_sec_key is None and storage_access_key is None):
            check_minio = True

            if storageapi is not None:
                # Minio Configuration
                self.endpoint = storageapi
                self.access_key = storage_access_key
                self.secret_key = storage_sec_key

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
            else:
                pass

        if check_minio == False:
            if storageapi is None:
                print('Error: storageapi must be not None if you want to use Minio')
                sys.exit(0)
            elif storage_sec_key is None:
                print('Error: storage_sec_key must be not None if you want to use Minio')
                sys.exit(0)
            elif storage_access_key is None:
                print('Error: storage_access_key must be not None if you want to use Minio')
                sys.exit(0)

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
        if (
                user_oracle is not None and password_oracle is not None and host_oracle is not None and port_oracle is not None) \
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


    # def get_spark_columns(self, spark_df):
    #     """
    #     Return all columns of dataframe
    #     :param spark_df: spark dataframe
    #     :return: list of column in Spark's dataframe
    #     """
    #     res = []
    #     try:
    #         for col in spark_df.dtypes:
    #             res.append(col[0])
    #     except Exception as e:
    #         print('Error:', str(e))
    #
    #     return res

    def read_minio(self, object_path, delimiter=','):
        """
        Read data from object in Minio

        :param object_path: object path in Minio
        :param delimiter: delimiter in csv file
        :return: spark dataframe of csv file
        """

        try:
            df = self.spark.read.options(header=True, delimiter=delimiter).csv('s3a://%s' % object_path)
            return df

        except Exception as e:
            print('Error in', object_path + ' :', str(e))
            sys.exit(0)


    def read_postgres(self, database, table):
        """
        Read data from postgres and return spark dataframe

        :param database: database of postgres
        :param table: table of postgres
        :return: spark dataframe
        """

        try:
            df = self.spark.read.format("jdbc").option("url", "jdbc:postgresql://%s:%s/%s" %
                                           (self.host_pg, self.port_pg, database)) \
                .option("dbtable", table) \
                .option("user", self.user_pg) \
                .option("password", self.password_pg) \
                .option("driver", "org.postgresql.Driver").load()

            return df

        except Exception as e:
            print("Error:", str(e))
            sys.exit(0)


    def read_mysql(self, database, table):
        """
        Read data from mysql and return spark dataframe

        :param database: database of mysql
        :param table: table of mysql
        :return: spark dataframe
        """

        try:
            df = self.spark.read.format("jdbc") \
                .option("url",
                        "jdbc:mysql://%s:%s/%s" % (self.host_mysql, self.port_mysql, database)) \
                .option("dbtable", table) \
                .option("user", self.user_mysql) \
                .option("password", self.password_mysql) \
                .option("driver", "com.mysql.jdbc.Driver").load()

            return df

        except Exception as e:
            print("Error:", str(e))
            sys.exit(0)


    def read_oracle(self, service_name, table):
        """
        Read data from oracle and return spark dataframe

        :param database: service name of oracle
        :param table: table of oracle
        :return: spark dataframe
        """

        try:
            df = self.spark.read.format("jdbc") \
                .option("url",
                        "jdbc:oracle:thin//%s:%s/%s" % (self.host_oracle, self.port_oracle, service_name)) \
                .option("dbtable", table) \
                .option("user", self.user_oracle) \
                .option("password", self.password_oracle) \
                .option("driver", "oracle.jdbc.driver.OracleDriver").load()

            return df

        except Exception as e:
            print("Error:", str(e))
            sys.exit(0)


    def read_mssql(self, database, table):
        """
        Read data from mssql and return spark dataframe

        :param database: database of mssql
        :param table: table of mssql
        :return: spark dataframe
        """

        try:
            df  = self.spark.read.format("jdbc") \
                .option("url",
                        "jdbc:sqlserver://%s:%s;databaseName={%s}" % (self.host_sqlsv, self.port_sqlsv, database)) \
                .option("dbtable", table) \
                .option("user", self.user_sqlsv) \
                .option("password", self.password_sqlsv) \
                .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver").load()

            return df

        except Exception as e:
            print("Error:", str(e))
            sys.exit(0)


    def read_hdfs(self, filetype, location, delimiter=','):
        """
        Read data from hdfs and return spark dataframe

        :param filetype: type of in hdfs, eg: csv, orc, parquet
        :param location: location of files
        :param delimiter: delimiter of csv file
        :return: spark dataframe
        """

        location_path = 'hdfs://' + self.hdfs_ip + ':' + self.hdfs_port + location

        if filetype == 'csv':
            try:
                df = self.spark.read.option(header=True, delimiter=delimiter).csv(location_path)

                return df
            except Exception as e:
                print("Error:", str(e))
                sys.exit(0)

        elif filetype == 'parquet':
            try:
                df = self.spark.read.option(header=True).parquet(location_path)

                return df
            except Exception as e:
                print("Error:", str(e))
                sys.exit(0)

        elif filetype == 'orc':
            try:
                df = self.spark.read.option(header=True).orc(location_path)

                return df
            except Exception as e:
                print("Error:", str(e))
                sys.exit(0)

        else:
            print(filetype + ' is not supported')
            sys.exit()


    def read_cassandra(self, keyspace, table):
        """
        Read data from cassandra and return spark dataframe

        :param keyspace: keyspace in cassandra
        :param table: table in cassandra
        :return: spark dataframe
        """

        try:
            df = self.spark.read.format("org.apache.spark.sql.cassandra")\
                .option(table=table, keyspace=keyspace)

            return df

        except Exception as e:
            print("Error:", str(e))
            sys.exit(0)


    def write_postgres(self, df, database, table):
        """
        Write spark dataframe to postgres

        :param df: spark dataframe
        :param database: database in postgres
        :param table: table in postgres
        :return:
        """

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


    def write_mysql(self, df, database, table):
        """
        Write spark dataframe to mysql

        :param df: spark dataframe
        :param database: database in mysql
        :param table: table in mysql
        :return:
        """

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


    def write_mssql(self, df, database, table):
        """
        Write spark dataframe to SQLServer

        :param df: spark dataframe
        :param database: database in sqlserver
        :param table: table in sqlserver
        :return:
        """

        try:
            df.write.format("jdbc") \
                .option("url",
                        "jdbc:sqlserver://%s:%s;databaseName={%s}" % (self.host_sqlsv, self.port_sqlsv, database)) \
                .option("dbtable", table) \
                .option("user", self.user_sqlsv) \
                .option("password", self.password_sqlsv) \
                .option("driver", "com.microsoft.sqlserver.jdbc.SQLServerDriver").mode("append") \
                .save()

        except Exception as e:
            print("Error:", str(e))
            sys.exit(0)


    def write_oracle(self, df, service_name, table):
        """
        Write spark dataframe to Oracle

        :param df: spark dataframe
        :param service_name: service name in oracle
        :param table: table in oracle
        :return:
        """

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


    def write_hdfs(self, df, location, filetype='orc', delimiter=','):
        """
        Write spark dataframe to hdfs

        :param df: spark dataframe
        :param location: location in hdfs to save file
        :param filetype: type of file to save in hdfs, eg: orc, parquet, csv
        :param delimiter: delimiter of csv file
        :return:
        """

        location_path = 'hdfs://' + self.hdfs_ip + ':' + self.hdfs_port + location

        if filetype == 'csv':
            try:
                df.write.mode('append').option(delimiter=delimiter).csv(location_path)
            except Exception as e:
                print("Error:", str(e))
                sys.exit(0)

        elif filetype == 'parquet':
            try:
                df.write.mode('append').parquet(location_path)
            except Exception as e:
                print("Error:", str(e))
                sys.exit(0)

        elif filetype == 'orc':
            try:
                df.write.mode('append').orc(location_path)

            except Exception as e:
                print("Error:", str(e))
                sys.exit(0)

        else:
            print(filetype + ' is not supported')
            sys.exit()


    def write_cassandra(self, df, keyspace, table):
        """
        Write spark dataframe to cassandra

        :param df: spark dataframe
        :param keyspace: keyspace in cassandra
        :param table: table in cassandra
        :return:
        """

        try:
            df.write.format("org.apache.spark.sql.cassandra").mode('append').options(table=table_cassandra,
                                                                                     keyspace=keyspace_cassandra).save()

        except Exception as e:
            print('Error:', str(e))
            sys.exit()


    def write_minio(self, df, file_path, delimiter=','):
        """
        Write spark dataframe to Minio, type of file is csv
        :param df: spark dataframe
        :param file_path: file  _path in Minio
        :param delimiter: delimiter of csv file
        :return:
        """

        try:
            df.write.format('csv').option(header=True, delimiter=delimiter).save('s3a://' + file_path, mode='append')

        except Exception as e:
            print('Error:', str(e))
            sys.exit()
