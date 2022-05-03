from os import listdir
import math
import random
import PySimpleGUI as sg


def scalar(v1, v2):
    """
    :param v1: wektor-lista
    :param v2: wektor-lista
    :return: iloczyn skalarny dwóch wektorów
    """
    if len(v1) != len(v2):
        print("Error: Vector needs to be of length: ", len(v2))
        raise ValueError()

    s = 0
    for i in range(0, len(v1)):
        s += v1[i] * v2[i]

    return s


def add(v1, v2):
    """dodawanie do siebie wektorów, przemienne"""
    if len(v1) != len(v2):
        print("Error: Vectors need to be of the same length")
        return None
    res = []
    for i in range(0, len(v1)):
        res.append(v1[i] + v2[i])
    return res


def mul(v, c):
    """mnożenie wektora przez stałą, nieprzemienne"""
    res = []
    for x in v:
        res.append(x * c)
    return res


def length_of_vector(v):
    s = 0
    for i in range(0, len(v)):
        s += v[i]**2
    return math.sqrt(s)


def normalize(v):
    res = []
    leng = length_of_vector(v)
    if leng != 0:
        for n in v:
            res.append(n/leng)
    else:
        for n in range(len(v)):
            res.append(0)
    return res


class Perceptron:
    _alfa = 0.6

    def __init__(self, language):
        self.lang = language

        self.t = random.randint(-5, 5)   # losujemy próg

        self.w = []
        for i in range(0, 26):
            self.w.append(random.randint(-5, 5))   # losujemy wektor wag

    def output_discrete(self, x):
        net = scalar(x, self.w)
        if net >= self.t:
            return 1
        else:
            return 0

    def output_continuous(self, x):
        net = scalar(x, self.w)
        return 1 / (1 + math.e**(-net))

    def delta(self, x, d, y):
        w0 = []
        for i in self.w:
            w0.append(i)
        w0.append(self.t)
        x0 = []
        for i in x:
            x0.append(i)
        x0.append(-1)

        w1 = add(w0, mul(x0, (d - y) * self._alfa))
        t1 = w1.pop()

        self.w = w1
        self.t = t1

    def __str__(self):
        return "Perceptron " + self.lang


def text_to_vector(text):
    """
    :param text: Dowolny tekst
    :return: 26-wymiarowy wektor proporcji liter a-z {dict}
    """
    letters = {}

    for i in range(97, 123):  # a-z
        letters[chr(i)] = 0

    for c in text:
        if c in letters.keys():
            letters[c] += 1
        elif chr(ord(c)+32) in letters.keys():    # chr(97) = 'a'
            letters[chr(ord(c)+32)] += 1          # ord('a') = 97

    letter_vector = []
    for l in letters.keys():
        letter_vector.append(letters[l])

    return letter_vector


data_dir = input("Data directory path: ")  # folder danych treningowych

langs = {}

for d in listdir(data_dir):
    langs[d] = []

    for filename in listdir(data_dir + "\\" + d):
        text = ""
        with open(data_dir + "\\" + d + "\\" + filename, "r", encoding='UTF-8') as f:
            lines = f.read().splitlines()
        for l in lines:
            text += l
        langs[d].append(text)

numoflangs = len(langs.keys())

perceptrons = []

for lang in langs.keys():
    perceptrons.append(Perceptron(lang))

n = 500   # liczba powtorzeń potoku nauczania

print("I'm learning, wait...", end="")
for i in range(0, n):
    if i % 10 == 0:
        print(str(int((n-i)/10))+"...", end="")  # poczekalnia

    for lang in langs.keys():
        for text in langs[lang]:
            vector = text_to_vector(text)

            for p in perceptrons:
                y = p.output_discrete(vector)
                if p.lang == lang:
                    d = 1
                else:
                    d = 0

                if y != d:
                    p.delta(vector, d, y)

print("END.")


layout = [[sg.Text("Write your text here:")],
          [sg.Multiline("", key='input')],
          [sg.Button("Classify", button_color="purple"), sg.Button("Clear all")],
          [sg.Text("Result: ", font=('Arial', 10, 'bold')),
           sg.Text("", key='res', size=(30, 1))]]

window = sg.Window("Natural language processing", layout)

while True:
    event, values = window.read()

    if event == sg.WIN_CLOSED:
        break

    if event == "Clear all":
        window['input'].update(value="")
        window['res'].update(value="", text_color='white')

    if event == "Classify":
        text = values['input']

        if text == "\n":
            window['res'].update(value="Write something!", text_color='red')

        elif len(text) < 50:
            window['res'].update(value="Write something longer!", text_color='orange')

        else:
            vector = normalize(text_to_vector(text))
            outs = []
            result = None

            for p in perceptrons:
                p.w = normalize(p.w)
                y = p.output_continuous(vector)
                outs.append(y)

            m = max(outs)
            for i in range(0, len(outs)):
                if m == outs[i]:
                    result = perceptrons[i].lang

            window['res'].update(value=result, text_color='white')

window.close()

