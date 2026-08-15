import json
import os
from django.core.management.base import BaseCommand
from plants.models import DistrictPlantRecommendation

class Command(BaseCommand):
    help = 'Seeds 64 districts plant recommendation data into PostgreSQL'

    def handle(self, *args, **kwargs):
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
        
        # Primary json path inside plants/data/
        json_path = os.path.join(base_dir, 'data', 'bd_plant_recommendations_64_districts.json')

        if not os.path.exists(json_path):
            # Fallback path if data is located under plantica_core/data/
            core_dir = os.path.dirname(base_dir)
            json_path = os.path.join(core_dir, 'data', 'bd_plant_recommendations_64_districts.json')

        if not os.path.exists(json_path):
            from django.conf import settings
            json_path = os.path.join(settings.BASE_DIR, 'plants', 'data', 'bd_plant_recommendations_64_districts.json')

        if not os.path.exists(json_path):
            self.stdout.write(self.style.ERROR(f'File not found at: {json_path}'))
            return


        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

            # Clean old records
            DistrictPlantRecommendation.objects.all().delete()

            items_to_create = []
            for item in data:
                items_to_create.append(
                    DistrictPlantRecommendation(
                        district=item.get('district', ''),
                        plant_name_bn=item.get('plant_name_bn', ''),
                        plant_name_en=item.get('plant_name_en', ''),
                        sunlight=item.get('sunlight', ''),
                        space=item.get('space', ''),
                        season=item.get('season', ''),
                        soil_type=item.get('soil_type', ''),
                        watering_info=item.get('watering_info', ''),
                        fertilizer_info=item.get('fertilizer_info', ''),
                        harvest_time=item.get('harvest_time', ''),
                        growth_time=item.get('growth_time', ''),
                        difficulty=item.get('difficulty', ''),
                        care_tips=item.get('care_tips', ''),
                        extra_description=item.get('extra_description', '')
                    )
                )

            # Bulk insert all items into PostgreSQL
            DistrictPlantRecommendation.objects.bulk_create(items_to_create)
            self.stdout.write(self.style.SUCCESS(f'Successfully imported {len(items_to_create)} plant recommendation records into PostgreSQL!'))
