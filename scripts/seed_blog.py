"""
Seed script to populate the database with sample blog posts
"""
from app.db.session import SessionLocal
from app.models.blog import BlogPost
from app.models.user import User
import sys
import os
from datetime import datetime, timedelta

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def seed_blog_posts():
    db = SessionLocal()

    try:
        # Get the first user (admin) to be the author
        author = db.query(User).first()

        if not author:
            print("No users found. Please create a user first.")
            return

        # Check if blog posts already exist
        existing_posts = db.query(BlogPost).count()
        if existing_posts > 0:
            print(
                f"Blog posts already exist ({existing_posts} posts). Skipping seed.")
            return

        sample_posts = [
            {
                "title": "The Ultimate Guide to Sustainable Fashion in 2024",
                "slug": "ultimate-guide-sustainable-fashion-2024",
                "excerpt": "Discover how to build a sustainable wardrobe without compromising on style. Learn about eco-friendly materials, ethical brands, and mindful shopping habits.",
                "content": """In today's world, fashion and sustainability go hand in hand. The fashion industry is one of the largest polluters globally, but we can make a difference through conscious choices.

**Understanding Sustainable Fashion**

Sustainable fashion means creating clothing in a way that's mindful of environmental and social impacts. This includes using organic materials, reducing waste, and ensuring fair labor practices.

**Building Your Sustainable Wardrobe**

1. **Quality Over Quantity**: Invest in timeless pieces that last longer rather than fast fashion trends.
2. **Choose Natural Fibers**: Opt for organic cotton, linen, hemp, and bamboo fabrics.
3. **Support Ethical Brands**: Research brands that prioritize fair wages and safe working conditions.
4. **Embrace Secondhand**: Thrift stores and vintage shops are treasure troves of unique finds.
5. **Care for Your Clothes**: Proper maintenance extends the life of your garments.

**The Impact of Your Choices**

Every purchase you make is a vote for the kind of world you want to live in. By choosing sustainable fashion, you're supporting a healthier planet and fairer working conditions for garment workers worldwide.

Remember, sustainable fashion isn't about perfection—it's about making better choices when you can. Start small, and your wardrobe will gradually transform into something you can feel good about wearing.""",
                "featured_image": "/assets/images/colour_dress.jpg",
                "category": "Sustainability",
                "tags": "sustainable fashion, eco-friendly, ethical fashion, green living",
                "is_published": True,
                "published_at": datetime.utcnow() - timedelta(days=5),
                "views_count": 342
            },
            {
                "title": "Spring 2024 Fashion Trends You Need to Know",
                "slug": "spring-2024-fashion-trends",
                "excerpt": "From bold colors to vintage-inspired pieces, discover the hottest fashion trends that will define spring 2024 and how to incorporate them into your wardrobe.",
                "content": """Spring is finally here, and with it comes a fresh wave of fashion trends that are both exciting and wearable. Let's explore the key trends that will dominate this season.

**1. Bold Colors and Prints**

Say goodbye to neutral palettes! This spring is all about vibrant colors—think electric blues, sunny yellows, and hot pinks. Don't be afraid to mix and match bold prints for a statement look.

**2. Oversized Blazers**

The oversized blazer trend continues strong. Pair it with fitted trousers for a sophisticated office look, or throw it over a dress for effortless chic.

**3. Cutout Details**

Strategic cutouts are everywhere this season. From subtle shoulder reveals to dramatic waist cutouts, this trend adds interest to any outfit.

**4. Sheer Fabrics**

Sheer and semi-transparent fabrics create beautiful layering opportunities. Layer them over solid pieces for a romantic, ethereal look.

**5. Low-Rise Jeans**

Yes, they're back! Low-rise jeans from the early 2000s are making a major comeback, but this time with modern updates.

**6. Maxi Skirts**

Flowing maxi skirts in bold prints and solid colors are the perfect piece for transitioning from day to night.

**How to Wear These Trends**

Remember, trends are meant to inspire, not dictate. Choose pieces that align with your personal style and make you feel confident. Mix trendy items with classic staples for a balanced, timeless look.""",
                "featured_image": "/assets/images/summer_style.jpg",
                "category": "Trends",
                "tags": "spring fashion, 2024 trends, fashion guide, style tips",
                "is_published": True,
                "published_at": datetime.utcnow() - timedelta(days=12),
                "views_count": 528
            },
            {
                "title": "How to Build a Capsule Wardrobe That Works",
                "slug": "build-capsule-wardrobe-guide",
                "excerpt": "Simplify your life with a capsule wardrobe. Learn how to curate a collection of versatile, high-quality pieces that work together seamlessly.",
                "content": """A capsule wardrobe is a minimalist approach to fashion that focuses on owning fewer, better-quality items that can be mixed and matched to create numerous outfits.

**What is a Capsule Wardrobe?**

A capsule wardrobe typically consists of 30-40 essential pieces (excluding underwear and accessories) that you love to wear and that work well together. The goal is to create a functional wardrobe that simplifies getting dressed while expressing your personal style.

**Building Your Capsule Wardrobe: Step by Step**

**Step 1: Assess Your Current Wardrobe**
Start by pulling everything out and asking yourself:
- Do I love wearing this?
- Does it fit properly?
- Have I worn it in the past year?
- Does it represent my current style?

**Step 2: Define Your Style**
Look for patterns in the items you kept. What colors dominate? What silhouettes do you gravitate toward? This will guide your future purchases.

**Step 3: Choose Your Color Palette**
Select 3-4 neutral base colors and 2-3 accent colors. This ensures everything coordinates easily.

**Step 4: Essential Pieces to Include**
- 3-4 pairs of well-fitting jeans or trousers
- 2-3 blazers or structured jackets
- 5-7 tops (mix of t-shirts, blouses, and sweaters)
- 2-3 dresses
- 1-2 coats
- Quality shoes for different occasions
- Classic accessories

**Step 5: Quality Over Quantity**
Invest in well-made pieces that will last. It's better to have one excellent white shirt than five mediocre ones.

**Maintaining Your Capsule**
Review your wardrobe seasonally. Remove pieces that no longer serve you and add items thoughtfully based on genuine needs.

**The Benefits**
- Less decision fatigue
- More outfit possibilities
- Higher quality wardrobe
- Reduced clutter
- Better for your wallet and the environment

A capsule wardrobe isn't about restriction—it's about freedom. Freedom from clutter, from decision fatigue, and from the pressure to keep up with every trend.""",
                "featured_image": "/assets/images/mix_and_match.jpg",
                "category": "Style Guide",
                "tags": "capsule wardrobe, minimalist fashion, wardrobe essentials, organization",
                "is_published": True,
                "published_at": datetime.utcnow() - timedelta(days=20),
                "views_count": 891
            },
            {
                "title": "The Art of Mixing High and Low Fashion",
                "slug": "mixing-high-low-fashion-guide",
                "excerpt": "You don't need a designer wardrobe to look stylish. Discover how to expertly blend luxury pieces with affordable fashion for a high-end look on any budget.",
                "content": """Creating a stylish, elevated wardrobe doesn't mean every piece needs a designer label. The art of mixing high and low fashion is all about knowing where to invest and where to save.

**Understanding High-Low Fashion**

High-low dressing means pairing luxury or investment pieces with more affordable items to create a balanced, stylish outfit. This approach makes fashion more accessible while allowing you to build a wardrobe that looks expensive without breaking the bank.

**Where to Invest: High-End Pieces**

**1. Classic Outerwear**
A quality coat or jacket is worth the investment. Look for timeless styles in neutral colors that will last for years.

**2. Handbags**
A well-made bag in a classic style can elevate any outfit and withstand daily use.

**3. Shoes**
Quality footwear provides better support and lasts longer. Invest in classic styles you'll wear regularly.

**4. Tailored Pieces**
Well-fitted blazers and trousers are worth spending on. The construction and fabric quality make a noticeable difference.

**Where to Save: Lower-Priced Items**

**1. Trendy Pieces**
Since trends change quickly, it makes sense to buy trendy items at lower price points.

**2. Basic T-Shirts and Tops**
Simple, everyday basics can be found at reasonable prices without sacrificing quality.

**3. Workout Wear**
Unless you're a serious athlete, mid-range activewear works perfectly fine.

**4. Jewelry and Accessories**
Fashion jewelry and accessories allow you to experiment with trends affordably.

**Styling Tips for High-Low Fashion**

1. **Balance is Key**: Pair one statement luxury piece with simpler, affordable items.
2. **Focus on Fit**: No matter the price, ensure everything fits properly. Tailoring affordable pieces can make them look expensive.
3. **Pay Attention to Details**: Iron your clothes, polish your shoes, and maintain your pieces well.
4. **Mix Textures**: Combining different fabrics and textures adds visual interest and sophistication.
5. **Confidence is Everything**: How you wear something matters more than how much it cost.

**Building Your Mixed Wardrobe**

Start with a few key investment pieces: a classic coat, quality jeans, a leather bag, and versatile shoes. Build around these with affordable pieces that complement your style and can be easily updated as trends change.

Remember, fashion is personal expression, not a price tag. The goal is to create a wardrobe that makes you feel confident and reflects your style, regardless of where each piece came from.""",
                "featured_image": "/assets/images/formal.jpg",
                "category": "Style Guide",
                "tags": "high-low fashion, budget fashion, styling tips, fashion advice",
                "is_published": True,
                "published_at": datetime.utcnow() - timedelta(days=28),
                "views_count": 645
            },
            {
                "title": "Accessorizing 101: Complete Your Perfect Outfit",
                "slug": "accessorizing-guide-complete-outfit",
                "excerpt": "Master the art of accessorizing with our comprehensive guide. Learn how to choose and style jewelry, bags, scarves, and more to elevate any outfit.",
                "content": """Accessories are the exclamation point of your outfit—they complete your look and showcase your personal style. Let's explore how to accessorize like a pro.

**The Power of Accessories**

Accessories can transform a simple outfit into something special. They add personality, color, and sophistication while allowing you to express your unique style.

**Essential Accessories Every Wardrobe Needs**

**1. Jewelry Basics**
- Stud earrings (pearl, diamond, or gold)
- Delicate necklace
- Statement necklace
- Classic watch
- Stackable rings
- Versatile bracelet

**2. Bags for Every Occasion**
- Structured tote for work
- Crossbody bag for casual days
- Evening clutch
- Weekend bag

**3. Scarves and Wraps**
- Silk scarf for elegance
- Cozy wool scarf for winter
- Lightweight cotton scarf for spring

**4. Belts**
- Classic leather belt
- Statement belt for cinching
- Woven or braided belt for casual looks

**5. Sunglasses**
- Classic aviators
- Oversized frames
- Cat-eye style

**The Art of Accessorizing: Rules to Follow**

**Rule 1: Balance Your Look**
If you're wearing a busy pattern, keep accessories minimal. Bold accessories work best with simple outfits.

**Rule 2: Don't Overdo It**
Less is often more. Choose one or two statement pieces rather than wearing everything at once.

**Rule 3: Match Your Metals**
While mixing metals can work, it's safer to stick with one metal tone (gold, silver, or rose gold) throughout your accessories.

**Rule 4: Consider Proportion**
Match the scale of your accessories to your outfit and body frame. Delicate jewelry suits petite frames, while bolder pieces work on larger frames.

**Rule 5: Think About Occasion**
Daytime calls for more subtle accessories, while evening events allow for more drama and sparkle.

**Styling Different Accessories**

**Jewelry:**
- Layer necklaces of different lengths
- Stack thin rings for interest
- Mix textures (smooth, hammered, gemstones)

**Scarves:**
- Tie around your neck for classic elegance
- Wear as a headband or hair accessory
- Tie to your bag for a pop of color

**Belts:**
- Define your waist in oversized pieces
- Add structure to dresses
- Create interest in monochrome outfits

**Common Accessorizing Mistakes to Avoid**

1. Matching everything exactly (especially bag and shoes)
2. Forgetting to remove accessories when needed
3. Ignoring the occasion
4. Choosing trendy over timeless for investment pieces
5. Not experimenting with new styles

**Conclusion**

Accessories are an affordable way to update your look and express your creativity. Don't be afraid to experiment, but remember that confidence is your best accessory. When you feel good in what you're wearing, it shows!""",
                "featured_image": "/assets/images/accessories.jpg",
                "category": "Style Guide",
                "tags": "accessories, jewelry, styling, fashion tips, outfit ideas",
                "is_published": True,
                "published_at": datetime.utcnow() - timedelta(days=35),
                "views_count": 723
            },
        ]

        # Create blog posts
        for post_data in sample_posts:
            post_data["author_id"] = author.id
            blog_post = BlogPost(**post_data)
            db.add(blog_post)

        db.commit()
        print(f"Successfully seeded {len(sample_posts)} blog posts!")

    except Exception as e:
        db.rollback()
        print(f"Error seeding blog posts: {str(e)}")
    finally:
        db.close()


if __name__ == "__main__":
    seed_blog_posts()
