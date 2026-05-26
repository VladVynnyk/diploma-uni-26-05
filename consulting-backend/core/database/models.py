from sqlalchemy import DateTime, create_engine, TIMESTAMP, func, text
from sqlalchemy.dialects.postgresql import UUID
#
engine = create_engine('postgresql+psycopg2://postgres:1234\@127.0.0.1/consultingdb')

import uuid
from typing import List
from sqlalchemy import Table, Column, String, Integer, ForeignKey, Boolean
from sqlalchemy.orm import Mapped, relationship, mapped_column, column_property
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.sql import select


db_user = 'postgres'
db_password = '1234'
db_host = 'localhost'
db_port = '49153'
db_name = 'cryptodb'

# create the database url for SQLAlchemy
db_url = f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
# engine = sqlalchemy.create_engine(db_url)
# connection = engine.connect()

# Base = declarative_base()
class Base(DeclarativeBase):
    pass

class Order(Base):
    __tablename__ = 'order'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")  # SQL function for generating UUIDs
    )
    price = Column(Integer) # Price of consultation
    status = Column(String(30), nullable=False, server_default="new")
    topic = Column(String(255))
    message = Column(String(1000))
    scheduled_at = Column(DateTime(timezone=True))
    duration_minutes = Column(Integer, nullable=False, server_default="60")
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    consultant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))

    # Relationships to the User table
    consultant: Mapped["User"] = relationship(
        "User",
        foreign_keys=[consultant_id],
        back_populates="consultations_as_consultant",
    )
    client: Mapped["User"] = relationship(
        "User",
        foreign_keys=[client_id],
        back_populates="consultations_as_client",
    )


class Review(Base):
    __tablename__ = 'review'

    # id: Mapped[str] = mapped_column(String(26), primary_key=True, index=True, default=lambda: str(ulid.new()))
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")  # SQL function for generating UUIDs
    )
    description = Column(String(255))
    rating = Column(Integer)
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    consultant_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE"))
    client_id: Mapped[uuid.UUID] = mapped_column(ForeignKey("users.id", ondelete="CASCADE")) 

    # Relationships to User
    consultant: Mapped["User"] = relationship("User", foreign_keys=[consultant_id], back_populates="reviews_as_consultant")
    client: Mapped["User"] = relationship("User", foreign_keys=[client_id], back_populates="reviews_as_client")
    

association_table = Table(
    "tags_users",
    Base.metadata,
    Column("tag_id", ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True),
    Column("user_id", ForeignKey("users.id", ondelete="CASCADE"), primary_key=True),
)

class Tag(Base):
    __tablename__ = "tags"

    # id = Column(Integer, primary_key=True, index=True)
    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")  # SQL function for generating UUIDs
    )
    name: Mapped[str] =  mapped_column(String(255), unique=True)
    description = Column(String(255))
    created_at = Column(TIMESTAMP, server_default=func.now())
    
    users: Mapped[List["User"]] = relationship(
        secondary=association_table, back_populates="tags", cascade="all, delete, save-update"
    )

# User entity represents two user types: clients, and consultants.
# Clients - it's a people, who buying consultations
# Consultants - it's a people, who selling consultations
class User(Base):
    __tablename__ = 'users'

    id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        server_default=text("gen_random_uuid()")  # SQL function for generating UUIDs
    )
    first_name = Column(String(255))
    last_name = Column(String(255))
    phone_number = Column(String(255))

    email = Column(String(255))
    password = Column(String(255))

    photo = Column(String(255))
    description = Column(String(255))
    price = Column(Integer) # Field for price of hour of consultation

    created_at = Column(TIMESTAMP, server_default=func.now())

    # Relationships with Tag
    tags: Mapped[List[Tag]] = relationship(
        secondary=lambda: association_table, back_populates="users", cascade="all, delete, save-update", lazy="joined"
    )

    # Relationships to the Order table
    consultations_as_consultant: Mapped[list["Order"]] = relationship(
        "Order",
        foreign_keys="Order.consultant_id",
        back_populates="consultant",
        cascade="all, delete",
    )
    consultations_as_client: Mapped[list["Order"]] = relationship(
        "Order",
        foreign_keys="Order.client_id",
        back_populates="client",
        cascade="all, delete",
    )

    # Relationships with Review
    reviews_as_consultant: Mapped[List["Review"]] = relationship(
        "Review",
        foreign_keys="Review.consultant_id",
        back_populates="consultant",
        cascade="all, delete",
    )
    reviews_as_client: Mapped[List["Review"]] = relationship(
        "Review",
        foreign_keys="Review.client_id",
        back_populates="client",
        cascade="all, delete",
    )

    rating = column_property(
        select(func.coalesce(func.avg(Review.rating), 0))
        .where(Review.consultant_id == id)
        .correlate_except(Review)
        .as_scalar()
    )

    is_consultant = Column(Boolean, default=False) # Field of verifying, that user is or customer, or consultant. It's used only for display consultants on frontend.
    is_admin = Column(Boolean, default=False, nullable=False, server_default="false")


class CardPayment(Base):
    __tablename__ = 'card_payment'

    id = Column(Integer, primary_key=True, index=True)
    rrn = Column(String(255))
    masked_card = Column(String(255))
    sender_cell_phone = Column(String(255))
    response_signature_string = Column(String(255))
    response_status = Column(String(255))
    sender_account = Column(String(255))
    fee = Column(String(255))
    rectoken_lifetime = Column(String(255))
    reversal_amount = Column(String(255))
    settlement_amount = Column(String(255))
    actual_amount = Column(String(255))
    order_status = Column(String(255))
    response_description = Column(String(255))
    verification_status = Column(String(255))
    order_time = Column(String(255))
    actual_currency = Column(String(255))
    order_id = Column(String(255), unique=True)
    parent_order_id = Column(String(255))
    merchant_data = Column(String(255))
    tran_type = Column(String(255))
    eci = Column(String(255))
    settlement_date = Column(String(255))
    payment_system = Column(String(255))
    rectoken = Column(String(255))
    approval_code = Column(String(255))
    merchant_id = Column(Integer)
    settlement_currency = Column(String(255))
    payment_id = Column(Integer)
    product_id = Column(String(255))
    currency = Column(String(255))
    card_bin = Column(Integer)
    response_code = Column(String(255))
    card_type = Column(String(255))
    amount = Column(String(255))
    sender_email = Column(String(255))
    signature = Column(String(255))

    # order_id = 



