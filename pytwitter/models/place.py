"""
    Place object

    Refer: https://developer.twitter.com/en/docs/twitter-api/data-dictionary/object-model/place
"""

from dataclasses import dataclass, field, make_dataclass
from typing import Dict, List, Optional, Union

from .base import BaseModel


@dataclass
class PlaceGeoProperties(BaseModel):
    name: Optional[str] = field(default=None, repr=False)


@dataclass
class PlaceGeo(BaseModel):
    type: Optional[str] = field(default=None)
    bbox: Optional[List[float]] = field(default=None, repr=False)
    properties: Optional[Union[Dict, PlaceGeoProperties]] = field(
        default=None, repr=False
    )

    def __post_init__(self):
        if self.properties is not None and isinstance(self.properties, dict):
            new_properties = make_dataclass(
                "PlaceGeoProperties",
                [
                    (key, Optional[type(value)], field(default=None, repr=False))
                    for key, value in self.properties.items()
                ],
                bases=(PlaceGeoProperties,),
            )
            self.properties = new_properties.new_from_json_dict(self.properties)


@dataclass
class Place(BaseModel):
    """
    A class representing place object.
    """

    id: Optional[str] = field(default=None)
    full_name: Optional[str] = field(default=None)
    contained_within: Optional[List] = field(default=None, repr=False)
    country: Optional[str] = field(default=None, repr=False)
    country_code: Optional[str] = field(default=None, repr=False)
    geo: Optional[PlaceGeo] = field(default=None, repr=False)
    name: Optional[str] = field(default=None, repr=False)
    place_type: Optional[str] = field(default=None, repr=False)
