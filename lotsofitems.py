from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Category, Base, CategoryItem

engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()




# Items for basketball
category1 = Category(name="Basketball")

session.add(category1)
session.commit()

categoryItem2 = CategoryItem(name="Basketball Ball", description="standard size basketball",
                     price="$7.50", category=category1)

session.add(categoryItem2)
session.commit()


categoryItem1 = CategoryItem(name="Basketball hoop", description="standard size basketball hoop",
                     price="$12.99", category=category1)

session.add(categoryItem1)
session.commit()

# Items for Snowboard
category2 = Category(name="Snowboarding")

session.add(category2)
session.commit()


categoryItem1 = CategoryItem(name="Snowboard", description="standard snowboard",
                     price="$59.99", category=category2)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(name="Bindings",
                     description="snap on bindings", price="$29", category=category2)

session.add(categoryItem2)
session.commit()

categoryItem3 = CategoryItem(name="Boots", description="size 13 boots",
                     price="15", category=category2)

session.add(categoryItem3)
session.commit()

print "items added"