from datetime import datetime, timedelta
from fastapi import FastAPI, HTTPException, Body, status, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel
import sqlalchemy
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from typing import List
from sqlalchemy.sql import text
import xml.etree.ElementTree as ET
import os

tree = ET.parse('backend_config.xml')
root = tree.getroot()

frontendurl = os.environ.get('FRONTEND_HOST', '192.168.2.170:3000')
dbHost = root.find('dbHost').text
dbPort = root.find('dbPort').text
dbName = root.find('dbName').text
dbUser = root.find('dbUser').text
dbPassword = root.find('dbPassword').text

# engine = sqlalchemy.create_engine
# ("mysql+pymysql://tempwade:password@23.229.227.36:3306/tastyonabudget")
engine = sqlalchemy.create_engine(
    "mariadb+mariadbconnector://" +
    dbUser +
    ":" +
    dbPassword +
    "@" +
    dbHost +
    ":" +
    dbPort +
    "/" +
    dbName)
# engine = sqlalchemy.create_engine
# ("mariadb+mariadbconnector://temp:password@192.168.2.170:3306/tasty")
Base = declarative_base()
Session = sqlalchemy.orm.sessionmaker()
Session.configure(bind=engine)
session = Session()


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None


class User(Base):
    __tablename__ = 'users'
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement='ignore_fk')
    children: Mapped[List["UserSurveyDataSQL"]
                     ] = relationship(back_populates="parent")
    username = sqlalchemy.Column(sqlalchemy.String(length=100))
    password = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=False)
    email = sqlalchemy.Column(sqlalchemy.String(length=100), nullable=False)
    firstName = sqlalchemy.Column(
        sqlalchemy.String(
            length=100),
        nullable=False)


class UserLoginData(BaseModel):
    username: str
    password: str
    email: str
    firstName: str


class LoginModel(BaseModel):
    username: str
    password: str


class recipe(Base):
    __tablename__ = 'recipe'
    id = sqlalchemy.Column(sqlalchemy.String(length=100), primary_key=True)
    title = sqlalchemy.Column(sqlalchemy.String(length=100))
    steps = sqlalchemy.Column(sqlalchemy.String(length=100))
    nutrition = sqlalchemy.Column(sqlalchemy.String(length=100))
    description = sqlalchemy.Column(sqlalchemy.String(length=100))
    servings = sqlalchemy.Column(sqlalchemy.String(length=100))
    thumbnail = sqlalchemy.Column(sqlalchemy.String(length=100))
    ingredients = sqlalchemy.Column(sqlalchemy.String(length=100))
    tags = sqlalchemy.Column(sqlalchemy.String(length=100))


class UserSurveyDataSQL(Base):
    __tablename__ = 'userdata'
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement=True)
    users_id = mapped_column(ForeignKey("users.id"))
    parent = relationship("User", back_populates="children")
    calorie_goal = sqlalchemy.Column(sqlalchemy.String(length=100))
    gender = sqlalchemy.Column(sqlalchemy.String(length=100))
    height = sqlalchemy.Column(sqlalchemy.String(length=100))
    weight = sqlalchemy.Column(sqlalchemy.String(length=100))
    age = sqlalchemy.Column(sqlalchemy.String(length=100))
    cooking_exp = sqlalchemy.Column(sqlalchemy.String(length=100))
    num_days = sqlalchemy.Column(sqlalchemy.String(length=100))
    activity_level = sqlalchemy.Column(sqlalchemy.String(length=100))


class UserSurveyData(BaseModel):
    userID: int
    calorie_goal: str
    gender: str
    height: str
    weight: str
    age: str
    cooking_exp: str
    num_days: str
    activity_level: str


class likedrecipies(Base):
    __tablename__ = 'likedrecipies'
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    recipie_id = sqlalchemy.Column(sqlalchemy.String(length=100))


class dislikedrecipies(Base):
    __tablename__ = 'dislikedrecipies'
    id = sqlalchemy.Column(
        sqlalchemy.Integer,
        primary_key=True,
        autoincrement=True)
    user_id = sqlalchemy.Column(sqlalchemy.Integer)
    recipie_id = sqlalchemy.Column(sqlalchemy.String(length=100))


