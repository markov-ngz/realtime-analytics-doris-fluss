# Intro and Setup Guide

The following steps shows how to setup the project and run the jobs locally in three part :
- application packaging & dependency installation
- docker container launch
- data transformation jobs

**Prerequisites**<br>
To run the script the following is needed on the environment , version hinted are what was used at the time of project : 
- docker (29.9.1)
- openjdk ( 25.0.4.1 )
- maven (3.9.12)
- uv (0.12.13)

## Package app and prepare environment

### generate-fake-data

Flink Job to publish fake data to a specified sink. It is made on 3 components : 
- the event/pojo with its generator function
- a flink `DataGeneratorSource` to allow to control the rate and number of published events
- a sink to choose ( atm only fluss and fluss-gateway are available)

```shell
cd generate-fake-data
mvn package
```

### mart-search-keyword-trend

Flink transformation job reading search event & sale order to produce a search-keyword-trend.
```shell
cd mart-seach-keyword-trend
mvn package
```
Note : The mart produced is still a bit "raw" but it allows to externalize parameters and refine the query as the use case was clearly not precisely defined beforehand.

### send-sql-to-flink

Python tool to submit SQL file to Flink using the gateway. It allows to not open the  sql-client and automate basic table creation.

```shell
uv sync
```

### dashboard-search-keyword-trend

Streamlit multi page application to visualize result with 2 dashboards :
- search keyword trends 
- post purchase intent through the scope of search made after a sale  

```shell
uv sync
```

## Docker 

### Network
In order to ease the deployment of Doris, the FQDN mode is not setup and the be and fe identify themselves using static ip.
Hence we create a unique docker network with a specified cidr range.
Also all containers are in the same network it allows to use built in service discovery.
```shell
docker network create quickstart-fluss-doris --subnet 172.22.0.0/16
```

### Mounted volumes
Fluss, Flink & Doris requires multiple lib to placed under the classpath.

Here is the list of jar to use :
```
├── doris_plugins
│   └── fluss-fs-s3-1.0.0.jar
├── flink_catalog_store
│   └── fluss_paimon.yaml
├── flink_job
│   ├── fluss-flink-tiering-1.0.0.jar
│   ├── generate-fake-data-1.0.0.jar
│   └── mart-search-keyword-trend-1.0-SNAPSHOT.jar
├── flink_lib
│   ├── fluss-flink-2.3-1.0.0.jar
│   ├── fluss-fs-s3-1.0.0.jar
│   ├── fluss-lake-paimon-1.0.0.jar
│   ├── hadoop-mapreduce-client-core-3.5.0.jar
│   ├── paimon-bundle-2.0.0.jar
│   └── paimon-s3-2.0.0.jar
├── flink_plugins
│   └── flink-s3-fs-native
│       └── flink-s3-fs-native-2.3.0.jar
├── fluss_plugins
│   └── paimon
│       └── paimon-s3-2.0.0.jar
```

### Build Doris from source  (Optional)
As Doris 5.0.0 was still not available on October 2026, it was built from master branch 
using the script `build.sh` . It took 1 hour 20 minutes on a poor laptop.
Then the image needed to be built , so the output dir needs to be moved under the docker context.
```shell
build.sh

cd ~/doris/docker/runtime

mkdir -p fe/resource/amd64/apache-doris-5.0.0-main-bin-x64
mkdir -p be/resource/amd64/apache-doris-5.0.0-main-bin-x64
mkdir -p ms/resource/amd64/apache-doris-5.0.0-main-bin-x64

cp -r ../../output/fe fe/resource/amd64/apache-doris-5.0.0-main-bin-x64/fe
cp -r ../../output/be be/resource/amd64/apache-doris-5.0.0-main-bin-x64/be
cp -r ../../output/ms ms/resource/amd64/apache-doris-5.0.0-main-bin-x64/ms
```

Official guide at : https://doris.apache.org/community/source-install/compilation-with-docker"

### Run containers
```sh
# Rustfs
docker compose -f rustfs.docker-compose.yaml up -d
# Fluss Cluster
docker compose -f fluss.docker-compose.yaml up -d
# Flink session mode deployment
docker compose -f flink.docker-compose.yaml up -d
# Apache Doris integrated storage deployment
docker compose -f doris.docker-compose.yaml up -d
```

## Data transformations

### DDL 

Using the tool send_sql_to_flink ,activate the proper python env and run the following commands to submit sql statements to the Flink Gateway : 
```sh
uv run send-sql-to-flink --filepath ddl/1-staging.sql
uv run send-sql-to-flink --filepath ddl/3-mart.sql
```

Also Doris catalog needs to be setup by running an ephemeral mysql container connected to Doris cluster and execute a few statements. *
Alternatively it allows to check, all dependencies and connection are correctly setup. 
```shell
source docker-setup/open_doris_mysql_client.sh

# => execute doris_fluss_catalog.sql statements.
```

### Fluss Tiering Service
```sh
docker exec -it jobmanager-1 flink run -d \
  /opt/flink/usrlib/fluss-flink-tiering-1.0.0.jar \
    --fluss.bootstrap.servers fluss-coordinator:9123 \
    --datalake.format paimon \
    --datalake.paimon.metastore filesystem \
    --datalake.paimon.warehouse s3://datalake/paimon \
    --datalake.paimon.s3.endpoint http://rustfs:9000 \
    --datalake.paimon.s3.access.key rustfsadmin \
    --datalake.paimon.s3.secret.key rustfsadmin \
    --datalake.paimon.s3.path.style.access true
```

### Fake Raw data
```shell
# Search Events 
docker exec -it jobmanager-1 flink run -d \
  /opt/flink/usrlib/generate-fake-data-1.0.0.jar \
        --pipeline.name generate-fake-event \
        --event.class ngz.markov.fixtures.ecommerce.SearchEvent \
        --event.rate 1 \
        --sink.type fluss-gateway \
        --sink.fluss-gateway.gatewayurl http://fluss-gateway:8080 \
        --sink.fluss-gateway.clusterid default \
        --sink.fluss-gateway.database staging \
        --sink.fluss-gateway.table search_event \
        --sink.fluss-gateway.operation append
# Sale Orders 
docker exec -it jobmanager-1 flink run -d \
  /opt/flink/usrlib/generate-fake-data-1.0.0.jar \
        --pipeline.name generate-fake-event \
        --event.class ngz.markov.fixtures.ecommerce.SaleOrder \
        --event.rate 1 \
        --sink.type fluss-gateway \
        --sink.fluss-gateway.gatewayurl http://fluss-gateway:8080 \
        --sink.fluss-gateway.clusterid default \
        --sink.fluss-gateway.database staging \
        --sink.fluss-gateway.table sale_order \
        --sink.fluss-gateway.operation append

```

### Transformation Job

```shell
# Transformations
docker exec -it jobmanager-1 flink run -d \
  /opt/flink/usrlib/mart-search-keyword-trend-1.0-SNAPSHOT.jar \
  --fluss.bootstrap.servers fluss-coordinator:9123 \
  --fluss.source.sale-order.database staging \
  --fluss.source.sale-order.table sale_order \
  --fluss.source.search-event.database staging \
  --fluss.source.search-event.table search_event \
  --fluss.sink.search-trends.database mart \
  --fluss.sink.search-trends.table search_keyword_trend
```

## Visualization

Install dependencies and run the application
```shell
streamlit run src/dashboard-search-keyword-trend/
```
