USE CATALOG fluss_paimon ;

USE staging ;


SET 'execution.runtime-mode' = 'batch';
SET 'sql-client.execution.result-mode' = 'tableau';

SELECT count(*) FROM staging.search_event;