from .constants import (
    CREW_BONUS_ITEM,
    CREW_CLASSES,
    CREW_COLLECTIONS,
    CREW_FACIAL_FEATURE,
    CREW_HAIR,
    CREW_HAIR_COLOR,
    CREW_HEAD_PIECE,
    CREW_OUTFIT,
    CREW_SEX,
    CREW_TITLES,
    RARITIES,
    SIZES,
    SPECTRAL_TYPES,
)


def to_rarity(bonuses: list) -> str:
    """Calculates rarity from bonus amount

    Args:
        bonuses: collection of bonuses

    Returns:
        Rarity
    """
    rarity = 0
    for b in bonuses:
        rarity += b["level"]

    if rarity <= 3:
        return RARITIES[rarity]
    if rarity <= 5:
        return RARITIES[4]
    return RARITIES[5]


def to_size(radius: int) -> str:
    """Converts asteroid radius to size

    Args:
        radius: radius number

    Returns:
        Asteroid size
    """
    if radius <= 5000:
        return SIZES[0]
    if radius <= 20000:
        return SIZES[1]
    if radius <= 50000:
        return SIZES[2]
    return SIZES[3]


def asteroid_to_names(item: dict) -> dict:
    """Converts number values in an asteroid item to the string variant

    Args:
        item: Asteroid item as received in get_asteroid()

    Returns:
        Asteroid item
    """
    spectralCode = int(item["spectralType"])
    if spectralCode < 0 or spectralCode > 10:
        item["spectralType"] = SPECTRAL_TYPES[0]
    else:
        item["spectralType"] = SPECTRAL_TYPES[spectralCode]
    item["rarity"] = to_rarity(item["bonuses"])
    item["size"] = to_size(item["r"])
    return item


def crew_to_names(item: dict) -> dict:
    """Converts number values in a crew item to the string variant

    Args:
        item: Crew item as received in get_crewmate()

    Returns:
        Crew item
    """
    item["crewCollection"] = CREW_COLLECTIONS[int(item["crewCollection"]) - 1]
    item["sex"] = CREW_SEX[int(item["sex"]) - 1]
    item["crewClass"] = CREW_CLASSES[int(item["crewClass"]) - 1]
    item["title"] = CREW_TITLES[int(item["title"]) - 1]
    item["outfit"] = CREW_OUTFIT[int(item["outfit"]) - 1]
    item["hair"] = CREW_HAIR[int(item["hair"]) - 1]
    item["facialFeature"] = CREW_FACIAL_FEATURE[int(item["facialFeature"]) - 1]
    item["hairColor"] = CREW_HAIR_COLOR[int(item["hairColor"]) - 1]
    item["headPiece"] = CREW_HEAD_PIECE[int(item["headPiece"]) - 1]
    item["bonusItem"] = CREW_BONUS_ITEM[int(item["bonusItem"]) - 1]
    return item
