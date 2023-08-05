class Calculator:
    """The Calculator makes Addition, Subtraction, Multiplication, Division and take Root of a number"""

    def __init__(self):
        self.total = 0

    def add(self, *args):
        """Adds a number/s to 0 or total and returns the sum
        
            calculator.add(5, 5, 5)
            15
            calculator.add(3)
            18
            calculator.add(12, 5)
            35
        """
        self.total += sum(args)
        return self.total

    def subtract(self, *args):
        """Subtracts a number/s from 0 or total and returns the sum

            calculator.subtract(5, 3)
            2
            calculator.subtract(2)
            0
        """
        for num in args:
            self.total -= num
        return self.total

    def multiply(self, *args):
        """Multiplies a number/s from 0 or total and returns the sum

            calculator.multiply(5, 5)
            25
            calculator.multiply(3)
            75
        """
        for num in args:
            if self.total == 0 and len(args) > 1:
                self.total = num
            else:
                self.total *= num
        return self.total

    def divide(self, *args):
        """Divide/s a number/s from 0 or total and return the sum

            calculator.divade(10, 2)
            5.0
            calculator.divade(2)
            2.5

        """
        for num in args:
            if self.total == 0 and len(args) > 1:
                self.total = num
            else:
                self.total /= num
        return round(self.total, 1)

    def root(self, number=None):
        """Takes a root of number you pass in or takes root from existing total
        
            e.g. total = 81
            
            calculator.root() # if we not passing any number, function take a root from existing number
            9
            calculator.root(25)
            5

        """
        if number is None:
            return round(self.total ** 0.5)
        else:
            return round(number ** 0.5)

    def reset(self):
        """Resets the calculator total to 0 and returns it
        
            calculator.reset()
            0

        """
        self.total = 0
        return self.total