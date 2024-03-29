# -*- coding: utf-8 -*-
"""Data_Warehouse_Project.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1eCb3RT36jw5iqubKHWj9L3gD4ZARXsWv

## Data Warehouse creation using ETL Pipelining

### Section 1: Prerequisites

#### Import Required Libraries
"""

import os
import json
import pymongo
import pyspark.pandas as pd  # This uses Koalas that is included in PySpark version 3.2 or newer.
from pyspark.sql.functions import col
from pyspark.sql.types import StructType, StructField, StringType, TimestampType, BinaryType
from pyspark.sql.types import ByteType, ShortType, IntegerType, LongType, FloatType, DecimalType

"""#### Instantiate Global Variables"""

# Azure MySQL Server Connection Information ###################
jdbc_hostname = " "
jdbc_port = 3306
src_database = "sakila_project"

connection_properties = {
  "user" : " ",
  "password" : " ",
  "driver" : "org.mariadb.jdbc.Driver"
}

# MongoDB Atlas Connection Information ########################
atlas_cluster_name = "cluster0.2skipiu"
atlas_database_name = "sakila_project"
atlas_user_name = "nck6fj"
atlas_password = " "

# Data Files (JSON) Information ###############################
dst_database = "sakila_project"
base_dir = "dbfs:/FileStore/lab_data"

data_dir = f"{base_dir}/project_data/source_data"
batch_dir = f"{data_dir}/batch"
stream_dir = f"{data_dir}/stream"

database_dir = f"{base_dir}/{dst_database}"

orders_stream_dir = f"{stream_dir}/orders"
purchase_orders_stream_dir = f"{stream_dir}/purchase_orders"
inventory_trans_stream_dir = f"{stream_dir}/inventory_transactions"

orders_output_bronze = f"{database_dir}/fact_orders_bronze"
orders_output_silver = f"{database_dir}/fact_orders_silver"
orders_output_gold = f"{database_dir}/fact_orders_gold"

inventory_output_bronze = f"{database_dir}/fact_inventory_bronze"
inventory_output_silver = f"{database_dir}/fact_inventory_silver"
inventory_output_gold = f"{database_dir}/fact_inventory_gold"

rental_output_bronze = f"{database_dir}/fact_rental_bronze"
rental_output_silver = f"{database_dir}/fact_rental_silver"
rental_output_gold = f"{database_dir}/fact_rental_gold"

# Delete the Streaming Files ##################################
dbutils.fs.rm(f"{database_dir}/fact_payment", True)
dbutils.fs.rm(f"{database_dir}/fact_inventory", True)
dbutils.fs.rm(f"{database_dir}/fact_rental", True)

# Delete the Database Files ###################################
dbutils.fs.rm(database_dir, True)

"""#### 3.0 Define Global Functions"""

##################################################################################################################
# Use this Function to Fetch a DataFrame from the MongoDB Atlas database server Using PyMongo.
##################################################################################################################
def get_mongo_dataframe(user_id, pwd, cluster_name, db_name, collection, conditions, projection, sort):
    '''Create a client connection to MongoDB'''
    mongo_uri = f"mongodb+srv://{user_id}:{pwd}@{cluster_name}.mongodb.net/{db_name}"

    client = pymongo.MongoClient(mongo_uri)

    '''Query MongoDB, and fill a python list with documents to create a DataFrame'''
    db = client[db_name]
    if conditions and projection and sort:
        dframe = pd.DataFrame(list(db[collection].find(conditions, projection).sort(sort)))
    elif conditions and projection and not sort:
        dframe = pd.DataFrame(list(db[collection].find(conditions, projection)))
    else:
        dframe = pd.DataFrame(list(db[collection].find()))

    client.close()

    return dframe

