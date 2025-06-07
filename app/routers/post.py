from fastapi import FastAPI, Response, status, HTTPException, Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from .. import models, schemas, utils
from ..database import get_db
from ..oauth2 import get_current_user
from sqlalchemy import func

router = APIRouter(
    prefix="/posts",
    tags=['Posts']
)

## Get all post
@router.get("/", response_model=List[schemas.Post])
def get_posts(db: Session = Depends(get_db), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    posts = db.query(models.Post).filter(models.Post.title.contains(search)).limit(limit).offset(skip).all()  # Get all posts
    
    ##Query DB with JOIN
    results =db.query(models.Post, func.count(models.Vote.post_id).label("votes")).join(models.Vote, models.Vote.post_id == models.Post.id, 
                                        isouter=True).group_by(models.Post.id)
    print(results)
    
    return posts
##With authorization required##
# def get_posts(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
#     posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
#     return posts
####################################################################################################

## Create a post
@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    new_post = models.Post(**post.model_dump(), owner_id=current_user.id)
    #new_post = models.Post(title=post.title, content=post.content, published=post.published) #<--inefficient way
    db.add(new_post)
    db.commit()
    db.refresh(new_post) # <-- similar to the RETURNING SQL function in PostgreSQL
    # conn.close() 
    # cursor.execute(""" INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) 
    #                RETURNING * """, 
    #                (post.title, post.content, post.published)) ## <-- SQL to insert into DB
    # new_post = cursor.fetchone()
    # conn.commit() ## <-- SAVES to DB
    return new_post


## Get a post
@router.get("/{id}", response_model=schemas.Post)
def get_post(id: int, response: Response, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to access this post")
    
    response.status_code = status.HTTP_200_OK
    return post

## Delete a post
@router.delete("/{id}")
def delete_post(id: int, response: Response, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    post = post_query.first()
    
    if post is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to delete this post")
    
    post_query.delete(synchronize_session=False)
    db.commit()
    response.status_code = status.HTTP_204_NO_CONTENT
    return Response(status_code=status.HTTP_204_NO_CONTENT)

## Update a post
@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int, post: schemas.PostCreate, response: Response, db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    post_query = db.query(models.Post).filter(models.Post.id == id)
    db_post = post_query.first()
    
    if not db_post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Post not found")
    
    if db_post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to update this post")
    
    post_query.update(post.model_dump(), synchronize_session=False)
    db.commit()
    response.status_code = status.HTTP_200_OK
    return post_query.first()
