import datetime
import enum
import typing

import strawberry


@strawberry.enum
class Episode(enum.Enum):
    NEWHOPE = "NEWHOPE"
    EMPIRE = "EMPIRE"
    JEDI = "JEDI"


@strawberry.interface
class Character:
    id: strawberry.ID
    name: str
    appears_in: typing.List[Episode]

    friend_ids: strawberry.Private[typing.List[strawberry.ID]]

    @strawberry.field
    def friends(self) -> typing.Optional[typing.List[typing.Optional["Character"]]]:
        return [character_map[x] for x in self.friend_ids]


@strawberry.type
class Human(Character):
    total_credits: int

    starship_ids: typing.List[strawberry.ID]

    @strawberry.field
    def starships(self) -> typing.Optional[typing.List[typing.Optional["Starship"]]]:
        return [starship_map[x] for x in self.starship_ids]


@strawberry.type
class Droid(Character):
    primary_function: str


@strawberry.type
class Starship:
    id: strawberry.ID
    name: str


SearchResult = strawberry.union("SearchResult", (Human, Droid, Starship))

human_map: typing.Dict[strawberry.ID, Human] = {
    strawberry.ID("h-1"): Human(
        id=strawberry.ID("h-1"),
        name="luke",
        appears_in=[Episode.NEWHOPE, Episode.EMPIRE],
        friend_ids=[strawberry.ID("h-2"), strawberry.ID("d-2")],
        starship_ids=[],
        total_credits=3,
    ),
    strawberry.ID("h-2"): Human(
        id=strawberry.ID("h-2"),
        name="obi",
        appears_in=[Episode.NEWHOPE, Episode.EMPIRE, Episode.JEDI],
        friend_ids=[strawberry.ID("h-1")],
        starship_ids=[],
        total_credits=3,
    ),
}
droid_map: typing.Dict[strawberry.ID, Droid] = {
    strawberry.ID("d-1"): Droid(
        id=strawberry.ID("d-1"),
        name="C-3PO",
        appears_in=[Episode.NEWHOPE],
        friend_ids=[strawberry.ID("h-2")],
        primary_function="search",
    ),
    strawberry.ID("d-2"): Droid(
        id=strawberry.ID("d-2"),
        name="R2-D2",
        appears_in=[Episode.NEWHOPE, Episode.JEDI],
        friend_ids=[strawberry.ID("h-1"), strawberry.ID("d-1")],
        primary_function="dig",
    ),
}
starship_map: typing.Dict[strawberry.ID, Starship] = {
    strawberry.ID("s-1"): Starship(id=strawberry.ID("s-1"), name="darkstar"),
    strawberry.ID("s-2"): Starship(id=strawberry.ID("s-2"), name="ufo"),
}
hero_map: typing.Dict[Episode, strawberry.ID] = {
    Episode.NEWHOPE: strawberry.ID("h-1"),
    Episode.EMPIRE: strawberry.ID("h-2"),
    Episode.JEDI: strawberry.ID("d-1"),
}

character_map: typing.Dict[strawberry.ID, Character] = {}
character_map.update(human_map)
character_map.update(droid_map)

search_result_map: typing.Dict[strawberry.ID, SearchResult] = {}
search_result_map.update(human_map)
search_result_map.update(droid_map)
search_result_map.update(starship_map)


@strawberry.type
class Query:
    @strawberry.field
    def hello(self) -> str:
        return "hello world"

    @strawberry.field
    def today(self) -> datetime.date:
        return datetime.datetime.now().date()

    @strawberry.field
    def hero(self, episode: Episode) -> Character:
        return character_map[hero_map[episode]]

    @strawberry.field
    def droid(self, id: strawberry.ID) -> Droid:
        return droid_map[id]

    @strawberry.field
    def search(self, text: str) -> typing.List[SearchResult]:
        return [x for x in search_result_map.values() if text in x.name]


schema = strawberry.Schema(query=Query)

# show schema
# $ python -m strawberry export-schema server:schema

# run server
# $ python -m strawberry server server:schema