##################################################################################################################
# Use this Function to Create New Collections by Uploading JSON file(s) to the MongoDB Atlas server.
##################################################################################################################
def set_mongo_collection(user_id, pwd, cluster_name, db_name, src_file_path, json_files):
    '''Create a client connection to MongoDB'''
    mongo_uri = f"mongodb+srv://{user_id}:{pwd}@{cluster_name}.mongodb.net/{db_name}"
    client = pymongo.MongoClient(mongo_uri)
    db = client[db_name]

    '''Read in a JSON file, and Use It to Create a New Collection'''
    for file in json_files:
        db.drop_collection(file)
        json_file = os.path.join(src_file_path, json_files[file])
        with open(json_file, 'r') as openfile:
            json_object = json.load(openfile)
            file = db[file]
            result = file.insert_many(json_object)

    client.close()

    return result

"""### Section II: Populate Dimensions by Ingesting Reference (Cold-path) Data
#### 1.0. Fetch Reference Data From an Azure MySQL Database
##### 1.1. Create a New Databricks Metadata Database.
"""

# Commented out IPython magic to ensure Python compatibility.
# %sql
DROP DATABASE IF EXISTS sakila_dlh CASCADE;

# Commented out IPython magic to ensure Python compatibility.
# %sql
CREATE DATABASE IF NOT EXISTS sakila_dlh
COMMENT "DS-2002 Final Database"
LOCATION "dbfs:/FileStore/lab_data/sakila_dlh"
WITH DBPROPERTIES (contains_pii = true, purpose = "DS-2002 Final");

"""#### 1.2. Create a New Table that Sources Date Dimension Data from a Table in an Azure MySQL database."""

# Commented out IPython magic to ensure Python compatibility.
# %sql
CREATE OR REPLACE TEMPORARY VIEW view_date
USING org.apache.spark.sql.jdbc
OPTIONS (
  url "jdbc:mysql://nck6fj-mysql.mysql.database.azure.com:3306/sakila_project", --Replace with your Server Name
  dbtable "dim_date",
  user "nkirkman",    --Replace with your User Name
  password "AppleFritter098#!"  --Replace with you password
)

# Commented out IPython magic to ensure Python compatibility.
# %sql
USE DATABASE sakila_dlh;

CREATE OR REPLACE TABLE sakila_dlh.dim_date
COMMENT "Date Dimension Table"
LOCATION "dbfs:/FileStore/lab_data/sakila_dlh/dim_date"
AS SELECT * FROM view_date

# Commented out IPython magic to ensure Python compatibility.
# %sql
DESCRIBE EXTENDED sakila_dlh.dim_date;

# Commented out IPython magic to ensure Python compatibility.
# %sql
SELECT * FROM sakila_dlh.dim_date LIMIT 5

"""#### 1.3. Create a New Table that Sources Customer Dimension Data from an Azure MySQL database."""

# Commented out IPython magic to ensure Python compatibility.
# %sql
-- Create a Temporary View named "view_customer" that extracts data from your MySQL Northwind database.
CREATE OR REPLACE TEMPORARY VIEW view_customer
USING org.apache.spark.sql.jdbc
OPTIONS (
  url "jdbc:mysql://nck6fj-mysql.mysql.database.azure.com:3306/sakila_project", --Replace with your Server Name
  dbtable "dim_customer",
  user "nkirkman",
  password " "
)

# Commented out IPython magic to ensure Python compatibility.
# %sql
USE DATABASE sakila_dlh;

CREATE OR REPLACE TABLE sakila_dlh.dim_customer
COMMENT "Customer Dimension Table"
LOCATION "dbfs:/FileStore/lab_data/sakila_dlh/dim_customer"
AS SELECT * FROM view_customer

-- Create a new table named "sakila_project.dim_customer" using data from the view named "view_customer"

# Commented out IPython magic to ensure Python compatibility.
# %sql
DESCRIBE EXTENDED sakila_dlh.dim_customer;

# Commented out IPython magic to ensure Python compatibility.
# %sql
SELECT * FROM sakila_dlh.dim_customer LIMIT 5

"""#### 2.0. Fetch Reference Data in JSON format from a MongoDB Atlas Database
###### 2.1. View the Data Files on the Databricks File System
"""

