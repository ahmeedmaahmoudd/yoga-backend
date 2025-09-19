from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import create_engine, Column, Integer, String, Text, Boolean, Float, ForeignKey, Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship, Session
from pydantic import BaseModel
from typing import List, Optional

DATABASE_URL = "postgresql://avnadmin:AVNS_hTqfB48BIOmlvOOHHsP@pg-28fe0712-ahmed-54d9.h.aivencloud.com:26258/yoga-me"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

activity_responsible_teachers = Table(
    "activity_responsible_teachers",
    Base.metadata,
    Column("activity_id", Integer, ForeignKey("activities.id"), primary_key=True),
    Column("teacher_id", Integer, ForeignKey("teachers.id"), primary_key=True),
)

activity_teaching_teachers = Table(
    "activity_teaching_teachers",
    Base.metadata,
    Column("activity_id", Integer, ForeignKey("activities.id"), primary_key=True),
    Column("teacher_id", Integer, ForeignKey("teachers.id"), primary_key=True),
)

class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, nullable=False)
    position_title = Column(String, nullable=False)
    bio = Column(Text, nullable=False)
    email = Column(String, unique=True, nullable=False)
    image_url = Column(String, unique=False, nullable=False)

    responsible_activities = relationship("Activity", secondary=activity_responsible_teachers, back_populates="responsible_teachers")
    teaching_activities = relationship("Activity", secondary=activity_teaching_teachers, back_populates="teaching_teachers")

class Activity(Base):
    __tablename__ = "activities"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    image_url = Column(String)
    activity_type_id = Column(Integer, ForeignKey("activity_type.id"), nullable=False)  # <-- this is key
    capacity = Column(Integer, nullable=False)
    price = Column(Float, nullable=False)
    schedule = Column(String, nullable=False)
    expertise_level = Column(Integer, nullable=False)
    is_highlighted = Column(Boolean, default=False)
    location = Column(String, nullable=False)

    responsible_teachers = relationship("Teacher", secondary=activity_responsible_teachers, back_populates="responsible_activities")
    teaching_teachers = relationship("Teacher", secondary=activity_teaching_teachers, back_populates="teaching_activities")
    @property
    def activity_type(self):
        return self.activity_type_obj.typename if self.activity_type_obj else None

class TeacherList(BaseModel):
    id: int
    first_name: str
    image_url: str
    position_title: str

    class Config:
        orm_mode = True

class TeacherForActivity(BaseModel):
    id: int
    first_name: str
    position_title: str

    class Config:
        orm_mode = True

class ActivityList(BaseModel):
    id: int
    title: str
    activity_type: str
    image_url: Optional[str] = None  # Make image_url optional
    location: str
    is_highlighted: bool
    expertise_level: str
    
    class Config:
        orm_mode = True



class TeacherDetail(BaseModel):
    id: int
    first_name: str
    position_title: str
    bio: str
    email: str
    image_url: Optional[str] = None  # Add this line
    teaching_activities: List[ActivityList] = []
    responsible_activities: List[ActivityList] = []

    class Config:
        orm_mode = True


class ActivityDetail(BaseModel):
    id: int
    title: str
    description: str
    image_url: Optional[str] = None
    activity_type: str
    activity_type_id: int 
    capacity: int
    price: float
    schedule: str
    expertise_level: int
    is_highlighted: bool
    location: str
    responsible_teachers: List[TeacherForActivity] = []
    teaching_teachers: List[TeacherForActivity] = []

    class Config:
        orm_mode = True

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

app = FastAPI(title="Teaching Activities API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/teachers/", response_model=List[TeacherList])
def get_all_teachers(db: Session = Depends(get_db)):
    return db.query(Teacher).all()

@app.get("/teachers/{teacher_id}", response_model=TeacherDetail)
def get_teacher_details(teacher_id: int, db: Session = Depends(get_db)):
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if teacher is None:
        raise HTTPException(status_code=404, detail="Teacher not found")
    return teacher


@app.get("/activities/", response_model=List[ActivityList])
def get_all_activities(db: Session = Depends(get_db)):
    activities = db.query(Activity).all()
    return [
        ActivityList(id=a.id, title=a.title, activity_type=a.activity_type, image_url=a.image_url, location=a.location, is_highlighted= a.is_highlighted, expertise_level=a.expertise_level)
        for a in activities
    ]

@app.get("/activities/{activity_id}", response_model=ActivityDetail)
def get_activity_detail(activity_id: int, db: Session = Depends(get_db)):
    activity = db.query(Activity).options(
        selectinload(Activity.responsible_teachers),
        selectinload(Activity.teaching_teachers),
        selectinload(Activity.activity_type_obj)  # Add this to load the activity type
    ).filter(Activity.id == activity_id).first()
    
    if activity is None:
        raise HTTPException(status_code=404, detail="Activity not found")
    return activity


@app.get("/activities/highlighted/", response_model=List[ActivityList])
def get_highlighted_activities(db: Session = Depends(get_db)):
    activities = db.query(Activity).filter(Activity.is_highlighted == True).all()
    return [
        ActivityList(id=a.id, title=a.title, activity_type=a.activity_type, image_url=a.image_url, location=a.location, is_highlighted= a.is_highlighted,expertise_level=a.expertise_level)
        for a in activities
    ]

class ActivityType(Base):
    __tablename__ = "activity_type"

    id = Column(Integer, primary_key=True, index=True)
    typename = Column(String, nullable=False)
    short_description = Column(String)
    image_url = Column(String)
    long_description = Column(Text)
    benefits = Column(Text)

    activities = relationship("Activity", backref="activity_type_obj", lazy="selectin")


class ActivityTypeBasic(BaseModel):
    id: int
    typename: str
    short_description: Optional[str] = None
    image_url: Optional[str] = None

    class Config:
        orm_mode = True
@app.get("/activity-types/", response_model=List[ActivityTypeBasic])
def get_all_activity_types(db: Session = Depends(get_db)):
    return db.query(ActivityType).all()


class ActivityTypeFull(BaseModel):
    id: int
    typename: str
    short_description: Optional[str] = None
    image_url: Optional[str] = None
    long_description: Optional[str] = None
    benefits: Optional[str] = None
    activities: List[ActivityDetail] = [] 

    class Config:
        orm_mode = True

activities = relationship(
    "Activity",
    backref="activity_type_obj",
    lazy="selectin"  # or 'joined' for eager loading
)

from sqlalchemy.orm import selectinload

@app.get("/activity-types/{id}", response_model=ActivityTypeFull)
def get_activity_type_by_id(id: int, db: Session = Depends(get_db)):
    activity_type = db.query(ActivityType).options(
        selectinload(ActivityType.activities)
        .selectinload(Activity.responsible_teachers),
        selectinload(ActivityType.activities)
        .selectinload(Activity.teaching_teachers)
    ).filter(ActivityType.id == id).first()

    if activity_type is None:
        raise HTTPException(status_code=404, detail="Activity type not found")
    return activity_type



if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
