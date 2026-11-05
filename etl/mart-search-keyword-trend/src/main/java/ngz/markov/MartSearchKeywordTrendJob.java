package ngz.markov;

import ngz.markov.model.EnrichedSearchEvent;
import ngz.markov.model.SearchKeywordTrend;
import ngz.markov.model.SaleOrder;
import ngz.markov.model.SearchEvent;
import ngz.markov.operator.RevenueAttributionJoinFunction;
import ngz.markov.operator.SearchEventAggregateFunction;
import ngz.markov.operator.SearchEventWindowFunction;
import ngz.markov.operator.TrendVelocityProcessFunction;
import ngz.markov.model.WindowedSearchMetrics;
import ngz.markov.sink.SearchKeywordTrendSink;
import ngz.markov.source.SaleOrderSource;
import ngz.markov.source.SearchEventSource;
import ngz.markov.util.KeywordNormalizer;
import org.apache.flink.api.common.eventtime.WatermarkStrategy;
import org.apache.flink.streaming.api.datastream.DataStream;
import org.apache.flink.streaming.api.environment.StreamExecutionEnvironment;
import org.apache.flink.streaming.api.windowing.assigners.SlidingEventTimeWindows;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;


public class MartSearchKeywordTrendJob {

	private static final Logger LOG = LoggerFactory.getLogger(MartSearchKeywordTrendJob.class);


	public static void main(String[] args) throws Exception {
		// Sets up the execution environment, which is the main entry point
		final StreamExecutionEnvironment env = StreamExecutionEnvironment.getExecutionEnvironment();
		JobConfig jobConfig = JobConfig.fromArgs(args);


		// Step 1 :  Sources
		DataStream<SearchEvent> searchEvents = env
				.fromSource(
						SearchEventSource.build(
								jobConfig.getBootstrapServers(),
								jobConfig.getSearchEventDatabase(),
								jobConfig.getSearchEventTable(),
								jobConfig.getFlussConfig()
								),
						WatermarkStrategy
								.<SearchEvent>forBoundedOutOfOrderness(jobConfig.getOutOfOrdernessBound())
								// event_time is epoch-ms → convert to epoch-ms for Flink
								.withTimestampAssigner(
										(event, recordTimestamp) -> event.getEventTime()
								)
								.withIdleness(jobConfig.getSearchEventIdleTimeout()),
						"search_event_source"
				)
				.name("search_event_source");
		DataStream<SaleOrder> saleOrders = env
				.fromSource(
						SaleOrderSource.build(
								jobConfig.getBootstrapServers(),
								jobConfig.getSaleOrderDatabase(),
								jobConfig.getSaleOrderTable(),
								jobConfig.getFlussConfig()
						),
						WatermarkStrategy
								.<SaleOrder>forBoundedOutOfOrderness(jobConfig.getOutOfOrdernessBound())
								.withTimestampAssigner(
										(order, recordTimestamp) -> order.getOrderTime()
								)
								.withIdleness(jobConfig.getSaleOrderIdleTimeout())
								,
						"sale_order_source"
				)
				.name("sale_order_source");


		// Step 2 revenue attribution join (raw events, keyed by sessionId)
		DataStream<EnrichedSearchEvent> enrichedEvents = searchEvents
				.filter(e -> e.getSearchText() != null && !e.getSearchText().isBlank())
				.name("filter_blank_keywords")
				.keyBy(SearchEvent::getSessionId)
				.connect(saleOrders.keyBy(SaleOrder::getSessionId))
				.process(new RevenueAttributionJoinFunction())
				.name("revenue_attribution_join");

		// Step 3: HOP window aggregation per normalizedKeyword
		DataStream<WindowedSearchMetrics> windowedMetrics = enrichedEvents
				.keyBy(e -> KeywordNormalizer.normalize(e.getSearchText()))
				.window(SlidingEventTimeWindows.of(jobConfig.getHopWindowSize(), jobConfig.getHopWindowSlide()))
				.aggregate(
						new SearchEventAggregateFunction(),
						new SearchEventWindowFunction()
				)
				.name("hop_window_aggregation");

		// Step 4: Trend Velocity
		DataStream<SearchKeywordTrend> searchKeywordTrend = windowedMetrics
				.keyBy(WindowedSearchMetrics::getNormalizedKeyword)
				.process(new TrendVelocityProcessFunction())
				.name("trend_velocity");

		// Final : Sink to Fluss
		searchKeywordTrend.sinkTo(SearchKeywordTrendSink.build(
						jobConfig.getBootstrapServers(),
						jobConfig.getSearchTrendsDatabase(),
						jobConfig.getSearchTrendsTable(),
				jobConfig.getFlussConfig()
				))
				.name("fluss_search_keyword_trend_sink");

		env.execute("search-keyword-trend-job");

	}
}
