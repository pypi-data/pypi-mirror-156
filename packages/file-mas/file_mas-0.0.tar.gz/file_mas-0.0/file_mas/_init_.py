import json, random


class FileMas():
    """class of special array, that saves in a file"""
    def __init__(self, name, first = False, values = []):
        """System function: initialization"""
        if first:
            self.values = values
        self.name = name
        self.file_name = name = name + '.json'
        if first:
            file = open(self.file_name, "w")
            json.dump(values, file)
            file.close()
        else:
            file = open(self.file_name,'r')
            self.values = json.load(file)
            file.close()
        self.length = len(values)

    def load(self):
        """System function: loads value from a file"""
        file = open(self.file_name, 'r')
        self.values = json.load(file)
        file.close()

    def pick(self):
        """System function: picks value in a file"""
        file = open(self.file_name, 'w')
        json.dump(self.values, file)
        file.close()

    def change(self, new_val):
        """changes values to new_val"""
        self.values = new_val
        self.pick()
        return self.values

    def add(self, new_val):
        """appends new_val to mas"""
        self.values.append(new_val)
        self.pick()
        return self.values

    def len(self):
        """returns length of values"""
        return len(self.values)

    def rev(self, change=True):
        """returns inverse array, if change = True - change values."""
        if change:
            self.values = self.values[::-1]
            self.pick()
            return self.values
        else:
            return self.values[::-1]

    def choose(self, first=0, end=-1):
        """chooses random element from first to end elements"""
        temp = self.values[first: end]
        temp.append(self.values[end])
        return random.choice(temp)

    def mix(self, change=True):
        """return random mixed values. If change = true also changes them."""
        if change:
            random.shuffle(self.values)
            self.pick()
            return self.values
        else:
            temp = self.values
            random.shuffle(temp)
            return temp

    def del_index(self, index=-1):
        self.values.pop(index)
        self.pick()
        return self.values

    def del_value(self, value, count=1):
        for i in range(count):
            self.values.remove(value)
        self.pick()
        return self.values


def test():
    """system function to test programs"""
    test_mas = FileMas([1, 2, 3, 4, 5], "test")
    print(test_mas.mix())


if __name__ == "__main__":
    test()