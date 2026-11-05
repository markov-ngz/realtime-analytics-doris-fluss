package ngz.markov.source;


import ngz.markov.model.SaleOrder;
import org.apache.fluss.flink.source.deserializer.FlussDeserializationSchema;
import org.apache.fluss.record.LogRecord;
import org.apache.fluss.row.InternalRow;
import org.apache.fluss.types.RowType;
import org.apache.flink.api.common.typeinfo.TypeInformation;

import java.math.BigDecimal;

/**
 * Deserializes a projected Fluss LogRecord into a {@link SaleOrder}.
 *
 * Column order MUST match the projection defined in {@link SaleOrderSource}:
 *   [0] order_id      STRING
 *   [1] order_status  STRING
 *   [2] order_time    BIGINT
 *   [3] session_id    STRING
 *   [4] revenue       DECIMAL
 */
public class SaleOrderDeserializationSchema implements FlussDeserializationSchema<SaleOrder> {

    private static final long serialVersionUID = 1L;

    @Override
    public void open(InitializationContext context) {
        // no-op for now
    }

    @Override
    public SaleOrder deserialize(LogRecord record) throws Exception {
        InternalRow row = record.getRow();

        SaleOrder order = new SaleOrder();

        order.setOrderId(row.isNullAt(0) ? null : row.getString(0).toString());
        order.setOrderStatus(row.isNullAt(1) ? null : row.getString(1).toString());
        order.setOrderTime(row.getLong(2));
        order.setSessionId(row.isNullAt(3) ? null : row.getString(3).toString());

        if (!row.isNullAt(4)) {
            order.setRevenue((BigDecimal) row.getDecimal(4, 18, 2).toBigDecimal());
        }

        return order;
    }

    @Override
    public TypeInformation<SaleOrder> getProducedType(RowType rowSchema) {
        return TypeInformation.of(SaleOrder.class);
    }
}
