from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from models import Base, Category, CategoryItem, User

engine = create_engine('sqlite:///itemcatalogwithusers.db')
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


# Create dummy user
User1 = User(name="Robo Barista", email="tinnyTim@udacity.com",
             picture='https://pbs.twimg.com/profile_images/2671170543/18debd694829ed78203a5a36dd364160_400x400.png')
session.add(User1)
session.commit()

# Items for basketball
category1 = Category(name="Basketball")

session.add(category1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Basketball Ball", description="standard size basketball",
                     price="$7.50", category=category1)

session.add(categoryItem2)
session.commit()


categoryItem1 = CategoryItem(user_id=1, name="Basketball hoop", description="standard size basketball hoop",
                     price="$12.99", category=category1)

session.add(categoryItem1)
session.commit()

# Items for Snowboard
category2 = Category(name="Snowboarding")

session.add(category2)
session.commit()


categoryItem1 = CategoryItem(user_id=1, name="Snowboard", description="standard snowboard",
                     price="$59.99", category=category2)

session.add(categoryItem1)
session.commit()

categoryItem2 = CategoryItem(user_id=1, name="Bindings",
                     description="snap on bindings", price="$29", category=category2)

print "added items withs users"