package ngz.markov.fixtures.crm;

import ngz.markov.fixtures.Generator;

import java.time.Instant;
import java.time.temporal.ChronoUnit;
import java.util.ArrayList;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Set;
import java.util.HashSet;

import net.datafaker.Faker;

public class CustomerGenerator implements Generator<Customer> {

    private static final String[] COUNTRIES = {
            "FR", "ES", "BE", "CH", "IT"
    };

    // Configure these IDs to match your application's brand catalog.
    private static final int MIN_BRAND_ID = 1;
    private static final int MAX_BRAND_ID = 2;

    private static final int CUSTOMER_ID_SPACE = 20;

    private static final Map<String, Faker> FAKER_BY_COUNTRY = Map.of(
            "FR", new Faker(Locale.forLanguageTag("fr-FR")),
            "ES", new Faker(Locale.forLanguageTag("es-ES")),
            "BE", new Faker(Locale.forLanguageTag("fr-BE")),
            "CH", new Faker(Locale.forLanguageTag("de-CH")),
            "IT", new Faker(Locale.forLanguageTag("it-IT"))
    );

    private final Faker faker;

    public CustomerGenerator() {
        this.faker = new Faker();
    }

    @Override
    public Customer generate() {
        String country = faker.options().option(COUNTRIES);
        Faker local = FAKER_BY_COUNTRY.get(country);

        Segment segment = faker.options().option(Segment.class);
        AcquisitionChannel acquisitionChannel =
                faker.options().option(AcquisitionChannel.class);

        int brandId = generateBrandId();

        return Customer.builder()
                .customerId(generateCustomerId())
                .brandId(brandId)
                .email(local.internet().emailAddress())
                .phone(local.phoneNumber().phoneNumber())
                .segment(segment.getLabel())
                .lastPurchaseTs(randomRecentEpochSeconds(segment))
                .country(country)
                .optIn(faker.bool().bool())
                .acquisitionChannel(acquisitionChannel.getLabel())
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

    public List<Customer> generateBatch(int count) {
        if (count < 0) {
            throw new IllegalArgumentException("count must be >= 0");
        }

        int maxUniqueKeys =
                CUSTOMER_ID_SPACE * (MAX_BRAND_ID - MIN_BRAND_ID + 1);

        if (count > maxUniqueKeys) {
            throw new IllegalArgumentException(
                    "Requested " + count + " customers, but only "
                            + maxUniqueKeys + " unique (customerId, brandId) pairs "
                            + "are available with the current configuration."
            );
        }

        List<Customer> batch = new ArrayList<>(count);
        Set<String> generatedKeys = new HashSet<>();

        while (batch.size() < count) {
            Customer customer = generate();
            String key = customer.getCustomerId()
                    + ":" + customer.getBrandId();

            if (generatedKeys.add(key)) {
                batch.add(customer);
            }
        }

        return batch;
    }

    public String generateCustomerId() {
        return String.valueOf(
                faker.number().numberBetween(1, CUSTOMER_ID_SPACE + 1)
        );
    }

    private long randomRecentEpochSeconds(Segment segment) {
        int minDaysAgo;
        int maxDaysAgo = switch (segment) {
            case CHURNED -> {
                minDaysAgo = 180;
                yield 365;
            }
            case AT_RISK -> {
                minDaysAgo = 60;
                yield 180;
            }
            case NEW -> {
                minDaysAgo = 0;
                yield 30;
            }
            default -> {
                minDaysAgo = 1;
                yield 90;
            }
        };

        Instant now = Instant.now();
        Instant from = now.minus(maxDaysAgo, ChronoUnit.DAYS);
        Instant to = now.minus(minDaysAgo, ChronoUnit.DAYS);

        long rangeSeconds = to.getEpochSecond() - from.getEpochSecond();

        return from.getEpochSecond()
                + (long) (Math.random() * (rangeSeconds + 1));
    }
}
