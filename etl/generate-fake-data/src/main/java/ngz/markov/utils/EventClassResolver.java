package ngz.markov.utils;

public final class EventClassResolver {

    private EventClassResolver() {
    }

    public static Class<?> resolve(String className) {
        try {
            ClassLoader classLoader =
                    Thread.currentThread().getContextClassLoader();

            return Class.forName(
                    className,
                    true,
                    classLoader
            );

        } catch (ClassNotFoundException | ClassCastException e) {
            throw new IllegalArgumentException(
                    "Invalid event class: " + className, e);
        }
    }
}