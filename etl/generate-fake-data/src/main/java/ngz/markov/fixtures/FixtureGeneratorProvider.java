package ngz.markov.fixtures;

import ngz.markov.fixtures.crm.Customer;
import ngz.markov.fixtures.crm.CustomerGenerator;
import ngz.markov.fixtures.ecommerce.SaleOrder;
import ngz.markov.fixtures.ecommerce.SaleOrderGenerator;
import ngz.markov.fixtures.ecommerce.SearchEvent;
import ngz.markov.fixtures.ecommerce.SearchEventGenerator;

import java.util.HashMap;
import java.util.Map;
import java.util.function.Supplier;

public class FixtureGeneratorProvider {

    private static final Map<Class<?>, Supplier<? extends Generator<?>>> REGISTRY =
            new HashMap<>();

    static {
        REGISTRY.put(Customer.class, CustomerGenerator::new);
        REGISTRY.put(ngz.markov.fixtures.dummy.Customer.class, ngz.markov.fixtures.dummy.CustomerGenerator::new);
        REGISTRY.put(SearchEvent.class, SearchEventGenerator::new);
        REGISTRY.put(SaleOrder.class, SaleOrderGenerator::new);
    }

    private FixtureGeneratorProvider() {
    }

    public static <T> Generator<T> getGenerator(Class<T> clazz) {
        Supplier<? extends Generator<?>> supplier = REGISTRY.get(clazz);

        if (supplier == null) {
            throw new IllegalArgumentException(
                    "No generator registered for " + clazz.getName());
        }

        return (Generator<T>) supplier.get();
    }
}