Base.metadata.create_all(engine)


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

app = FastAPI()


origins = [
    "http://" + frontendurl,
    frontendurl
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


SECRET_KEY = "c43421ccc0b4a9bd1905ef5facd2bf8a4e70ffb0445a6da31d4b0ef3e246d1fb"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30


def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password):
    return pwd_context.hash(password)


def get_user(username: str):
    user = (session.query(User).filter(User.username == username).first())
    return (user)


def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user:
        return False
    if verify_password(password, user.password):
        return user
    return False


def create_access_token(
        user: UserLoginData,
        expires_delta: timedelta | None = None):
    to_encode = user.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except JWTError:
        raise credentials_exception
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user


async def get_current_active_user(
    current_user: User = Depends(get_current_user)
):
    if current_user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return current_user


def get_user_data():
    User = get_current_active_user()
    usersurveydata = (session.query(UserSurveyData).filter(
        User.id == UserSurveyDataSQL.users_id).first())
    return (usersurveydata)


tags = ["Auth"]


@app.post("/auth/login")
def login(login: LoginModel):
    user = authenticate_user(login.username, login.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token({"id": user.id,
                                        "username": user.username,
                                        "email": user.email,
                                        "fname": user.firstName},
                                       expires_delta=access_token_expires)
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "login_status": "success"}


@app.put("/addUser")
async def addUser(user: UserLoginData):
    user.password = get_password_hash(user.password)
    newUser = User(
        username=user.username,
        password=user.password,
        email=user.email,
        firstName=user.firstName
    )
    if len(session.query(User).filter(
        User.username == user.username
    ).all()) != 0:
        raise HTTPException(status_code=400, detail="double user")
    if len(session.query(User).filter(
        User.email == user.email
    ).all()) != 0:
        raise HTTPException(status_code=400, detail="double email")
    session.add(newUser)
    session.commit()
    raise HTTPException(status_code=200, detail="Succ")


@app.put("/like_recipie")
async def like_recipie(
    payload: dict = Body(...)
):
    query = text(
        "SELECT * from likedrecipies where user_id = :user_id AND recipie_id"
        "= :recipie_id")
    result = session.execute(query,
                             {'user_id': payload["userId"],
                              'recipie_id': payload["recipieId"]})
    rows = result.mappings().all()
    ret = [dict(row) for row in rows]
    query = text(
        "SELECT * from dislikedrecipies where user_id = :user_id AND"
        "recipie_id = :recipie_id")
    result = session.execute(query,
                             {'user_id': payload["userId"],
                              'recipie_id': payload["recipieId"]})
    rows = result.mappings().all()
    ret2 = [dict(row) for row in rows]
    print(len(ret))
    if (len(ret2) > 0):
        crud = text(
            "delete from dislikedrecipies where user_id = :user_id AND"
            " recipie_id = :recipie_id")
        session.execute(crud, {'user_id': payload["userId"],
                               'recipie_id': payload["recipieId"]})
        session.commit()
    if (len(ret) > 0):
        crud = text(
            "delete from likedrecipies where user_id = :user_id AND"
            " recipie_id = :recipie_id")
        session.execute(crud,
                        {'user_id': payload["userId"],
                         'recipie_id': payload["recipieId"]})
        session.commit()
        return
    newLike = likedrecipies(
        user_id=payload["userId"],
        recipie_id=payload["recipieId"])
    session.add(newLike)
    session.commit()


