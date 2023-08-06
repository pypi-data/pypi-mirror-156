
letter_to_number = {
  "A": 1,
  "B": 3,
  "C": 3,
  "D": 2,
  "E": 1,
  "F": 4,
  "G": 2,
  "H": 4,
  "I": 1,
  "J": 8,
  "K": 5,
  "L": 1,
  "M": 3,
  "N": 1,
  "O": 1,
  "P": 3,
  "Q": 10,
  "R": 1,
  "S": 1,
  "T": 1,
  "U": 1,
  "V": 4,
  "W": 4,
  "X": 8,
  "Y": 4,
  "Z": 10,
  " ": 0,
  "-": 0,
  ",": 0,
}
number_to_word = {
    0: "ZERO"
}

import inflect
p = inflect.engine()
p.number_to_words(99)

#Nigger shit
# print(p.number_to_words(int(input('Print Daddy: '))))
for n in range(10000):
    # print(n)
    number_to_word[n] = p.number_to_words(n)

# print(number_to_word)

def score_of_word(Daddy):
  return sum(letter_to_number[letter] for letter in Daddy.upper())

def score_of_number(X):
    return score_of_word(number_to_word[int(X)])

# print(score_of_number(input('Plesae daddy: ')))

def is_number_equal_to_score(Z):
    return Z == score_of_number(Z)

for number in number_to_word.keys():
    print(number,score_of_number(number),is_number_equal_to_score(number))
    if is_number_equal_to_score(number): break


# print(score_of_word(input('Please type the leetter pls: ')))