source_dir = '/Workspace/Users/nck6fj@virginia.edu/DS-2002-main/04-Databricks/lab_data/retail/batch'
json_files = {"payment" : 'sakila_payment.json'
              , "rental" : 'sakila_rental.json'}

set_mongo_collection(atlas_user_name, atlas_password, atlas_cluster_name, atlas_database_name, source_dir, json_files)

"""####2.3.1. Fetch Rental Dimension Data from the New MongoDB Collection"""

# Commented out IPython magic to ensure Python compatibility.
# %scala
import com.mongodb.spark._

val userName = "nck6fj"
val pwd = " "
val clusterName = "cluster0.2skipiu"
val atlas_uri = s"mongodb+srv://$userName:$pwd@$clusterName.mongodb.net/?retryWrites=true&w=majority"

# Commented out IPython magic to ensure Python compatibility.
# %scala

val df_rental = spark.read.format("com.mongodb.spark.sql.DefaultSource")
.option("spark.mongodb.input.uri", atlas_uri)
.option("database", "sakila_project")
.option("collection", "rental").load()
.select("rental_id", "rental_date", "inventory_id", "customer_id", "return_date", "staff_id", "last_update")

display(df_rental)

# Commented out IPython magic to ensure Python compatibility.
# %scala
df_rental.printSchema()

"""#### 2.3.2. Use the Spark DataFrame to Create a New Rental Dimension Table in the Databricks Metadata Database (sakila_project)"""

# Commented out IPython magic to ensure Python compatibility.
# %scala
df_rental.write.format("delta").mode("overwrite").saveAsTable("sakila_dlh.dim_rental")

# Commented out IPython magic to ensure Python compatibility.
# %sql
DESCRIBE EXTENDED sakila_dlh.dim_rental

# Commented out IPython magic to ensure Python compatibility.
# %sql
SELECT * FROM sakila_dlh.dim_rental LIMIT 5

"""#### 2.4.1 Fetch Payment Dimension Data from the New MongoDB Collection"""

# Commented out IPython magic to ensure Python compatibility.
# %scala
val df_payment = spark.read.format("com.mongodb.spark.sql.DefaultSource")
.option("spark.mongodb.input.uri", atlas_uri)
.option("database", "sakila_project")
.option("collection", "payment").load()
.select("payment_id","customer_id","staff_id","rental_id","amount", "payment_date", "last_update")

display(df_payment)

# Commented out IPython magic to ensure Python compatibility.
# %scala
df_payment.printSchema()

"""#### 2.4.2. Use the Spark DataFrame to Create a New Payment Dimension Table in the Databricks Metadata Database (sakila_project)"""

# Commented out IPython magic to ensure Python compatibility.
# %scala
df_payment.write.format("delta").mode("overwrite").saveAsTable("sakila_dlh.dim_payment")

# Commented out IPython magic to ensure Python compatibility.
# %sql
DESCRIBE EXTENDED sakila_dlh.dim_payment

# Commented out IPython magic to ensure Python compatibility.
# %sql
SELECT * FROM sakila_dlh.dim_payment LIMIT 5

"""#### 3.0. Fetch Inventory Data from a File System
#### 3.1. Use PySpark to Read From a CSV File
"""

inventory_csv = f"{batch_dir}/sakila_inventory.csv"

df_inventory = spark.read.format('csv').options(header='true', inferSchema='true').load(inventory_csv)
display(df_inventory)

df_inventory.printSchema()

df_inventory.write.format("delta").mode("overwrite").saveAsTable("sakila_dlh.dim_inventory")

# Commented out IPython magic to ensure Python compatibility.
# %sql
DESCRIBE EXTENDED sakila_dlh.dim_inventory;

# Commented out IPython magic to ensure Python compatibility.
# %sql
SELECT * FROM sakila_dlh.dim_inventory LIMIT 5;

"""##### Verify Dimension Tables"""

# Commented out IPython magic to ensure Python compatibility.
# %sql
USE sakila_dlh;
SHOW TABLES

