package ngz.markov.fixtures.crm;

public enum Segment {

    PREMIUM    ("Premium",     500, 5_000),
    LOYAL      ("Loyal",       100,   500),
    NEW        ("New",           0,   100),
    AT_RISK    ("At-Risk",      50,   300),
    CHURNED    ("Churned",       0,     0),
    OCCASIONAL ("Occasional",   20,   150);

    private final String label;
    private final int    minSpend;   // EUR / month
    private final int    maxSpend;

    Segment(String label, int minSpend, int maxSpend) {
        this.label    = label;
        this.minSpend = minSpend;
        this.maxSpend = maxSpend;
    }

    public String getLabel()    { return label; }
    public int    getMinSpend() { return minSpend; }
    public int    getMaxSpend() { return maxSpend; }

    /** Convenience: returns the label, which is stored in the Flink table. */
    @Override
    public String toString() { return label; }
}