@app.put("/dislike_recipie")
async def dislike_recipie(payload: dict = Body(...)):
    query = text(
        "SELECT * from dislikedrecipies where user_id = :user_id AND"
        " recipie_id = :recipie_id")
    result = session.execute(query,
                             {'user_id': payload["userId"],
                              'recipie_id': payload["recipieId"]})
    rows = result.mappings().all()
    ret = [dict(row) for row in rows]

    query = text(
        "SELECT * from likedrecipies where user_id = :user_id AND"
        " recipie_id = :recipie_id")
    result = session.execute(query,
                             {'user_id': payload["userId"],
                              'recipie_id': payload["recipieId"]})
    rows = result.mappings().all()
    ret2 = [dict(row) for row in rows]
    print(len(ret))
    if (len(ret2) > 0):
        crud = text(
            "delete from likedrecipies where user_id = :user_id AND"
            " recipie_id = :recipie_id")
        session.execute(crud,
                        {'user_id': payload["userId"],
                         'recipie_id': payload["recipieId"]})
        session.commit()

    print(len(ret))
    if (len(ret) > 0):
        crud = text(
            "delete from dislikedrecipies where user_id = :user_id AND"
            " recipie_id = :recipie_id")
        session.execute(crud,
                        {'user_id': payload["userId"],
                         'recipie_id': payload["recipieId"]})
        session.commit()
        return
    newLike = dislikedrecipies(
        user_id=payload["userId"],
        recipie_id=payload["recipieId"])
    session.add(newLike)
    session.commit()


@app.get("/users/me/items/")
async def read_own_items(
    current_user: User = Depends(get_current_active_user)
):
    return [{"item_id": "Foo", "owner": current_user.username}]


@app.get("/recipes")
async def getrecipes():
    query = text(
        "SELECT recipe.id,title,steps,nutrition,description,"
        "servings,thumbnail,ingredients,tags,"
        "group_concat(dislikedrecipies.user_id) as isdislikedrecipe,"
        "group_concat(likedrecipies.user_id) as islikedrecipe"
        "FROM recipe"
        "LEFT JOIN dislikedrecipies"
        "ON recipe.id = dislikedrecipies.recipie_id"
        "LEFT JOIN likedrecipies"
        "ON recipe.id = likedrecipies.recipie_id"
        "GROUP BY recipe.id")
    return (session.execute(query))


@app.put("/removetests")
async def getrecipesr():
    query = text(
        "DELETE FROM users WHERE username IN "
        "('testuser','testuser','testuser3','testuser4')")
    return (session.execute(query))


@app.get("/recipes/reccomended/{username}")
async def getrecipesforUser(username: str):
    current_user = get_user(username)
    userdata = (session.query(UserSurveyDataSQL).filter(
        current_user.id == UserSurveyDataSQL.users_id).first())
    ret = None
    if (userdata is not None):
        if (int(userdata.calorie_goal) is not None):
            calories = int(userdata.calorie_goal)
            if (calories < 400):
                calories = 400
            if (calories > 1400):
                calories = 1400
            print(calories)
            caloriesupper = calories + 100
            calorieslower = calories - 100
            query = text(
                "SELECT DISTINCT recipe.id,title,steps,nutrition,description,\
                        servings,thumbnail,ingredients,tags, \
                         group_concat(dislikedrecipies.user_id) as dislikedBy,\
                          group_concat(likedrecipies.user_id) as likedBy \
                         FROM recipe LEFT JOIN dislikedrecipies \
                         ON recipe.id = dislikedrecipies.recipie_id \
                         LEFT JOIN likedrecipies ON recipe.id =\
                         likedrecipies.recipie_id  \
                         WHERE nutrition REGEXP\
                         '\"calories\":([1-9][0-9]{0,2}|[0-9]{1,2})' \
                         AND JSON_EXTRACT(nutrition, '$.calories')\
                         BETWEEN " + str(calorieslower) + " \
                         AND " + str(caloriesupper) + " \
                         AND recipe.id NOT IN (SELECT recipie_id\
                         FROM dislikedrecipies \
                         WHERE user_id = " + str(userdata.users_id) + ") \
                         GROUP BY recipe.id ORDER BY RAND() \
                         Limit " + str(userdata.num_days) + ";")
            result = session.execute(query)
            ret = result.mappings().all()
    else:
        ret = None
    return (ret)


@app.get("/recipes/liked/{username}")
async def getLikedRecipes(username: str):
    current_user = get_user(username)
    userdata = (session.query(User).filter(current_user.id == User.id).first())
    print(userdata)
    ret = None
    query = text(
        "SELECT recipe.id,title,steps,nutrition,"
        "description,servings,thumbnail,ingredients,tags, "
        "group_concat(likedrecipies.user_id) as likedBy "
        "FROM recipe "
        "LEFT JOIN likedrecipies "
        "ON recipe.id = likedrecipies.recipie_id "
        "WHERE recipe.id IN (SELECT recipie_id FROM likedrecipies)"
        " AND user_id = " + str(
            userdata.id) + " "
        "GROUP BY recipe.id;")
    result = session.execute(query)
    ret = result.mappings().all()
    return (ret)


