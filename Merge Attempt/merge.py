import os, pickle


def save_obj(obj, name):
    with open(name + '.pkl', 'wb') as f:
        pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)


def load_obj(name):
    with open(name + '.pkl', 'rb') as f:
        return pickle.load(f)


n1 = load_obj("Char_info")
n2 = load_obj("Char_info (2)")

for key in n2:
    if n1.get(key) != None:
        max = 0
        for char in n1[key]:
            if char[10] > max:
                max = char[10]
        for card in n2[key]:
            card[10] += max
            n1[key].append(card)
    else:
        n1[key] = n2[key]

print("e")
save_obj(n1, "Char_info")
