package ngz.markov.fixtures.ecommerce;

import net.datafaker.Faker;
import ngz.markov.fixtures.Generator;

import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

public class SearchEventGenerator implements Generator<SearchEvent> {

    private final Faker faker;

    // List of 15 clothes ecommerce words
    private static final List<String> CLOTHES_WORDS = List.of(
            "t-shirt", "jeans", "jacket", "hoodie", "sneakers",
            "sweater", "dress", "shorts", "coat", "skirt",
            "blazer", "socks", "scarf", "boots", "cap"
    );

    // 3 distinct Polish regions (Voivodeships)
    private static final List<String> POLISH_REGIONS = List.of(
            "Mazowieckie", "Małopolskie", "Wielkopolskie"
    );

    public SearchEventGenerator() {
        this.faker = new Faker();
    }

    @Override
    public SearchEvent generate() {
        // Gaussian distribution mapped to indices 0 to 14 (mean = 7, std dev = 2.0)
        double gaussian = ThreadLocalRandom.current().nextGaussian();;
        int index = (int) Math.round(7.0 + (gaussian * 2.0));
        // Clamp index between 0 and 14 to prevent OutOfBounds
        index = Math.clamp(index, 0, CLOTHES_WORDS.size() - 1);
        String skewedSearchText = CLOTHES_WORDS.get(index);

        long currentTime = System.currentTimeMillis();
        long randomEventTime = currentTime - faker.number().numberBetween(0, 3600000L); // within the last hour

        return SearchEvent.builder()
                .eventId(faker.internet().uuid())
                .eventType("search")
                .eventTime(randomEventTime)
                .userId(String.valueOf(faker.number().numberBetween(1, 101))) // between 1 and 100
                .sessionId("0000-000-0000") // hard coded value to match with sale order
                .deviceType(faker.options().option("mobile", "desktop", "tablet"))
                .channel(faker.options().option("organic", "paid", "social", "direct"))
                .region(faker.options().option(POLISH_REGIONS.toArray(new String[0])))
                .searchId(faker.internet().uuid())
                .searchText(skewedSearchText)

                // Product context -> null per constraints
                .skuId(null)
                .productId(null)
                .categoryId(null)
                .brandId(null)
                .merchantId(null)

                // A/B experiment context -> null per constraints
                .experimentId(null)
                .experimentVariant(null)

                // Event-specific attributes -> null per constraints
                .searchRank(null)
                .quantity(null)
                .orderId(null)
                .revenue(null)

                // Ingestion metadata
                .sourceSystem("web_frontend")
                .ingestionTime(currentTime)
                .build();
    }
}