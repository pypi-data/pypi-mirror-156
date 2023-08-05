class Calculator:
    """The Calculator makes Addition, Subtraction, Multiplication, Division and take Root of a number"""

    def __init__(self):
        self.total = 0

    def add(self, *args):
        """Adds a number/s to 0 or total and returns the sum"""
        self.total += sum(args)
        return self.total

    def subtract(self, *args):
        """Subtracts a number/s from 0 or total and returns the sum"""
        self.total -= sum(args)
        return self.total

    def multiply(self, *args):
        """Multiplies a number/s from 0 or total and returns the sum"""
        for num in args:
            if self.total == 0 and len(args) > 1:
                self.total = num
            else:
                self.total *= num
        return self.total

    def divide(self, *args):
        """Divide/s a number/s from 0 or total and return the sum"""
        for num in args:
            if self.total == 0 and len(args) > 1:
                self.total = num
            else:
                self.total /= num
        return round(self.total, 1)

    def root(self, number=None):
        """Takes a root of number you pass in or takes root from existing total"""
        if number is None:
            return round(self.total ** 0.5)
        else:
            return round(number ** 0.5)

    def reset(self):
        """Resets the calculator total to 0"""
        self.total = 0
        return self.total