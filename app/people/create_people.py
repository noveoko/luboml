from pydantic import BaseModel, validator
from typing import Optional,MutableSet



class PersonName(BaseModel):
    first: Optional[str]
    last: Optional[str]
    middle: Optional[str]
    first_phone: Optional
    middle_phone: Optional[MutableSet[str]]
    last_phone: Optional[MutableSet[str]]

class Person(BaseModel):
    full_name: PersonName    



x_name = PersonName(first='Sam', middle='', last='Thompson')
x = Person(full_name=x_name)
print(x)

