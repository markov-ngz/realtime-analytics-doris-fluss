CREATE CATALOG fluss_paimon PROPERTIES (
    'type' = 'fluss',
    -- Fluss Properties
    'fluss.bootstrap.servers' = 'fluss-coordinator:9123',
    'fluss.client.fs.s3.access.key'        = 'rustfsadmin',
    'fluss.client.fs.s3.secret.key'        = 'rustfsadmin',
    'fluss.client.fs.s3.endpoint'          = 'http://rustfs:9000',
    'fluss.client.fs.s3.region'            = 'eu-north-1',
    'fluss.client.fs.s3.path-style-access' = 'true',

    -- Lake Properties
    'fluss.lake.paimon.warehouse'          = 's3://datalake/paimon',
    'fluss.lake.paimon.metastore'          = 'filesystem',
    'fluss.lake.paimon.s3.endpoint'        = 'http://rustfs:9000',
    'fluss.lake.paimon.s3.access-key'      = 'rustfsadmin',
    'fluss.lake.paimon.s3.secret-key'      = 'rustfsadmin',
    'fluss.lake.paimon.s3.region'          = 'eu-north-1',
    -- Common configs
    'use_path_style' = 'true' -- s3 rustfs
);


-- not enabled at time of the demo ( PR was still under development )
-- SET GLOBAL enable_jni_heap_admission = true; -- avoid oom for big tables

SWITCH fluss_paimon;

SHOW DATABASES ;

USE mart ;

SHOW TABLES ;

SELECT *
FROM mart.search_keyword_trend
LIMIT 10
;