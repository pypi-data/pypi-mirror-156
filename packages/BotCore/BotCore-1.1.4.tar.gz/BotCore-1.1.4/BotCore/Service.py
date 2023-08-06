
from typing import TypeVar, Type, Generic

from BotCore import DAO, ModelInfo

T = TypeVar("T", bound=ModelInfo)
D = TypeVar("D", bound=DAO)


class Service(Generic[T, D]):

	def __init__(self, model: Type[T], dao: D):
		self.model: Type[T] = model
		self.dao: D = dao

	def create(self, **kwargs):
		return self.dao.create(**kwargs)

	def delete(self, row_id):
		return self.dao.delete(row_id)

	def getall(self) -> list[T]:
		return self.to_objects(self.dao.getall())

	def find_by_id(self, row_id):
		return self.to_object(self.dao.find_by_id(row_id))

	def to_objects(self, rows: list[tuple]) -> list[T]:
		return [self.to_object(row) for row in rows]

	def to_object(self, row: tuple) -> T:
		return self.model(dict(zip(self.model.fields(), row)))
