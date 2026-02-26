"""
Seed the database with sample data for testing.
Run: python seed_data.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'liz_web.settings')
django.setup()

from accounts.models import User
from equipment.models import Category, Equipment

def seed():
    print("🌱 Seeding Liz Web database...")

    # Create admin user
    if not User.objects.filter(username='admin').exists():
        User.objects.create_superuser(
            username='admin',
            email='admin@lizweb.co.ke',
            password='admin123',
            first_name='Admin',
            last_name='User',
            role='admin',
            phone_number='254700000001',
        )
        print("✅ Admin created (username: admin, password: admin123)")

    # Create staff user
    if not User.objects.filter(username='staff1').exists():
        User.objects.create_user(
            username='staff1',
            email='staff@lizweb.co.ke',
            password='staff123',
            first_name='James',
            last_name='Mwangi',
            role='staff',
            phone_number='254700000002',
        )
        print("✅ Staff created (username: staff1, password: staff123)")

    # Create customer user
    if not User.objects.filter(username='customer1').exists():
        User.objects.create_user(
            username='customer1',
            email='customer@lizweb.co.ke',
            password='customer123',
            first_name='Wanjiku',
            last_name='Kamau',
            role='customer',
            phone_number='254712345678',
            id_number='12345678',
        )
        print("✅ Customer created (username: customer1, password: customer123)")

    # Create categories
    categories_data = [
        {'name': 'Cameras', 'description': 'DSLR and Mirrorless cameras', 'icon': 'bi-camera'},
        {'name': 'Lenses', 'description': 'Camera lenses for all mounts', 'icon': 'bi-circle'},
        {'name': 'Lighting Kits', 'description': 'Studio and portable lighting', 'icon': 'bi-lightbulb'},
        {'name': 'Tripods & Supports', 'description': 'Tripods, monopods and stabilizers', 'icon': 'bi-triangle'},
        {'name': 'Audio', 'description': 'Microphones and audio recorders', 'icon': 'bi-mic'},
    ]
    for cat_data in categories_data:
        Category.objects.get_or_create(name=cat_data['name'], defaults=cat_data)
    print("✅ Categories created")

    # Create equipment with real images
    cameras = Category.objects.get(name='Cameras')
    lenses = Category.objects.get(name='Lenses')
    lighting = Category.objects.get(name='Lighting Kits')
    tripods = Category.objects.get(name='Tripods & Supports')
    audio = Category.objects.get(name='Audio')

    equipment_data = [
        # --- Cameras ---
        {
            'category': cameras, 'name': 'Canon EOS R5', 'brand': 'Canon', 'model_number': 'EOS R5',
            'serial_number': 'CAM-001', 'daily_rate': 5000, 'replacement_value': 450000,
            'description': '45MP full-frame mirrorless camera with 8K video capability. Ideal for professional photography and videography.',
            'image_url': 'https://images.unsplash.com/photo-1516035069371-29a1b244cc32?w=600&h=400&fit=crop',
        },
        {
            'category': cameras, 'name': 'Sony A7 IV', 'brand': 'Sony', 'model_number': 'ILCE-7M4',
            'serial_number': 'CAM-002', 'daily_rate': 4500, 'replacement_value': 350000,
            'description': '33MP full-frame hybrid camera with excellent autofocus and 4K 60p video.',
            'image_url': 'https://images.unsplash.com/photo-1510127034890-ba27508e9f1c?w=600&h=400&fit=crop',
        },
        {
            'category': cameras, 'name': 'Nikon Z6 III', 'brand': 'Nikon', 'model_number': 'Z6 III',
            'serial_number': 'CAM-003', 'daily_rate': 4000, 'replacement_value': 320000,
            'description': '24.5MP full-frame mirrorless with outstanding low-light performance.',
            'image_url': 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=600&h=400&fit=crop',
        },
        {
            'category': cameras, 'name': 'Canon EOS 90D', 'brand': 'Canon', 'model_number': 'EOS 90D',
            'serial_number': 'CAM-004', 'daily_rate': 2500, 'replacement_value': 150000,
            'description': '32.5MP APS-C DSLR perfect for wildlife and sports photography.',
            'image_url': 'https://images.unsplash.com/photo-1564466809058-bf4114d55352?w=600&h=400&fit=crop',
        },

        # --- Lenses ---
        {
            'category': lenses, 'name': 'Canon RF 24-70mm f/2.8L', 'brand': 'Canon', 'model_number': 'RF 24-70 f/2.8L',
            'serial_number': 'LEN-001', 'daily_rate': 2000, 'replacement_value': 280000,
            'description': 'Professional standard zoom lens with constant f/2.8 aperture. Ideal for portraits, events and weddings.',
            'image_url': 'https://images.unsplash.com/photo-1617005082133-548c4dd27f35?w=600&h=400&fit=crop',
        },
        {
            'category': lenses, 'name': 'Sony 70-200mm f/2.8 GM II', 'brand': 'Sony', 'model_number': '70-200 GM2',
            'serial_number': 'LEN-002', 'daily_rate': 2500, 'replacement_value': 350000,
            'description': 'Premium telephoto zoom for sports, wildlife and events.',
            'image_url': 'https://images.unsplash.com/photo-1614587185092-af24c3587572?w=600&h=400&fit=crop',
        },
        {
            'category': lenses, 'name': 'Canon RF 50mm f/1.2L', 'brand': 'Canon', 'model_number': 'RF 50mm f/1.2',
            'serial_number': 'LEN-003', 'daily_rate': 1800, 'replacement_value': 300000,
            'description': 'Ultra-fast prime lens with beautiful bokeh for portraits.',
            'image_url': 'https://images.unsplash.com/photo-1495707902641-75cac588d2e9?w=600&h=400&fit=crop',
        },

        # --- Lighting ---
        {
            'category': lighting, 'name': 'Godox AD600Pro Kit', 'brand': 'Godox', 'model_number': 'AD600Pro',
            'serial_number': 'LIT-001', 'daily_rate': 2000, 'replacement_value': 120000,
            'description': 'Complete studio strobe kit with stands, softboxes and triggers. 600Ws output.',
            'image_url': 'https://images.unsplash.com/photo-1604869515882-4d10fa4b0492?w=600&h=400&fit=crop',
        },
        {
            'category': lighting, 'name': 'Aputure 300D II LED', 'brand': 'Aputure', 'model_number': '300D Mark II',
            'serial_number': 'LIT-002', 'daily_rate': 3000, 'replacement_value': 180000,
            'description': '350W daylight LED light for video production and studio work.',
            'image_url': 'https://images.unsplash.com/photo-1533090161767-e6ffed986c88?w=600&h=400&fit=crop',
        },

        # --- Tripods & Supports ---
        {
            'category': tripods, 'name': 'Manfrotto 055 Carbon Fiber', 'brand': 'Manfrotto', 'model_number': 'MT055CXPRO4',
            'serial_number': 'TRI-001', 'daily_rate': 800, 'replacement_value': 55000,
            'description': 'Professional carbon fiber tripod with 90° column mechanism.',
            'image_url': 'https://images.unsplash.com/photo-1585298723682-7115561c51b7?w=600&h=400&fit=crop',
        },
        {
            'category': tripods, 'name': 'DJI RS 3 Pro Gimbal', 'brand': 'DJI', 'model_number': 'RS 3 Pro',
            'serial_number': 'TRI-002', 'daily_rate': 2500, 'replacement_value': 100000,
            'description': '3-axis gimbal stabilizer for professional video. Supports cameras up to 4.5kg.',
            'image_url': 'https://images.unsplash.com/photo-1589872307379-0ffdf9829123?w=600&h=400&fit=crop',
        },

        # --- Audio ---
        {
            'category': audio, 'name': 'Rode NTG5 Shotgun Mic', 'brand': 'Rode', 'model_number': 'NTG5',
            'serial_number': 'AUD-001', 'daily_rate': 1000, 'replacement_value': 65000,
            'description': 'Broadcast-grade shotgun microphone for film and video production.',
            'image_url': 'https://images.unsplash.com/photo-1590602847861-f357a9332bbc?w=600&h=400&fit=crop',
        },
    ]

    for eq_data in equipment_data:
        Equipment.objects.get_or_create(
            serial_number=eq_data['serial_number'],
            defaults=eq_data
        )
    print("✅ Equipment created (with real images)")
    print("\n🎉 Seed complete! You can now log in with:")
    print("   Admin:    admin / admin123")
    print("   Staff:    staff1 / staff123")
    print("   Customer: customer1 / customer123")

if __name__ == '__main__':
    seed()