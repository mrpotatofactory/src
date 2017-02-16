from toontown.pets.Pet import Pet

class FADDoodle(Pet):
    def makeRandomPet(self):
        Pet.makeRandomPet(self)
        self.clearBin()
        