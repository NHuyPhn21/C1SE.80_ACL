import sqlite3
from datetime import datetime
from backend.database import init_db, SessionLocal
from backend.models import User, Project, ProjectMembership, Chapter, ComicPage, CustomGlossary, ApiKeyConfig

init_db()

with SessionLocal() as db:
    # 1. Seed Users if empty
    users_data = [
        {"username": "W. Mori", "email": "w.mori@hoshikawamanga.co.jp", "role": "Lead Translator"},
        {"username": "Phan Van Quan", "email": "phanvanquann26@gmail.com", "role": "Project Manager"},
        {"username": "Phan Nhat Huy", "email": "nhathuyphan21@gmail.com", "role": "Translator"},
        {"username": "Phan Thanh Hoang", "email": "phanhoang0705@gmail.com", "role": "Typesetter"},
        {"username": "Studio Lead", "email": "you@studio.com", "role": "Project Manager"},
    ]
    
    for u in users_data:
        existing = db.query(User).filter_by(email=u["email"]).first()
        if not existing:
            user = User(
                username=u["username"],
                email=u["email"],
                password_hash="pbkdf2_sha256$mock",
                role=u["role"],
            )
            db.add(user)
    db.commit()

    # 2. Seed Projects if only 1 exists
    mori = db.query(User).filter_by(email="w.mori@hoshikawamanga.co.jp").first()
    owner_id = mori.id if mori else 1

    projects_data = [
        {
            "title": "Sousou no Frieren (葬送のフリーレン)",
            "description": "Fantasy drama series • Japanese ➔ Vietnamese Localization",
        },
        {
            "title": "Dungeon Meshi (ダンジョン飯)",
            "description": "Culinary fantasy adventure • Japanese ➔ English Dual Pass",
        },
        {
            "title": "Chainsaw Man Part 2",
            "description": "Dark action weekly • Japanese ➔ Vietnamese Priority",
        },
    ]

    for p in projects_data:
        existing_p = db.query(Project).filter_by(title=p["title"]).first()
        if not existing_p:
            new_p = Project(
                owner_id=owner_id,
                title=p["title"],
                description=p["description"],
            )
            db.add(new_p)
            db.commit()
            db.refresh(new_p)

            # Membership
            m = ProjectMembership(
                project_id=new_p.id,
                user_id=owner_id,
                project_role="Project Manager",
            )
            db.add(m)
            db.commit()

            # Chapter
            ch = Chapter(
                project_id=new_p.id,
                chapter_number=128 if "Frieren" in p["title"] else 52,
                chapter_name="Chapter 128: The Legacy of Heroes",
            )
            db.add(ch)
            db.commit()
            db.refresh(ch)

            # Sample Page
            cp = ComicPage(
                chapter_id=ch.id,
                page_number=1,
                original_path="assets/demo_page_01.jpg",
                clean_path="assets/clean_page_01.jpg",
            )
            db.add(cp)

            # Glossary
            g1 = CustomGlossary(
                project_id=new_p.id,
                source_term="フリーレン",
                target_term="Frieren",
            )
            g2 = CustomGlossary(
                project_id=new_p.id,
                source_term="ヒンメル",
                target_term="Himmel",
            )
            db.add(g1)
            db.add(g2)
            db.commit()

print("Database seeded with real production entities successfully!")
