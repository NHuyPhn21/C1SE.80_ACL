from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean, Float, Text
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.sql import func

Base = declarative_base()

# ==========================================
# NHÓM BẢNG USERS & PROJECTS
# ==========================================

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String(256), nullable=False)
    email = Column(String(256), nullable=False)
    password_hash = Column(Text, nullable=False)
    role = Column(String(50), nullable=False, default='USER')
    created_at = Column(DateTime, default=func.now())

    # Quan hệ (Relationships)
    projects_owned = relationship("Project", back_populates="owner")
    memberships = relationship("ProjectMembership", back_populates="user")

class Project(Base):
    __tablename__ = 'projects'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    owner_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    title = Column(String(256), nullable=False)
    description = Column(Text, nullable=True)
    created_at = Column(DateTime, default=func.now())

    # Quan hệ (Relationships)
    owner = relationship("User", back_populates="projects_owned")
    memberships = relationship("ProjectMembership", back_populates="project")
    api_keys = relationship("ApiKeyConfig", back_populates="project")
    glossaries = relationship("CustomGlossary", back_populates="project")
    chapters = relationship("Chapter", back_populates="project")

class ProjectMembership(Base):
    __tablename__ = 'project_memberships'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    project_role = Column(String(50), nullable=False) # e.g., Manager, Translator
    joined_at = Column(DateTime, default=func.now())

    project = relationship("Project", back_populates="memberships")
    user = relationship("User", back_populates="memberships")

class ApiKeyConfig(Base):
    __tablename__ = 'api_key_configs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    provider = Column(String(100), nullable=False) # Gemini, OpenAI
    encrypted_key = Column(Text, nullable=False)
    is_active = Column(Boolean, nullable=False, default=True)

    project = relationship("Project", back_populates="api_keys")

class CustomGlossary(Base):
    __tablename__ = 'custom_glossaries'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    source_term = Column(String(256), nullable=False)
    target_term = Column(String(256), nullable=False)
    created_at = Column(DateTime, default=func.now())

    project = relationship("Project", back_populates="glossaries")


# ==========================================
# NHÓM BẢNG COMIC PAGES & TASKS
# ==========================================

class Chapter(Base):
    __tablename__ = 'chapters'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    project_id = Column(Integer, ForeignKey('projects.id'), nullable=False)
    chapter_number = Column(Integer, nullable=False)
    chapter_name = Column(String(256), nullable=True)
    created_at = Column(DateTime, default=func.now())

    project = relationship("Project", back_populates="chapters")
    pages = relationship("ComicPage", back_populates="chapter")
    queue_tasks = relationship("QueueTask", back_populates="chapter")

class ComicPage(Base):
    __tablename__ = 'comic_pages'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey('chapters.id'), nullable=False)
    page_number = Column(Integer, nullable=False)
    original_path = Column(String(500), nullable=False)
    clean_path = Column(String(500), nullable=True)
    rendered_path = Column(String(500), nullable=True)
    status = Column(String(50), nullable=False, default='PENDING')

    chapter = relationship("Chapter", back_populates="pages")
    text_regions = relationship("TextRegion", back_populates="page")

class QueueTask(Base):
    __tablename__ = 'queue_tasks'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    chapter_id = Column(Integer, ForeignKey('chapters.id'), nullable=False)
    status = Column(String(50), nullable=False, default='QUEUED')
    progress_percent = Column(Integer, nullable=False, default=0)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())

    chapter = relationship("Chapter", back_populates="queue_tasks")
    logs = relationship("SystemLog", back_populates="task")

class TextRegion(Base):
    __tablename__ = 'text_regions'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    page_id = Column(Integer, ForeignKey('comic_pages.id'), nullable=False)
    bbox_json = Column(String(500), nullable=False)
    original_text = Column(Text, nullable=True)
    translated_text = Column(Text, nullable=True)
    font_family = Column(String(100), nullable=True)
    font_size = Column(Float, nullable=True)
    alignment = Column(String(50), nullable=True)

    page = relationship("ComicPage", back_populates="text_regions")

class SystemLog(Base):
    __tablename__ = 'system_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    task_id = Column(Integer, ForeignKey('queue_tasks.id'), nullable=False)
    level = Column(String(50), nullable=False)
    message = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=func.now())

    task = relationship("QueueTask", back_populates="logs")