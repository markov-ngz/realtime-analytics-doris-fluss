package ngz.markov.fixtures.dummy;

import net.datafaker.Faker;
import ngz.markov.fixtures.Generator;

public class CustomerGenerator implements Generator<Customer> {

    private static final int MIN_BRAND_ID = 1;
    private static final int MAX_BRAND_ID = 2;
    private static final int CUSTOMER_ID_SPACE = 50000;

    private final Faker faker;

    public CustomerGenerator() {
        this.faker = new Faker();
    }

    @Override
    public Customer generate() {

        return Customer.builder()
                .customerId(generateCustomerId())
                .brandId(generateBrandId())
                .build();
    }

    /**
     * Generates a brand ID from the configured inclusive range.
     */
    public int generateBrandId() {
        return faker.number().numberBetween(
                MIN_BRAND_ID, MAX_BRAND_ID + 1
        );
    }

    public String generateCustomerId() {
        return String.valueOf(
                faker.number().numberBetween(1, CUSTOMER_ID_SPACE + 1)
        );
    }
}
