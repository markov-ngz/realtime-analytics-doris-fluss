package ngz.markov.util;

import java.io.Serializable;
import java.text.Normalizer;
import java.util.regex.Pattern;

/**
 * Stateless keyword normalization applied before windowing so that
 * "Caroll", "CAROLL" and "caroll " all count as the same keyword.
 *
 * Rules (extend as needed):
 *   1. null / blank → empty string (caller should pre-filter these)
 *   2. Unicode NFKC normalization (handles full-width chars, ligatures)
 *   3. Lowercase
 *   4. Strip leading/trailing whitespace
 *   5. Collapse internal whitespace to single space
 *   6. Remove punctuation except hyphen (preserves "t-shirt", "self-care")
 */
public final class KeywordNormalizer implements Serializable {

    private static final long serialVersionUID = 1L;

    private static final Pattern COLLAPSE_SPACES   = Pattern.compile("\\s+");
    private static final Pattern STRIP_PUNCTUATION = Pattern.compile("[^\\p{L}\\p{N}\\s\\-]");

    private KeywordNormalizer() {}

    public static String normalize(String raw) {
        if (raw == null || raw.isBlank()) {
            return "";
        }
        String nfkc    = Normalizer.normalize(raw, Normalizer.Form.NFKC); // Normalization Form Compatibility Composition
        String lower   = nfkc.toLowerCase();
        String nopunct = STRIP_PUNCTUATION.matcher(lower).replaceAll("");
        return COLLAPSE_SPACES.matcher(nopunct.trim()).replaceAll(" ");
    }
}
