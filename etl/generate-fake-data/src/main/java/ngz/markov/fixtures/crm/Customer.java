package ngz.markov.fixtures.crm;

import lombok.Builder;
import lombok.Data;

@Data
@Builder
public class Customer {

    private String  customerId;
    private int     brandId;
    private String  email;
    private String  phone;
    private String  segment;
    private String  acquisitionChannel;
    private String  country;
    private boolean optIn;
    private long    lastPurchaseTs;   // epoch seconds
    private long    writtenAt ;
}