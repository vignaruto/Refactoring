class VendingMachine:
    def __init__(self, stock, prices):
        self.stock = stock
        self.prices = prices
        self.credit = 0

    def insert(self, coins):
        self.credit += coins

    def select(self, item):
        price = self.prices.get(item)
        if price is None:
            return "unknown"
        condition = self.stock.get(item, 0) > 0
        if condition:
            condition = self.credit >= price and price > 0
        if condition:
            self.stock[item] -= 1
            self.credit -= price
            return "dispensed"
        return "denied"

if __name__ == "__main__":
    vm = VendingMachine({"cola": 1}, {"cola": 150})
    vm.insert(200)
    assert vm.select("cola") == "dispensed"
    assert vm.credit == 50
    assert vm.select("cola") == "denied"
    assert vm.select("tea") == "unknown"
