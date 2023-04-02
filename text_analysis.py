import pymorphy3
import string


def delete_extra_parts(text):
    morph = pymorphy3.MorphAnalyzer()
    tokens = text.translate(str.maketrans('', '', string.punctuation)).lower().split()
    clear_tokens = tuple(
        filter(lambda x: morph.parse(x)[0].tag.POS not in ('CONJ', 'PRCL', 'INTJ', 'PREP'), tokens))

    return clear_tokens


def get_bgramms(tokens):
    return tuple((tokens[i], tokens[i + 1]) for i in range(len(tokens) - 1))


def get_correct_text(aud_txt, rel_txt):
    aud_tok, real_tok = delete_extra_parts(aud_txt), delete_extra_parts(rel_txt)
    aud_bgram, real_bgram = get_bgramms(aud_tok), get_bgramms(real_tok)

    comparison = [g in real_bgram for g in aud_bgram]
    similarity = comparison.count(True) / len(comparison)

    return similarity
