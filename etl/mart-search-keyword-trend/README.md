# Mart Search Keyword Trend Job

Flink transformation job reading search event & sale order to produce the mart search-keyword-trend.

## Mart specification

**Key:** `window_start` , `window_end` , `search_keyword`

**Field description:** 

| Column                  | description                                                                                      | compute rule                                                                                                                                                                                                                                                                                                                            | datatype |
 |-------------------------|--------------------------------------------------------------------------------------------------|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------|---|
| window_start            | Window start time                                                                                | 1 hour window sliding by 5 minutes  ( should be able to be changed at job config level )                                                                                                                                                                                                                                                | TIMESTAMP(3) |
| window_end              | Window end time                                                                                  |                                                                                                                                                                                                                                                                                                                                         | TIMESTAMP(3) |
| search_keyword          | Raw text typed into the main search bar of the site ( eg. [JD tool bar ](https://global.jd.com/) | `search_event.search_text`                                                                                                                                                                                                                                                                                                              | STRING |
| normalized_keyword      | Search Keyword which was cleaned by the following rules                                          | 1. null / blank → empty string (caller should pre-filter these) <br> 2. Unicode NFKC normalization (handles full-width chars, ligatures)  <br> 3. Lowercase  <br> 4. Strip leading/trailing whitespace  <br>5. Collapse internal whitespace to single space  <br>6. Remove punctuation except hyphen (preserves "t-shirt", "self-care") | STRING |
| primary_region          | Identifies if trend is region-specific (e.g., Mazowieckie)                                       |                                                                                                                                                                                                                                                                                                                                         | STRING |
| search_count            | Number of times a normalized keyword has been typed in the search bar                            |                                                                                                                                                                                                                                                                                                                                         | BIGINT |
| unique_user_count       | number of distinct user having search                                                            | use `search_event.user id` without null                                                                                                                                                                                                                                                                                                 | BIGINT |
| avg_searches_per_user   | High ratio indicates user friction / difficulty finding the item                                 | use `search_event.user id` without null                                                                                                                                                                                                                                                                                                 | DOUBLE |
| dominant_channel        | e.g., 'paid', 'organic' - tells marketing if ads drove it                                        | `search_event.channel`                                                                                                                                                                                                                                                                                                                  | STRING |
| dominant_device         | e.g., 'mobile' vs 'desktop'                                                                      | `search_event.device_type`                                                                                                                                                                                                                                                                                                              | STRING |
| pre_order_search_count  | Searches occurring up to 60 minutes before an order within the same session                      |                                                                                                                                                                                                                                                                                                                                         | BIGINT |
| attributed_revenue      | Revenue attributed to pre-order searches                                                         | sum of `sale_order.revenue` with the system currency (PLN)                                                                                                                                                                                                                                                                              | DECIMAL(18, 2) |
| conversion_proxy_rate   | Ratio of searches that led to an order_id within the session                                     |                                                                                                                                                                                                                                                                                                                                         | DOUBLE |
| post_order_search_count | Searches occurring up to 60 minutes after an order within the same session                       |                                                                                                                                                                                                                                                                                                                                         | BIGINT |
| post_order_revenue      | Revenue (if any) tied to post-order behavior                                                     | sum of `sale_order.revenue` with the system currency (PLN)                                                                                                                                                                                                                                                                              | DECIMAL(18, 2) |
| baseline_search_count   | Average search count over the past 24 hours                                                      |                                                                                                                                                                                                                                                                                                                                         | BIGINT |
| search_count_delta      | Absolute change vs baseline                                                                      |                                                                                                                                                                                                                                                                                                                                         | BIGINT |
| trend_velocity_score    | Rate of acceleration (Z-score or multiplier vs baseline)                                         |                                                                                                                                                                                                                                                                                                                                         | DOUBLE |
| updated_at              | Processing time of the row ( not the time it was tiered to datalake )                            |                                                                                                                                                                                                                                                                                                                                         | TIMESTAMP(3) |



## Usage

The following arguments are supported :

### Fluss

**Generic options**<br>

- `fluss.bootstrap.servers` — Fluss cluster bootstrap servers.
- Any argument prefixed with `fluss.client.` — forwarded to the Fluss client configuration with the prefix stripped (e.g. `fluss.client.foo=bar` becomes `foo=bar`).

**source : sale order**<br>
- `fluss.source.sale-order.database` — Source database for sale orders.
- `fluss.source.sale-order.table` — Source table for sale orders.

**source : search event**<br>
- `fluss.source.search-event.database` — Source database for search events.
- `fluss.source.search-event.table` — Source table for search events.

**sink : search-trends**<br>
- `fluss.sink.search-trends.database` — Target database for the search-keyword-trend mart.
- `fluss.sink.search-trends.table` — Target table for the search-keyword-trend mart.

NOTE : aws credentials are needed to be specified to read/write to s3 like object ( rustfs in this project )

### Transformation options

- `window.out-of-orderness-bound` — Allowed out-of-orderness bound for event time. Default: `5s`.
- `window.hop-size` — Size of the hopping window. Default: `1h`.
- `window.hop-slide` — Slide interval of the hopping window. Default: `5min`.

### Source idleness timeouts

- `source.search-event.idle-timeout` — Idle timeout for the search-event source. Default: `1min`.
- `source.sale-order.idle-timeout` — Idle timeout for the sale-order source. Default: `5min`.


## Transformation steps

1. Read Sources : SaleOrder & SearchEvent from dedicated Fluss Table
2. Filter by removing SearchEvent whose `searchText` field is null or blank
3. Join SaleOrder & SearchEvent on sessionId to produce an EnrichedSearchEvent with either pre or post sale search information :
    2 list states : SaleOrder & searchEvent with a 60 minutes retention
    Post Sale search An order arrives if no search event is tied in the state of searchevent => 
4. Window aggregation for normalizedKeywords
5. Window Trend velocity comparison to baseline
6. Sink to Fluss table

schema picture de la suite des transfos / operator

## Flink configuration
Description of flink key feature implementation

**Watermark**: 
reminder :essence of time for a flink job, if watermark do not advance then time is stopped and no new epoch is created.
implementation:
- `fluss_source.search_events` : based on event_time
- `fluss_source.sale_order` : based on order_time ( ingestion time into the system not the sale's )
- **out of orderness bound** : 5 seconds , no monotonous timestamp as time is not crucial here ? 

**Idleness** 
reminder :defines if the source is stale , meaning that there is no need to wait for new events . why defining it here ? 
implementation :
- `fluss_source.search_events` : 1 minute
- `fluss_source.sale_order` : 5 minutes ( slow changes )

**Watermark Alignment**
reminder : for two streams joined on a timestamp, it is required to align their watermark as they need to be from the same epoch  so they can be joined.
implementation : the join is based on sessionId hence it is not needed

**OffsetInitializer**
FlussSource offers 4 options : `earliest` , `latest` , `full` , `timestamp`
Choice `fùll`: As it is a development job with fake data, thefull snapshot on the table upon first startup allows to produce immediate result with prepared data without having to setup generator job at the same time

**Backpressure:**
Should there be any ? If the window aggregation is too slow and massive load of events happens at the source ?
Then increase the parrallelism ? 

**Restart Strategy:** 
`off` : for the same reason as the offsetinitializer, this is fake job data hence, when it breaks it is often because of misconfig or mistakes hence no restart is expected to investigate.

**Checkpointing:**
- `retained checkpoint` : delete on cancellation 
- `savepoints-dir`: s3://flink/savepoints , save on remote 
- `interval`: "300000" ,  every 5 min no real sla or system constraint  [doc](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/ops/production_ready/#choose-the-right-checkpoint-interval)
- `max-concurrent-checkpoints`: "1" , how can multiple checkpoint occurs  ? Does it mean problems or too heavy charge around checkpoints so that they overlap ? 
- `min-pause`: default 0ms, 
- `buffer debloating` : not configured , not needed to have smaller checkpoints by limiting in flight data
- `mode`: EXACTLY_ONCE , no opinion but wondering would accumulator and state breaks if AT_LEAST_ONCE is dealt ? With higher scale it could speed up 
- `retained checkpoints` : only one as default, no usage there 
- `incremental`: false ,  default , not needed as state is not massive so it would only be a loss of performance for recovery time

Reminders : 
- checkpoint vs savepoints : 
- savepoints : 
    - canonical : unified format between all state backend ( possible to save asrocksdb and restore as forst )
    - native : specific to state backend
[doc](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/ops/state/savepoints/#savepoint-format)
- checkpoints :
    - barrier : checkpoint record's delimitation
    - aligned /  unaligned : if checkpointing takes too much time ( backpressure case ) , unaligned checkpoint breaks the barrier to also checkpoint in flight data
[doc](https://nightlies.apache.org/flink/flink-docs-release-2.3/docs/concepts/stateful-stream-processing/#barriers)
    - incremental : record the changes that happened since the latest completed checkpoint

**State:**
- `backend-type`: rocksdb embedded , if too big then could forst for disagregate state management be a better choice ? 
- `changelog enabled` : false,  not needed as checkpoint duration is not a problem there 

? state evolution ? 
If the event of SaleOrder or SearchEvent were to be changed , would it break the state and how to migrate it ? 

**Logging:** 
log4j default with console append and format `%d{HH:mm:ss,SSS} %-5p %-60c %x - %m%n`

**Custom Metrics:** 
`/`



