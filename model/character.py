from __init__ import db
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.sql import func

class CharacterSheet(db.Model):
    __bind_key__ = 'rpg'
    __tablename__ = 'character_sheets'
    
    id = Column(Integer, primary_key=True)
    user_github_id = Column(String(255), nullable=False)  # 确保没有 ForeignKey 错误
    name = Column(String(255), nullable=False)
    game_mode = Column(String(50), default='Adventure')
    motivation = Column(Text)
    fear = Column(Text)
    secret = Column(Text)
    analysis = Column(Text)
    created_at = Column(DateTime, default=func.current_timestamp())
    
    def __init__(self, user_github_id, name, **kwargs):
        self.user_github_id = user_github_id
        self.name = name
        for key, value in kwargs.items():
            setattr(self, key, value)
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_github_id': self.user_github_id,
            'name': self.name,
            'game_mode': self.game_mode,
            'motivation': self.motivation,
            'fear': self.fear,
            'secret': self.secret,
            'analysis': self.analysis,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None
        }