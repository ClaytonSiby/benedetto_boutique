"""
Update script to fix blog post image paths
"""
from app.db.session import SessionLocal
from app.models.blog import BlogPost
import sys
import os

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def update_blog_images():
    db = SessionLocal()

    try:
        # Mapping of slugs to new image paths
        image_updates = {
            "ultimate-guide-sustainable-fashion-2024": "/assets/images/colour_dress.jpg",
            "spring-2024-fashion-trends": "/assets/images/summer_style.jpg",
            "build-capsule-wardrobe-guide": "/assets/images/mix_and_match.jpg",
            "mixing-high-low-fashion-guide": "/assets/images/formal.jpg",
            "accessorizing-guide-complete-outfit": "/assets/images/accessories.jpg",
        }

        for slug, image_path in image_updates.items():
            post = db.query(BlogPost).filter(BlogPost.slug == slug).first()
            if post:
                post.featured_image = image_path
                print(f"Updated image for: {post.title}")

        db.commit()
        print("\nSuccessfully updated all blog post images!")

    except Exception as e:
        db.rollback()
        print(f"Error updating blog posts: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    update_blog_images()
