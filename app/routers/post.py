from fastapi import status, HTTPException, Response, Depends, APIRouter
from typing import List, Optional
from sqlalchemy.orm import Session
from .. import models, schemas, oauth2
from .. database import get_db
from sqlalchemy import func


router = APIRouter(
    prefix='/posts',
    tags=['Posts']
)


@router.get("/", response_model=List[schemas.PostOut])
def get_posts(db: Session = Depends(get_db),
              current_user: int = Depends(oauth2.get_current_user), limit: int = 10, skip: int = 0, search: Optional[str] = ""):
    # cursor.execute("""SELECT * from posts""")
    # post = cursor.fetchall()
    posts = db.query(models.Post).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    # posts = db.query(models.Post).filter(models.Post.owner_id == current_user.id).all()
    results = db.query(models.Post,
                       func.count(models.Vote.post_id).label("votes")).join(
        models.Vote, models.Vote.post_id == models.Post.id,
        isouter=True).group_by(models.Post.id).filter(
        models.Post.title.contains(search)).limit(limit).offset(skip).all()
    return results


@router.get("/{id}", response_model=schemas.PostOut)
def get_post(id: int,
             db: Session = Depends(get_db),
             current_user: int = Depends(oauth2.get_current_user)):
    #     cursor.execute("""SELECT * FROM posts WHERE id = %s """, (str(id)))
    #     post = cursor.fetchone()
    # post = db.query(models.Post).filter(models.Post.id == id).first()
    post = db.query(models.Post,
                    func.count(models.Vote.post_id).label("votes")).join(
                        models.Vote, models.Vote.post_id == models.Post.id, isouter=True).group_by(
                            models.Post.id).filter(models.Post.id == id).first()
    if not post:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found")
    # Если нужно добавить возможность получать пост по id только тому кто его создал
    # if post.Post.id != current_user.id:
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
    #                         detail="Not authorised to perform requested action.")
    return post


@router.post("/", status_code=status.HTTP_201_CREATED, response_model=schemas.Post)
def create_post(post: schemas.PostCreate,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    #     cursor.execute("""INSERT INTO posts (title, content, published) VALUES (%s, %s, %s) RETURNING * """,
    #                 (post.title,
    #                 post.content,
    #                 post.published))
    #     new_post = cursor.fetchone()
    #     conn.commit()
    new_post = models.Post(owner_id=current_user.id, **post.dict())
    db.add(new_post)
    db.commit()
    db.refresh(new_post)
    return new_post


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_post(id: int,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    #     cursor.execute("""DELETE FROM posts WHERE id = %s returning *""", (str(id)))
    #     post = cursor.fetchone()
    post = db.query(models.Post).filter(models.Post.id == id).first()
    if post == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Post not found")
    if post.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorised to perform requested action.")
    db.delete(post)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{id}", response_model=schemas.Post)
def update_post(id: int,
                post: schemas.PostCreate,
                db: Session = Depends(get_db),
                current_user: int = Depends(oauth2.get_current_user)):
    #     cursor.execute("""UPDATE posts SET (title, content, published) = (%s,%s,%s) WHERE id = %s returning *""",
    #                    (post.title, post.content, post.published,
    #                     (str(id))))
    #     post = cursor.fetchone()
    post_to_update = db.query(models.Post).filter(models.Post.id == id)
    posts = post_to_update.first()
    if posts == None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"Post with id: {id} not found")
    if posts.owner_id != current_user.id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="Not authorised to perform requested action.")
    post_to_update.update(post.dict(), synchronize_session=False)
    db.commit()
    return post_to_update.first()
