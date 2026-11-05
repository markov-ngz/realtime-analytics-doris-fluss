package ngz.markov.fixtures.ecommerce;

import java.math.BigDecimal;
import java.math.RoundingMode;
import java.util.List;
import java.util.concurrent.ThreadLocalRandom;

import net.datafaker.Faker;
import ngz.markov.fixtures.Generator;

public class SaleOrderGenerator implements Generator<SaleOrder> {

    private final Faker faker;

    // 3 distinct Polish regions (matching SearchEventGenerator)
    private static final List<String> POLISH_REGIONS = List.of(
            "Mazowieckie", "Małopolskie", "Wielkopolskie"
    );

    // Order statuses
    private static final List<String> ORDER_STATUSES = List.of(
            "COMPLETED", "PENDING", "CANCELLED"
    );

    public SaleOrderGenerator() {
        this.faker = new Faker();
    }

    @Override
    public SaleOrder generate() {
        long currentTime = System.currentTimeMillis();
        // Orders happen around the current time or slightly in the past (within the last hour)
        long randomOrderTime = currentTime - faker.number().numberBetween(0, 3600000L);

        int items = faker.number().numberBetween(1, 5);
        // Generate a random revenue between 30 and 600 PLN based on item count
        double rawRevenue = items * ThreadLocalRandom.current().nextDouble(30.0, 150.0);
        BigDecimal revenue = BigDecimal.valueOf(rawRevenue).setScale(2, RoundingMode.HALF_UP);

        return SaleOrder.builder()
                .orderId(faker.internet().uuid())
                .orderStatus(faker.options().option(ORDER_STATUSES.toArray(new String[0])))
                .orderTime(randomOrderTime)
                .userId(String.valueOf(faker.number().numberBetween(1, 11))) // 1 to 10, 10 % of searches
                .sessionId("0000-000-0000") // hard coded value to match with sale order
                .deviceType(faker.options().option("mobile", "desktop", "tablet"))
                .channel(faker.options().option("organic", "paid", "social", "direct"))
                .region(faker.options().option(POLISH_REGIONS.toArray(new String[0])))
                .totalItems(items)
                .revenue(revenue)
                .currency("PLN")
                .sourceSystem("checkout_service")
                .ingestionTime(currentTime)
                .build();
    }
}