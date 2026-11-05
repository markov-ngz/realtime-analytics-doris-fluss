package ngz.markov.fixtures;

import org.apache.flink.api.connector.source.SourceReaderContext;
import org.apache.flink.connector.datagen.source.GeneratorFunction;

public class FixtureGeneratorFunction<T> implements GeneratorFunction<Long, T> {

    private final Class<T> clazz;
    private Generator<T> generator;

    public FixtureGeneratorFunction(Class<T> clazz) {
        this.clazz = clazz;
    }

    @Override
    public void open(SourceReaderContext readerContext) {
        this.generator = FixtureGeneratorProvider.getGenerator(clazz);
    }

    @Override
    public T map(Long value) {
        return generator.generate();
    }
}