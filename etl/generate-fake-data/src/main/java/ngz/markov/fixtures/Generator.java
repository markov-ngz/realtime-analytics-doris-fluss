package ngz.markov.fixtures;

/*
 *  Generate Instance of the specified class
 */
public interface Generator<T> {
    T generate();
}