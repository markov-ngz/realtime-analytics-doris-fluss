package ngz.markov.sink.fluss;

import org.apache.fluss.flink.sink.serializer.FlussSerializationSchema;

import java.util.HashMap;
import java.util.Map;
import java.util.Objects;
import java.util.function.Supplier;

public final class SerializationSchemaRegistry {

    private final Map<Class<?>, SchemaRegistration<?>> registrations =
            new HashMap<>();

    public <T> void register(
            Class<T> clazz,
            Supplier<? extends FlussSerializationSchema<T>> schemaFactory) {

        Objects.requireNonNull(clazz);
        Objects.requireNonNull(schemaFactory);

        if (registrations.containsKey(clazz)) {
            throw new IllegalArgumentException(
                    "Schema already registered for " + clazz.getName());
        }

        registrations.put(
                clazz,
                new SchemaRegistration<>(clazz, schemaFactory));
    }

    public <T> FlussSerializationSchema<T> get(Class<T> clazz) {
        SchemaRegistration<?> registration = registrations.get(clazz);

        if (registration == null) {
            throw new IllegalArgumentException(
                    "No serialization schema registered for "
                            + clazz.getName());
        }

        if (!registration.clazz().equals(clazz)) {
            throw new IllegalStateException("Schema registration mismatch");
        }

        return castSchema(registration);
    }

    @SuppressWarnings("unchecked")
    private static <T> FlussSerializationSchema<T> castSchema(
            SchemaRegistration<?> registration) {
        return (FlussSerializationSchema<T>) registration.factory().get();
    }

    private record SchemaRegistration<T>(
            Class<T> clazz,
            Supplier<? extends FlussSerializationSchema<T>> factory) {

        private FlussSerializationSchema<T> createFor(Class<?> requestedClass) {
            if (!clazz.equals(requestedClass)) {
                throw new IllegalArgumentException(
                        "Schema type mismatch: " + requestedClass.getName());
            }

            return factory.get();
        }
    }
}