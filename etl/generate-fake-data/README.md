# Fake Data Generator

Flink Job to publish fake data to a specified sink. 
It is made on 3 components :
- the event/pojo with its generator function
- a flink `DataGeneratorSource` to allow to control the rate and number of published events
- a sink to choose ( atm only fluss and fluss-gateway are available)

**Usage**

Package the application and run a flink job like the following: 
```sh
flink run -d \
  /opt/flink/usrlib/generate-fake-data-1.0.0.jar \
        # Full Class Name 
        --event.class ngz.markov.fixtures.ecommerce.SearchEvent \
        # Rate ( event number / sec ) 
        --event.rate 1 \
        # Specify count for finite stream
        --event.count 60  \
        # Sink choice
        --sink.type fluss-gateway \
        --sink.fluss-gateway.gatewayurl http://fluss-gateway:8080 \
        --sink.fluss-gateway.clusterid default \
        --sink.fluss-gateway.database staging \
        --sink.fluss-gateway.table search_event \
        --sink.fluss-gateway.operation append
```

**Available event class**<br>

The fake event are organized by "domain" in order to be able to inject generator into each other and correlate keys. 

CRM :
- ngz.markov.fixtures.crm.Customer : PII and basic infos 

ECOMMERCE
- ngz.markov.fixtures.ecommerce.SaleOrder : Order with revenue happening
- ngz.markov.fixtures.crm.SearchEvent : Event happening when a user uses a search bar.

DUMMY (for tests & development usage ):
- ngz.markov.fixtures.dummy.Customer : 2 field class used to test sink and check connectivity


The objective is to create a complete ecosystem with a lot of class to easily mock events and define a "business" logic.

**Available sinks**
- fluss : write directly to fluss table using the FlussSource.
- fluss-gateway (experimental): write to the gateway using the HttpSink. As Fluss gateway is still under development , endpoint and body might break for versions > 1.0.0

**Roadmap**
Future evolutions could be to :
- improve cli by using `apache-common-cli`
- better handle correlation ids for a domain unit so that cross domain jobs can be achieved
- produce static files like CSV or Iceberg to also generate fixtures for batch mode jobs.
- attach SQL table DDL to a POJO