"""### Section III: Integrate Reference Data with Real-Time Data
#### 6.0. Use AutoLoader to Process Streaming (Hot Path) Orders Fact Data
##### 6.1. Bronze Table: Process 'Raw' JSON Data
"""

display(dbutils.fs.ls(orders_stream_dir))

(spark.readStream
 .format("cloudFiles")
 .option("cloudFiles.format", "json")
 .option("cloudFiles.schemaLocation", orders_output_bronze)
 .option("cloudFiles.inferColumnTypes", "true")
 .option("multiLine", "true")
 .load(orders_stream_dir)
 .createOrReplaceTempView("orders_raw_tempview"))

# Commented out IPython magic to ensure Python compatibility.
# %sql
/* Add Metadata for Traceability */
CREATE OR REPLACE TEMPORARY VIEW orders_bronze_tempview AS (
  SELECT *, current_timestamp() receipt_time, input_file_name() source_file
  FROM orders_raw_tempview
)

# Commented out IPython magic to ensure Python compatibility.
# %sql
SELECT * FROM orders_bronze_tempview

(spark.table("orders_bronze_tempview")
    .writeStream
    .format("delta")
    .option("checkpointLocation", f"{orders_output_bronze}/_checkpoint")
    .outputMode("append")
    .table("fact_orders_bronze"))

"""#### 6.2. Silver Table: Include Reference Data"""

(spark.readStream
  .table("fact_orders_bronze")
  .createOrReplaceTempView("orders_silver_tempview"))

# Commented out IPython magic to ensure Python compatibility.
# %sql
SELECT * FROM orders_silver_tempview

# Commented out IPython magic to ensure Python compatibility.
# %sql
DESCRIBE EXTENDED orders_silver_tempview

# Commented out IPython magic to ensure Python compatibility.
# %sql
CREATE OR REPLACE TEMPORARY VIEW fact_orders_silver_tempview AS (
SELECT o.fact_rental_key,
        o.amount,
        o.rental_date,
        r.rental_id,
        o.return_date,
        o.return_date_key,
        i.inventory_id,
        i.film_id,
        p.payment_id,
        c.first_name,
        c.last_name,
        rd.date_key
    FROM orders_silver_tempview AS o
    INNER JOIN sakila_dlh.dim_customer AS c
    ON c.customer_key = o.customer_key
    INNER JOIN sakila_dlh.dim_inventory AS i
    ON i.inventory_id = o.inventory_key
    INNER JOIN sakila_dlh.dim_payment AS p
    ON p.payment_id = o.payment_key
    INNER JOIN sakila_dlh.dim_rental AS r
    ON r.inventory_id = i.inventory_id
    LEFT OUTER JOIN sakila_dlh.dim_date AS rd
    ON rd.date_key = o.rental_date_key
)

(spark.table("fact_orders_silver_tempview")
      .writeStream
      .format("delta")
      .option("checkpointLocation", f"{orders_output_silver}/_checkpoint")
      .outputMode("append")
      .table("fact_orders_silver"))

# Commented out IPython magic to ensure Python compatibility.
# %sql
SELECT * FROM orders_silver_tempview

"""###7.3. Gold Table: Perform Aggregations
####Create a new Gold table using the CTAS approach. The table should include the total amount (total list price) of the purchase orders placed per Supplier for each Product. Include the Suppliers' Company Name, and the Product Name.
"""

# Commented out IPython magic to ensure Python compatibility.
# %sql
-- Author a query that returns the Total Amount grouped by Rental and Customer and sorted by Total Amount descending.

CREATE OR REPLACE TABLE sakila_dlh.rentals_per_customer_gold AS (
    SELECT rental_key AS rental,
     customer_key AS customer,
     SUM(amount) AS TotalAmount
  FROM sakila_dlh.fact_orders_bronze
  GROUP BY customer, rental
  ORDER BY TotalAmount DESC
);

SELECT * FROM sakila_dlh.rentals_per_customer_gold;