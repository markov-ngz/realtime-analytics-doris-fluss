package ngz.markov.model;

import lombok.Data;
import lombok.ToString;
import java.io.Serial;
import java.io.Serializable;
import java.math.BigDecimal;

import lombok.Data;
import lombok.ToString;
import java.io.Serial;
import java.io.Serializable;
import java.math.BigDecimal;

@Data
@ToString
public class EnrichedSearchEvent implements Serializable {

    @Serial
    private static final long serialVersionUID = 1L;

    private String eventId;
    private String eventType;
    private long eventTime;       // epoch-ms — used for watermark

    private String userId;
    private String sessionId;
    private String deviceType;
    private String channel;
    private String region;

    private String searchText;    // raw keyword to normalize + aggregate

    private String orderId;       // non-null when matched with an order
    private BigDecimal revenue;   // non-null for pre-order attributed searches
    private String searchType;    // "PRE_ORDER", "POST_ORDER", or "UNATTRIBUTED"
}