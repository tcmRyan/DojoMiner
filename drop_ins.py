from lib.dojo_requests import DojoRequests
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Integer, Column, String, Boolean, DateTime
import os
from datetime import datetime

DB_NAME = 'customer.db'

# Request setup
requests = DojoRequests()

# DB Setup
engine = create_engine('sqlite:///{}'.format(DB_NAME))
Session = sessionmaker(bind=engine)
session = Session()
Base = declarative_base()


class Customer(Base):
    __tablename__ = 'customers'

    id = Column(Integer, primary_key=True)
    child_name = Column(String)
    parent_name = Column(String)
    parent_email = Column(String)
    parent_phone = Column(String)
    active = Column(Boolean)
    inactive_date = Column(DateTime)


if not os.path.islink(DB_NAME):
    Base.metadata.create_all(engine)


def download_customer_lookup():
    resp = requests.get('https://dojo.code.ninja/api/employee/cn-ma-wellesley/customerexportlist/')
    data = resp.json()
    for entry in data:
        # Assuming no children with the same name
        customer = session.query(Customer).filter_by(child_name=entry['childName']).first()
        if customer:
            if customer.active and entry.get('isActiveDropIn'):
                customer.inactive_date = datetime.now()
                customer.active = False
                session.add(customer)
                session.commit()
        else:
            customer = Customer(
                child_name=entry['childName'],
                parent_name=entry['parent1Name'],
                parent_email=entry['parent1Email'],
                parent_phone=entry['parent1Phone'],
                active=entry['isActiveDropIn'],
            )
            session.add(customer)
            session.commit()


if __name__ == '__main__':
    download_customer_lookup()





