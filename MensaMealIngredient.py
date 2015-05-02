from enum import IntEnum

class General(IntEnum):
	# General Ingredients:
	Pork           = 1
	Beef           = 2
	NoMeat         = 3
	Alcohol        = 4
	Garlic         = 5
	Vegan          = 6
	
class Additives(IntEnum):
	# Additives:
	Colorant       = 7
	Preservative   = 8
	Antioxidant    = 9
	FlavorEnhancer = 10
	Sulfur         = 11
	Blackened      = 12
	Waxed          = 13
	Phosphate      = 14
	Sweetener      = 15
	Phenylalanine  = 16
	
class Allergens(IntEnum):
	# Allergens:
	Gluten         = 17
	Shellfish      = 18
	Eggs           = 19
	Fish           = 20
	Peanuts        = 21
	Soy            = 22
	Milk           = 23
	Nuts           = 24
	Celery         = 25
	Mustard        = 26
	Sesame         = 27
	Sulphite       = 28
	Lupine         = 29
	Molluscs       = 30
