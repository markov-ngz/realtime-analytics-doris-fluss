package ngz.markov.source;

import ngz.markov.model.SearchEvent;
import org.apache.fluss.flink.source.deserializer.FlussDeserializationSchema;
import org.apache.fluss.record.LogRecord;
import org.apache.fluss.row.InternalRow;
import org.apache.fluss.types.RowType;
import org.apache.flink.api.common.typeinfo.TypeInformation;

import java.io.Serial;
import java.math.BigDecimal;

public class SearchEventDeserializationSchema implements FlussDeserializationSchema<SearchEvent> {

    @Serial
    private static final long serialVersionUID = 1L;

    @Override
    public void open(InitializationContext context) {
        // no-op for now
    }

    @Override
    public SearchEvent deserialize(LogRecord record) throws Exception {
        InternalRow row = record.getRow();

        SearchEvent event = new SearchEvent();

        event.setEventId(row.isNullAt(0) ? null : row.getString(0).toString());
        event.setEventType(row.isNullAt(1) ? null : row.getString(1).toString());
        event.setEventTime(row.getLong(2));
        event.setUserId(row.isNullAt(3) ? null : row.getString(3).toString());
        event.setSessionId(row.isNullAt(4) ? null : row.getString(4).toString());
        event.setDeviceType(row.isNullAt(5) ? null : row.getString(5).toString());
        event.setChannel(row.isNullAt(6) ? null : row.getString(6).toString());
        event.setRegion(row.isNullAt(7) ? null : row.getString(7).toString());
        event.setSearchText(row.isNullAt(8) ? null : row.getString(8).toString());
        event.setOrderId(row.isNullAt(9) ? null : row.getString(9).toString());

        if (!row.isNullAt(10)) {
            event.setRevenue((BigDecimal) row.getDecimal(10, 18, 2).toBigDecimal());
        }

        return event;
    }

    @Override
    public TypeInformation<SearchEvent> getProducedType(RowType rowSchema) {
        return TypeInformation.of(SearchEvent.class);
    }
}
