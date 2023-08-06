from typing import Type

from BotCore import DataBase
from BotCore.ModelInfo import ModelInfo


# noinspection SqlNoDataSourceInspection,SqlResolve
class DAO:

	def __init__(self, database: DataBase, model: Type[ModelInfo]):
		self.database: DataBase = database
		self.model = model

	def create(self, **kwargs):
		return self.database.update(
			f"INSERT INTO {self.model.table()} ({', '.join(self.model.fields())}) "
			f"VALUES ({', '.join('?' for _ in self.model.fields())})",
			*[kwargs.get(field) for field in self.model.fields()]
		)

	def delete(self, row_id):
		return self.database.update(f"DELETE FROM {self.model.table()} WHERE id = ?", row_id)

	def getall(self):
		return self.database.fetchall(f"SELECT {', '.join(self.model.fields())} FROM {self.model.table()}")

	def find_by_id(self, row_id):
		return self.database.fetchone(
			f"SELECT {', '.join(self.model.fields())} "
			f"FROM {self.model.table()} "
			f"WHERE id = ?", row_id
		)
