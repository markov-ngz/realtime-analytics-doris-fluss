package ngz.markov.fixtures.crm;

public enum AcquisitionChannel {

    SEO             ("Search Engine", "Organic"),
    PPC             ("Pay-Per-Click", "Paid"),
    SOCIAL_ORGANIC  ("Social Media",  "Organic"),
    SOCIAL_PAID     ("Social Ads",    "Paid"),
    REFERRAL        ("Referral",      "Organic"),
    DIRECT          ("Direct",        "Organic"),
    EMAIL           ("Email Campaign","Owned"),
    AFFILIATE       ("Affiliate",     "Paid");

    private final String label;
    private final String category; // e.g., Paid vs Organic

    AcquisitionChannel(String label, String category) {
        this.label = label;
        this.category = category;
    }

    public String getLabel()    { return label; }
    public String getCategory() { return category; }

    @Override
    public String toString() { return label; }
}