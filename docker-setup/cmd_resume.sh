docker start \
  taskmanager-1 \
  jobmanager-1 \
  fluss-tablet-1 \
  fluss-gateway-1 \
  fluss-coordinator-1 \
  zookeeper-1 \
  rustfs-1 \
  be-1 \
  fe-1

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