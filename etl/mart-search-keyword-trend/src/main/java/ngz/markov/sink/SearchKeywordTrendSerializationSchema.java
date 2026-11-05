package ngz.markov.sink;

import ngz.markov.model.SearchKeywordTrend;
import org.apache.fluss.flink.row.OperationType;
import org.apache.fluss.flink.row.RowWithOp;
import org.apache.fluss.flink.sink.serializer.FlussSerializationSchema;
import org.apache.fluss.row.BinaryString;
import org.apache.fluss.row.Decimal;
import org.apache.fluss.row.GenericRow;
import org.apache.fluss.row.TimestampNtz;

public class SearchKeywordTrendSerializationSchema
        implements FlussSerializationSchema<SearchKeywordTrend> {

    private static final long serialVersionUID = 1L;

    @Override
    public void open(InitializationContext context) throws Exception {}

    @Override
    public RowWithOp serialize(SearchKeywordTrend value) throws Exception {

        GenericRow row = new GenericRow(19);

        // 0 - 1: Window timestamps
        row.setField(0, value.getWindowStart() != null
                ? TimestampNtz.fromMillis(value.getWindowStart().getTime()) : null);

        row.setField(1, value.getWindowEnd() != null
                ? TimestampNtz.fromMillis(value.getWindowEnd().getTime()) : null);

        // 2 - 4: Keyword dimensions
        row.setField(2, value.getSearchKeyword() != null
                ? BinaryString.fromString(value.getSearchKeyword()) : null);

        row.setField(3, value.getNormalizedKeyword() != null
                ? BinaryString.fromString(value.getNormalizedKeyword()) : null);

        row.setField(4, value.getPrimaryRegion() != null
                ? BinaryString.fromString(value.getPrimaryRegion()) : null);

        // 5 - 7: Volume & intent metrics
        row.setField(5, value.getSearchCount());
        row.setField(6, value.getUniqueUserCount());
        row.setField(7, value.getAvgSearchesPerUser());

        // 8 - 9: Channel & device dimensions
        row.setField(8, value.getDominantChannel() != null
                ? BinaryString.fromString(value.getDominantChannel()) : null);

        row.setField(9, value.getDominantDevice() != null
                ? BinaryString.fromString(value.getDominantDevice()) : null);

        // 10 - 14: Financial & conversion metrics
        row.setField(10, value.getPreOrderSearchCount());

        row.setField(11, value.getAttributedRevenue() != null
                ? Decimal.fromBigDecimal(value.getAttributedRevenue(), 18, 2) : null);

        row.setField(12, value.getConversionProxyRate());
        row.setField(13, value.getPostOrderSearchCount());

        row.setField(14, value.getPostOrderRevenue() != null
                ? Decimal.fromBigDecimal(value.getPostOrderRevenue(), 18, 2) : null);

        // 15 - 17: Trend velocity & spike metrics
        row.setField(15, value.getBaselineSearchCount());
        row.setField(16, value.getSearchCountDelta());
        row.setField(17, value.getTrendVelocityScore());

        // 18: Metadata timestamp
        row.setField(18, value.getUpdatedAt() != null
                ? TimestampNtz.fromMillis(value.getUpdatedAt().getTime()) : null);

        return new RowWithOp(row, OperationType.UPSERT);
    }
}
