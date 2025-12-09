from __init__ import db
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

class Quest(db.Model):
    __bind_key__ = 'rpg'
    __tablename__ = 'quests'
    
    id = Column(Integer, primary_key=True)
    user_github_id = Column(String(255), nullable=False)
    title = Column(String(255), nullable=False)
    location = Column(String(255))
    difficulty = Column(String(50), default='Medium')
    game_mode = Column(String(50), default='Adventure')
    reward = Column(Text)
    objective = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    def __init__(self, user_github_id, title, **kwargs):
        self.user_github_id = user_github_id
        self.title = title
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_github_id': self.user_github_id,
            'title': self.title,
            'location': self.location,
            'difficulty': self.difficulty,
            'game_mode': self.game_mode,
            'reward': self.reward,
            'objective': self.objective,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }