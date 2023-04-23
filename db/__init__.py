from sqlalchemy import Column, String, Integer, Text, ForeignKey, select, BigInteger
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()

engine = create_async_engine(
    "postgresql+asyncpg://postgres:123456@localhost:5432/tgbot2",
    echo=False,
)

Session = async_sessionmaker(bind=engine, expire_on_commit=False, class_=AsyncSession)
session = Session()


class User(Base):
    __tablename__ = 'user'
    id = Column('id', Integer, primary_key=True)
    fio = Column('fio', String)
    phone = Column('phone', String)
    lang = Column('lang', String)
    tuman = Column('tuman', String(100))
    year = Column('year', Integer)
    tg_user_id = Column('tg_user_id', BigInteger)
    application = relationship("Application", backref='users')
    viloyat_id = Column(Integer, ForeignKey('viloyat.id'))



class Application(Base):
    __tablename__ = 'application'
    id = Column('id', Integer, primary_key=True)
    status = Column('status', String, default='pending')
    application = Column('application', Text, default='pending')
    answer = Column('answer', String)
    sent = Column('sent', String)
    lang = Column('lang', String)
    user_id = Column(Integer, ForeignKey('user.id'))



class Text(Base):
    __tablename__ = 'text'
    id = Column('id', Integer, primary_key=True)
    greeting = Column('greeting', Text)
    step1 = Column('step1', String)
    step2 = Column('step2', String)
    step3 = Column('step3', Text)
    step4 = Column('step4', Text)
    step5 = Column('step5', Text)
    step6 = Column('step6', Text)
    step7 = Column('step7', Text)
    lang = Column('lang', Text)

    def __int__(self, id, greeting, step1, step2, step3, step4, step5, step6, step7, lang):
        self.id = id
        self.greeting = greeting
        self.step1 = step1
        self.step2 = step2
        self.step3 = step3
        self.step4 = step4
        self.step5 = step5
        self.step6 = step6
        self.step7 = step7
        self.lang = lang


class Viloyat(Base):
    __tablename__ = 'viloyat'
    id = Column('id', Integer, primary_key=True)
    name_uz = Column('name_uz', String(150))
    name_ru = Column('name_ru', String(150))
    name_uz_kir = Column('name_uz_kir', String(150))
    user = relationship("User", backref='viloyati')

async def get_lang(user_id) -> str:
    try:
        user = await session.execute(select(User).filter_by(tg_user_id=int(user_id)))
        user = user.scalar()

        return user.lang
    except:
        return 'uz_kir'