package ngz.markov.sink.fluss.serializationschema;

import ngz.markov.fixtures.crm.Customer;
import org.apache.fluss.flink.row.OperationType;
import org.apache.fluss.flink.row.RowWithOp;
import org.apache.fluss.flink.sink.serializer.FlussSerializationSchema;
import org.apache.fluss.row.BinaryString;
import org.apache.fluss.row.GenericRow;

public class CustomerSerializationSchema implements FlussSerializationSchema<Customer>{

    @Override
    public void open(InitializationContext context) throws Exception {}

    @Override
    public RowWithOp serialize(Customer value) throws Exception {
        GenericRow row = new GenericRow(9);

        row.setField(0, BinaryString.fromString(value.getCustomerId()));
        row.setField(1, value.getBrandId());
        row.setField(2, BinaryString.fromString(value.getEmail()));
        row.setField(3, BinaryString.fromString(value.getPhone()));
        row.setField(4, BinaryString.fromString(value.getSegment()));
        row.setField(5, BinaryString.fromString(value.getAcquisitionChannel()));
        row.setField(6, BinaryString.fromString(value.getCountry()));
        row.setField(7, value.isOptIn());
        row.setField(8, value.getLastPurchaseTs());

        return new RowWithOp(row, OperationType.UPSERT);
    }
}