@app.get("/recipes/{id}")
async def getrecipesid(id):
    return (session.query(recipe).filter(recipe.id == id).first())


@app.get("/recipes/{tags}")
async def getrecipestags(tags):
    return (session.query(recipe).all().filter(recipe.tags.like(tags)))


@app.get("/recipes/num/{num}")
async def getrecipesnum(num):
    query = text(
        "SELECT recipe.id,title,steps,nutrition,description"
        ",servings,thumbnail,ingredients,tags, "
        "group_concat(dislikedrecipies.user_id) as dislikedBy, "
        "group_concat(likedrecipies.user_id) as likedBy "
        "FROM recipe "
        "LEFT JOIN dislikedrecipies "
        "ON recipe.id = dislikedrecipies.recipie_id "
        "LEFT JOIN likedrecipies "
        "ON recipe.id = likedrecipies.recipie_id "
        "GROUP BY recipe.id "
        "ORDER BY RAND ( )"
        "limit  " + num)
    res = session.execute(query)
    ret = res.mappings().all()
    return (ret)


@app.get("/recipes/searchtitle/{searchval}")
async def searchrecipes(searchval):
    if not searchval:
        raise HTTPException(status_code=400, detail="Empty Search")
    sqlText = text(
        "SELECT recipe.id,title,steps,nutrition,description"
        ",servings,thumbnail,ingredients,tags, "
        "group_concat(dislikedrecipies.user_id) as dislikedBy, "
        "group_concat(likedrecipies.user_id) as likedBy "
        "FROM recipe "
        "LEFT JOIN dislikedrecipies "
        "ON recipe.id = dislikedrecipies.recipie_id "
        "LEFT JOIN likedrecipies "
        "ON recipe.id = likedrecipies.recipie_id "
        "where title like :searchval "
        "GROUP BY recipe.id ")
    res = session.execute(sqlText, {'searchval': '%' + searchval + '%'})
    ret = res.mappings().all()
    return (ret)


@app.get("/recipes/searchtags/{searchval}")
async def searchrecipesval(searchval):
    if not searchval:
        raise HTTPException(status_code=400, detail="Empty Search")
    sqlText = text(
        "SELECT recipe.id,title,steps,nutrition,description"
        ",servings,thumbnail,ingredients,tags, "
        "group_concat(dislikedrecipies.user_id) as dislikedBy, "
        "group_concat(likedrecipies.user_id) as likedBy "
        "FROM recipe "
        "LEFT JOIN dislikedrecipies "
        "ON recipe.id = dislikedrecipies.recipie_id "
        "LEFT JOIN likedrecipies "
        "ON recipe.id = likedrecipies.recipie_id "
        "where tags like :searchval "
        "GROUP BY recipe.id ")
    res = session.execute(sqlText, {'searchval': '%' + searchval + '%'})
    ret = res.mappings().all()
    return (ret)


@app.put("/userSurveyData")
async def putUserSurveyData(user: UserSurveyData):
    newUserSurveyData = UserSurveyDataSQL(
        users_id=user.userID,
        calorie_goal=user.calorie_goal,
        gender=user.gender,
        height=user.height,
        weight=user.weight,
        age=user.age,
        cooking_exp=user.cooking_exp,
        num_days=user.num_days,
        activity_level=user.activity_level)
    if (len(session.query(UserSurveyDataSQL).filter(
        UserSurveyDataSQL.users_id == user.userID
    ).all()) > 0):
        temp = session.query(UserSurveyDataSQL).filter(
            UserSurveyDataSQL.users_id == user.userID).one()
        session.delete(temp)
        session.commit()
    session.add(newUserSurveyData)
    session.commit()


@app.get("/python")
async def hello_world():
    hworld = "Hello World"
    return {hworld}
