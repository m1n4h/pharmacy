from sqlalchemy import Column, String, Integer
from app.db.base_class import Base


class RolePermission(Base):
    __tablename__ = "role_permissions"

    id = Column(Integer, primary_key=True, index=True)
    role = Column(String, nullable=False, index=True)
    module = Column(String, nullable=False)
    permission_type = Column(String, default="read")  # read, write, delete, * (all)

    def __repr__(self):
        return f"<RolePermission {self.role}:{self.module}:{self.permission_type}>"