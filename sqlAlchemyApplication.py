from sqlalchemy.orm import declarative_base
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Session
from sqlalchemy import Column, Integer, String
from sqlalchemy import ForeignKey, create_engine, inspect, select, func


Base = declarative_base()


class User(Base):
    __tablename__ = "user_account"
    # atributos
    id = Column(Integer, primary_key=True)
    name = Column(String)
    fullname = Column(String)

    address = relationship(
        "Address", back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self):
        return f"User(id={self.id},name={self.name},fullname={self.fullname})"


class Address(Base):
    __tablename__ = "adress"

    id = Column(Integer, primary_key=True)
    email_address = Column(String(40), nullable=False)
    user_id = Column(Integer, ForeignKey("user_account.id"), nullable=False)

    user = relationship(
        "User", back_populates="address"
    )

    def __repr__(self):
        return f"Address(id={self.id}, email_address={self.email_address})"


if __name__ == "__main__":
    # conexão com banco de dados.
    engine = create_engine("sqlite://")

    # criando as classes como tabela no banco de dados
    Base.metadata.create_all(engine)
    # criando inspector para analisar dados
    inspetor_engine = inspect(engine)

    print(inspetor_engine.has_table("user_account"))
    print(inspetor_engine.get_table_names())
    print(inspetor_engine.default_schema_name)

    with Session(engine) as session:
        leonardo = User(
            name='leonardo',
            fullname='Leonardo Pereira',
            address=[Address(email_address='leonardo@email.com')]
        )

        juliana = User(
            name='juliana',
            fullname='Juliana Teixeira',
            address=[Address(email_address='juliana@email.com'),
                     Address(email_address='julianat@email.com')]
        )

        jorge = User(name='jorge', fullname='Jorge Teixeira',)

        # enviando para o banco de dados (persistência de dados).
        session.add_all([leonardo, juliana, jorge])

        session.commit()

    stmt = select(User).where(User.name.in_(['juliana', 'leonardo']))
    print('Recuperando usuários a partir de uma condição de filtragem.')
    for user in session.scalars(stmt):
        print(user)

    print('\nRecuperando os endereços de e-mail de Juliana.')
    stmt_address = select(Address).where(Address.user_id.in_([2]))
    for address in session.scalars(stmt_address):

        print(address)

    stmt_order = select(User).order_by(User.fullname.desc())
    print("\nRecuperando info de maneira ordenada")
    for result in session.scalars(stmt_order):
        print(result)

    stmt_join = select(User.fullname, Address.email_address).\
        join_from(Address, User)
    # scalars não funciona nesse caso, pois trás somente o primeiro resultado.
    for result in session.scalars(stmt_join):
        print(result)

    connection = engine.connect()
    results = connection.execute(stmt_join).fetchall()
    print("\nExecutando statement a partir da connection")
    for result in results:
        print(result)

    stmt_count = select(func.count('*')).select_from(User)
    print("Total de instâncias em User")
    for result in session.scalars(stmt_count):
        print(result)
