import random

from count_caps import count_caps

def test_all_lowercase():
    assert count_caps("this sentence is all lowercase.") == 0

def test_all_uppercase():
    assert count_caps("THIS SENTENCE IS ALL UPPERCASE.") == 5

def test_all_propercase():
    assert count_caps("This Sentence Is All Propercase.") == 5

def test_all_mix():
    assert count_caps("This sentence is a mix.") == 1

def test_not_string():
    assert count_caps(0) == 0

def test_random_mix():
    """Generates a random sentence of uppercase and lowercase words to test"""

    lowercase_words = ['these', 'are', 'five', 'lowercase', 'words']
    uppercase_words = ['These', 'Are', 'Five', 'Uppercase', 'Words']
    words = []

    num_lowercase_words = random.randint(1, 5)
    num_uppercase_words = random.randint(1, 5)
    answer = num_uppercase_words

    while num_lowercase_words > 0 or num_uppercase_words > 0:
        if num_lowercase_words == 0:
            words.append(uppercase_words[random.randint(0,4)])
            num_uppercase_words -= 1
        elif num_uppercase_words == 0:
            words.append(lowercase_words[random.randint(0,4)])
            num_lowercase_words -= 1
        else:
            if random.random() > 0.5:
                words.append(uppercase_words[random.randint(0,4)])
                num_uppercase_words -= 1
            else:
                words.append(lowercase_words[random.randint(0,4)])
                num_lowercase_words -= 1

    sentence = " ".join(words)

    assert count_caps(sentence) == answer
