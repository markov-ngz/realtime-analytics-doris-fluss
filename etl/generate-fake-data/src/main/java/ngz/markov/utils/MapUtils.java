package ngz.markov.utils;

import java.util.HashMap;
import java.util.Map;

public class MapUtils {
    public static Map<String, String> subMap(Map<String, String> config, String prefix) {
        Map<String, String> result = new HashMap<>();

        for (Map.Entry<String, String> entry : config.entrySet()) {
            if (entry.getKey().startsWith(prefix)) {
                String newKey = entry.getKey().substring(prefix.length() );
                result.put(newKey, entry.getValue());
            }
        }

        return result;
    }
}
