import requests
import pymorphy3
import string

URL = 'https://api.diffchecker.com/public/text?output_type=html&email=onlybrinty@mail.ru'
HEADERS = {
    'Content-type': 'application/json'
}


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


def post_request(text1, text2):
    data = {"left": text1,
            "right": text2,
            "diff_level": "word"}

    response = requests.post(URL, json=data, headers=HEADERS)

    return response.text
