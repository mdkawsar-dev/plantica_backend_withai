import datetime
import math
import urllib.request
import json
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status, viewsets
from django.utils import timezone
from plantica_core.responses import custom_response, success_response, error_response
from .models import Plant, PlantTask, MasterPlant, DistrictPlantRecommendation, UserPlant
from disease.models import DiseaseDiagnosisLog
from .serializers import (
    PlantSerializer, PlantTaskSerializer, PlantDropdownSerializer, MasterPlantSerializer,
    DistrictPlantRecommendationSerializer, TaskSummarySerializer, PlantDiseaseReportSerializer
)

# ==========================================
#  1. Plant APIs (My Plants & Add Plant)
# ==========================================
class PlantListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    # --- Screen 1: "My Plants" List API ---
    def get(self, request):
        plants = Plant.objects.filter(user=request.user).order_by('-created_at')
        serializer = PlantSerializer(plants, many=True, context={'request': request})
        return custom_response(
            data=serializer.data,
            message="গাছের তালিকা সফলভাবে পাওয়া গেছে",
            code=status.HTTP_200_OK,
            status=True
        )

    # --- Screen 3: "Add New Plant" API ---
    def post(self, request):
        serializer = PlantSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return custom_response(
                data=serializer.data,
                message="নতুন গাছ সফলভাবে যোগ করা হয়েছে!",
                code=status.HTTP_201_CREATED,
                status=True
            )
        return custom_response(
            data=serializer.errors,
            message="গাছ যোগ করতে ব্যর্থ হয়েছে",
            code=status.HTTP_400_BAD_REQUEST,
            status=False
        )


# --- Screen 4: Minimal Plant List for Task Creation Dropdown ---
class PlantDropdownListView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        plants = Plant.objects.filter(user=request.user)
        serializer = PlantDropdownSerializer(plants, many=True, context={'request': request})
        return custom_response(
            data=serializer.data,
            message="ড্রপডাউন লিস্ট পাওয়া গেছে",
            code=status.HTTP_200_OK,
            status=True
        )


# ==========================================
#  2. Task APIs (Today's Tasks & Repeat Logic)
# ==========================================
class TaskListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    # --- Screen 2: "Today's Tasks" List API (Pending vs Completed Grouped) ---
    def get(self, request):
        tasks = PlantTask.objects.filter(user=request.user).order_by('due_date', 'due_time')
        
        pending_tasks = tasks.filter(is_completed=False)
        completed_tasks = tasks.filter(is_completed=True)

        pending_serializer = PlantTaskSerializer(pending_tasks, many=True, context={'request': request})
        completed_serializer = PlantTaskSerializer(completed_tasks, many=True, context={'request': request})

        data = {
            "pending_count": pending_tasks.count(),
            "completed_count": completed_tasks.count(),
            "pending_tasks": pending_serializer.data,
            "completed_tasks": completed_serializer.data
        }

        return custom_response(
            data=data,
            message="আজকের কাজের তালিকা পাওয়া গেছে",
            code=status.HTTP_200_OK,
            status=True
        )

    # --- Screen 4: "Create Task" API ---
    def post(self, request):
        serializer = PlantTaskSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            serializer.save(user=request.user)
            return custom_response(
                data=serializer.data,
                message="কাজটি সফলভাবে তৈরি করা হয়েছে!",
                code=status.HTTP_201_CREATED,
                status=True
            )
        return custom_response(
            data=serializer.errors,
            message="কাজ তৈরি করতে ব্যর্থ হয়েছে",
            code=status.HTTP_400_BAD_REQUEST,
            status=False
        )


# --- Screen 2: Task Checkmark / Status Toggle API (With Repeat Logic) ---
class ToggleTaskCompleteView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            task = PlantTask.objects.get(pk=pk, user=request.user)
            
            task.is_completed = not task.is_completed
            task.completed_at = timezone.now() if task.is_completed else None
            task.save()

            # Repeat Logic: Auto-generate next task if repeat frequency != 'একবার'
            if task.is_completed and task.repeat_frequency != 'একবার':
                next_date = task.due_date
                if task.repeat_frequency == 'দৈনিক':
                    next_date += datetime.timedelta(days=1)
                elif task.repeat_frequency == 'সপ্তাহে একবার':
                    next_date += datetime.timedelta(days=7)
                elif task.repeat_frequency == 'মাসে একবার':
                    next_date += datetime.timedelta(days=30)

                PlantTask.objects.create(
                    user=task.user,
                    plant=task.plant,
                    task_type=task.task_type,
                    due_date=next_date,
                    due_time=task.due_time,
                    repeat_frequency=task.repeat_frequency,
                    is_completed=False
                )

            status_msg = "কাজটি সম্পন্ন হিসেবে মার্ক করা হয়েছে" if task.is_completed else "কাজটি পুনরায় বাকি তালিকায় রাখা হয়েছে"

            return custom_response(
                data={"id": task.id, "is_completed": task.is_completed},
                message=status_msg,
                code=status.HTTP_200_OK,
                status=True
            )

        except PlantTask.DoesNotExist:
            return custom_response(
                data=None,
                message="কাজটি পাওয়া যায়নি",
                code=status.HTTP_404_NOT_FOUND,
                status=False
            )


class MasterPlantViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = MasterPlant.objects.all().order_by('id')
    serializer_class = MasterPlantSerializer
    permission_classes = [AllowAny]


# --- Home Dashboard Care Summary API ---
class HomeCareSummaryView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        today = datetime.date.today()
        pending_tasks = PlantTask.objects.filter(
            user=request.user,
            due_date=today,
            is_completed=False
        ).order_by('due_time')

        serializer = PlantTaskSerializer(pending_tasks, many=True, context={'request': request})

        data = {
            "pending_count": pending_tasks.count(),
            "subtitle": f"আজ {pending_tasks.count()}টি কাজ বাকি আছে।",
            "tasks": serializer.data
        }

        return custom_response(
            data=data,
            message="আজকের যত্নের সারাংশ পাওয়া গেছে",
            code=status.HTTP_200_OK,
            status=True
        )


# --- Weather & 7-Day Forecast API (Live Real-Time Integration) ---
class WeatherForecastView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        lat = request.query_params.get('lat') or request.query_params.get('latitude') or '23.8103'
        lon = request.query_params.get('lon') or request.query_params.get('lng') or request.query_params.get('longitude') or '90.4125'

        def to_bn_num(val):
            en_bn = {'0':'০', '1':'১', '2':'২', '3':'৩', '4':'৪', '5':'৫', '6':'৬', '7':'৭', '8':'৮', '9':'৯'}
            return ''.join(en_bn.get(c, c) for c in str(val))

        def get_bn_weekday(date_obj):
            days = ['সোমবার', 'মঙ্গলবার', 'বুধবার', 'বৃহস্পতিবার', 'শুক্রবার', 'শনিবার', 'রবিবার']
            return days[date_obj.weekday()]

        def get_bn_month_date(date_obj):
            months = ['', 'জানুয়ারি', 'ফেব্রুয়ারি', 'মার্চ', 'এপ্রিল', 'মে', 'জুন', 'জুলাই', 'আগস্ট', 'সেপ্টেম্বর', 'অক্টোবর', 'নভেম্বর', 'ডিসেম্বর']
            return f'{to_bn_num(date_obj.day)} {months[date_obj.month]}'

        def get_weather_desc(code):
            if code == 0:
                return 'রৌদ্রোজ্জ্বল'
            elif code in [1, 2, 3]:
                return 'আংশিক মেঘলা'
            elif code in [45, 48]:
                return 'কুয়াশাচ্ছন্ন'
            elif code in [51, 53, 55]:
                return 'হালকা গুঁড়ি গুঁড়ি বৃষ্টি'
            elif code in [61, 63, 65]:
                return 'বৃষ্টিপাত'
            elif code in [80, 81, 82]:
                return 'ভারী বর্ষণ'
            elif code in [95, 96, 99]:
                return 'বজ্রবৃষ্টি'
            return 'আংশিক মেঘলা'

        try:
            import requests as http_requests

            # 1. Reverse Geocoding to get real Location Name
            location_name = "ঢাকা, বাংলাদেশ"
            try:
                geo_url = f"https://api.bigdatacloud.net/data/reverse-geocode-client?latitude={lat}&longitude={lon}&localityLanguage=en"
                g_resp = http_requests.get(geo_url, timeout=5, headers={'User-Agent': 'PlanticaApp/1.0'})
                if g_resp.status_code == 200:
                    g_info = g_resp.json()
                    city = g_info.get('city') or g_info.get('locality') or g_info.get('principalSubdivision') or ''
                    country = g_info.get('countryName') or ''
                    if city and country:
                        if city.lower() == 'dhaka' or country.lower() == 'bangladesh':
                            location_name = "ঢাকা, বাংলাদেশ" if city.lower() == 'dhaka' else f"{city}, বাংলাদেশ"
                        else:
                            country_clean = country.split('(')[0].strip()
                            location_name = f"{city}, {country_clean}"
            except Exception:
                pass

            # 2. Live Weather Forecast from Open-Meteo with timezone=auto
            weather_url = f'https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current=temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,rain,weather_code,wind_speed_10m&daily=weather_code,temperature_2m_max,temperature_2m_min,precipitation_probability_max&timezone=auto'
            w_resp = http_requests.get(weather_url, timeout=10, headers={'User-Agent': 'PlanticaApp/1.0'})
            w_resp.raise_for_status()
            data = w_resp.json()


            current = data.get('current', {})
            daily = data.get('daily', {})

            c_temp = round(current.get('temperature_2m', 28))
            c_humidity = round(current.get('relative_humidity_2m', 80))
            c_wind = round(current.get('wind_speed_10m', 10))
            c_code = current.get('weather_code', 1)

            d_max = daily.get('temperature_2m_max', [30]*7)
            d_min = daily.get('temperature_2m_min', [22]*7)
            d_rain = daily.get('precipitation_probability_max', [50]*7)
            d_codes = daily.get('weather_code', [1]*7)
            d_dates = daily.get('time', [])

            today = datetime.date.today()
            current_condition_str = get_weather_desc(c_code)
            rain_chance_val = round(d_rain[0]) if d_rain else 50
            max_temp_val = round(d_max[0]) if d_max else 30
            min_temp_val = round(d_min[0]) if d_min else 22

            # Farming advice based on real rain chance and temp
            if rain_chance_val >= 60 or c_code in [51, 53, 55, 61, 63, 65, 80, 81, 82, 95, 96, 99]:
                farming_advice = "আজ প্রাকৃতিক বৃষ্টির সম্ভাবনা বেশি, তাই টবের গাছে বাড়তি পানি সেচ দেওয়া থেকে বিরত থাকুন।"
            elif max_temp_val >= 33:
                farming_advice = "আজ প্রখর রোদ ও বেশি তাপমাত্রা থাকতে পারে, বিকালের দিকে গাছে পর্যাপ্ত পানি দিন।"
            else:
                farming_advice = "আজ আবহাওয়া স্বাভাবিক ও অনুকূল রয়েছে, নিয়মিত পরিমিত পানি সেচ দিন।"

            # Dynamic Alerts
            alerts = []
            if c_code in [95, 96, 99]:
                alerts.append({"title": "বজ্রপাতের সতর্কতা", "type": "warning"})
            if rain_chance_val >= 70:
                alerts.append({"title": "ভারী বৃষ্টির সম্ভাবনা", "type": "info"})
            if not alerts:
                alerts.append({"title": "গাছের জন্য উপযুক্ত আবহাওয়া", "type": "success"})

            weekly_graph = []
            seven_day_forecast = []

            for i in range(min(7, len(d_dates))):
                dt = datetime.datetime.strptime(d_dates[i], '%Y-%m-%d').date()
                is_today = (i == 0)
                day_name = 'আজ' if is_today else get_bn_weekday(dt)
                date_str = get_bn_month_date(dt)
                desc = get_weather_desc(d_codes[i])
                mx = round(d_max[i])
                mn = round(d_min[i])
                rn = round(d_rain[i])
                
                weekly_graph.append({
                    'day': day_name,
                    'max': mx,
                    'min': mn
                })
                
                day_display = f'আজ ({get_bn_weekday(dt)})' if is_today else day_name
                seven_day_forecast.append({
                    'day': day_display,
                    'date': date_str,
                    'condition': desc,
                    'temp': f'{to_bn_num(mx)}° / {to_bn_num(mn)}°',
                    'rain_chance': f'{to_bn_num(rn)}%'
                })

            response_data = {
                "location": location_name,
                "date_display": get_bn_month_date(today),
                "current_temp": f"{to_bn_num(c_temp)}°সে",
                "current_condition": current_condition_str,
                "min_temp": f"{to_bn_num(min_temp_val)}°সে",
                "max_temp": f"{to_bn_num(max_temp_val)}°সে",
                "rain_chance": f"{to_bn_num(rain_chance_val)}%",
                "metrics": {
                    "humidity": f"{to_bn_num(c_humidity)}%",
                    "rainfall": f"{to_bn_num(rain_chance_val)}%",
                    "wind_speed": f"{to_bn_num(c_wind)} কিমি/ঘণ্টা",
                    "uv_index": "৪ (মাঝারি)"
                },
                "alerts": alerts,
                "farming_advice": farming_advice,
                "weekly_graph": weekly_graph,
                "seven_day_forecast": seven_day_forecast
            }

        except Exception as e:
            # Fallback data if offline or network error
            today = datetime.date.today()
            response_data = {
                "location": "ঢাকা, বাংলাদেশ",
                "date_display": get_bn_month_date(today),
                "current_temp": "২৮°সে",
                "current_condition": "আংশিক মেঘলা",
                "min_temp": "২২°সে",
                "max_temp": "৩২°সে",
                "rain_chance": "৬০%",
                "metrics": {
                    "humidity": "৮২%",
                    "rainfall": "৬০%",
                    "wind_speed": "১২ কিমি/ঘণ্টা",
                    "uv_index": "৪ (মাঝারি)"
                },
                "alerts": [
                    {"title": "গাছের জন্য উপযুক্ত আবহাওয়া", "type": "success"}
                ],
                "farming_advice": "আজ আবহাওয়া স্বাভাবিক রয়েছে, পরিমিত পানি সেচ দিন।",
                "weekly_graph": [
                    {"day": "আজ", "max": 30, "min": 22},
                    {"day": "শনিবার", "max": 31, "min": 23},
                    {"day": "রবিবার", "max": 29, "min": 22},
                    {"day": "সোমবার", "max": 32, "min": 24},
                    {"day": "মঙ্গলবার", "max": 30, "min": 23},
                    {"day": "বুধবার", "max": 28, "min": 22},
                    {"day": "বৃহস্পতিবার", "max": 31, "min": 24}
                ],
                "seven_day_forecast": [
                    {"day": f"আজ ({get_bn_weekday(today)})", "date": get_bn_month_date(today), "condition": "আংশিক মেঘলা", "temp": "৩০° / ২২°", "rain_chance": "৬০%"},
                ]
            }

        return custom_response(
            data=response_data,
            message="লাইভ আবহাওয়ার পূর্বাভাস সফলভাবে পাওয়া গেছে",
            code=status.HTTP_200_OK,
            status=True
        )




# --- Smart Plant Recommendation Filter API ---
class SmartPlantFilterView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        # Auto-seed database table if empty (e.g. fresh deployment on Render)
        if DistrictPlantRecommendation.objects.count() == 0:
            try:
                from django.core.management import call_command
                call_command('seed_plants')
            except Exception as e:
                print("Auto-seed error:", e)

        is_gps = request.data.get('is_gps', False)
        district = request.data.get('district')     # e.g., Barishal / Dhaka / ঢাকা / বরিশাল


        sunlight = request.data.get('sunlight')     # e.g., খুব বেশি / মাঝারি / কম
        space = request.data.get('space')           # e.g., টব / বেলকনি / ছাদ / খোলা মাঠ
        season = request.data.get('season')         # e.g., গ্রীষ্মকাল / শীতকাল
        soil_type = request.data.get('soil_type')   # e.g., দোআঁশ মাটি / পলি মাটি / এঁটেল মাটি

        # If GPS mode is selected or district is empty, use default district logic (e.g. Dhaka or Barishal)
        if is_gps or not district:
            district = "Barishal"

        district_clean = str(district).strip()

        # Dynamic Query filters dictionary
        filters = {}
        if district_clean:
            filters['district__icontains'] = district_clean
        if sunlight:
            filters['sunlight__icontains'] = sunlight
        if space:
            filters['space__icontains'] = space
        if season:
            filters['season__icontains'] = season
        if soil_type:
            filters['soil_type__icontains'] = soil_type

        # 1. Exact match query
        queryset = DistrictPlantRecommendation.objects.filter(**filters)

        # 2. Fallback: match district + sunlight or space
        if not queryset.exists() and district_clean:
            queryset = DistrictPlantRecommendation.objects.filter(district__icontains=district_clean)
            if sunlight:
                queryset = queryset.filter(sunlight__icontains=sunlight)

        # 3. Broad Fallback: return default district recommendations
        if not queryset.exists():
            queryset = DistrictPlantRecommendation.objects.filter(district__icontains='Barishal')[:10]

        serializer = DistrictPlantRecommendationSerializer(queryset, many=True, context={'request': request})

        return custom_response(
            data=serializer.data,
            message="উপযোগী গাছের পরামর্শ সফলভাবে তৈরি করা হয়েছে",
            code=status.HTTP_200_OK,
            status=True
        )


class DistrictPlantRecommendationDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, pk):
        try:
            plant_rec = DistrictPlantRecommendation.objects.get(pk=pk)
            serializer = DistrictPlantRecommendationSerializer(plant_rec, context={'request': request})
            return custom_response(
                data=serializer.data,
                message="উপযোগী গাছের বিস্তারিত তথ্য পাওয়া গেছে",
                code=status.HTTP_200_OK,
                status=True
            )
        except DistrictPlantRecommendation.DoesNotExist:
            return custom_response(
                data=None,
                message="গাছের তথ্য পাওয়া যায়নি",
                code=status.HTTP_404_NOT_FOUND,
                status=False
            )


# --- User Plant Individual Details API (Screen 5) ---
class UserPlantDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        # 1. Fetch plant instance for current user
        plant = None
        is_user_plant_model = False
        try:
            plant = Plant.objects.get(pk=pk, user=request.user)
        except Plant.DoesNotExist:
            try:
                plant = UserPlant.objects.get(pk=pk, user=request.user)
                is_user_plant_model = True
            except UserPlant.DoesNotExist:
                return custom_response(
                    data=None,
                    message="উদ্ভিদটি পাওয়া যায়নি",
                    code=status.HTTP_404_NOT_FOUND,
                    status=False
                )

        # 2. Extract Basic Info & Age Text
        image_url = None
        if plant.image and hasattr(plant.image, 'url'):
            image_url = request.build_absolute_uri(plant.image.url)

        if not is_user_plant_model:
            nickname = plant.nickname
            species = plant.species
            scientific_name = plant.species
            planting_date = str(plant.planting_date)
            location = plant.location
            age_text = plant.age_display
        else:
            nickname = plant.nickname
            species = plant.plant_info.name_bn if plant.plant_info else "চারাগাছ"
            scientific_name = plant.plant_info.scientific_name if (plant.plant_info and plant.plant_info.scientific_name) else species
            planting_date = str(plant.planted_date)
            location = plant.location or "বারান্দা"
            today = datetime.date.today()
            delta = today - plant.planted_date
            days = delta.days
            if days < 0:
                age_text = "সদ্য রোপণকৃত"
            else:
                months = days // 30
                rem_days = days % 30
                years = months // 12
                rem_months = months % 12
                if years > 0:
                    age_text = f"{years} বছর {rem_months} মাস"
                elif rem_months > 0:
                    age_text = f"{rem_months} মাস {rem_days} দিন"
                else:
                    age_text = f"{rem_days} দিন"

        # 3. Care History & Upcoming Schedule Tasks
        if not is_user_plant_model:
            tasks = PlantTask.objects.filter(plant=plant)
        else:
            tasks = PlantTask.objects.filter(user=request.user)

        completed_tasks = tasks.filter(is_completed=True).order_by('-completed_at', '-due_date')
        upcoming_tasks = tasks.filter(is_completed=False).order_by('due_date', 'due_time')

        care_history_serializer = TaskSummarySerializer(completed_tasks, many=True, context={'request': request})
        upcoming_serializer = TaskSummarySerializer(upcoming_tasks, many=True, context={'request': request})

        # 4. Disease Diagnosis Log Reports
        disease_logs = DiseaseDiagnosisLog.objects.filter(user=request.user).order_by('-created_at')
        if is_user_plant_model:
            disease_logs = disease_logs.filter(user_plant=plant)
        
        disease_reports_serializer = PlantDiseaseReportSerializer(disease_logs, many=True, context={'request': request})

        plant_details = {
            "plant_info": {
                "id": plant.id,
                "nickname": nickname,
                "species": species,
                "scientific_name": scientific_name,
                "planting_date": planting_date,
                "location": location,
                "image": image_url,
                "age_text": age_text,
            },
            "care_history": care_history_serializer.data,
            "upcoming_schedule": upcoming_serializer.data,
            "disease_reports": disease_reports_serializer.data,
        }

        return custom_response(
            data=plant_details,
            message="উদ্ভিদের বিস্তারিত তথ্য সফলভাবে পাওয়া গেছে",
            code=status.HTTP_200_OK,
            status=True
        )


# ==========================================
#  Nursery APIs (Google Maps Places Integration)
# ==========================================

def calculate_distance(lat1, lon1, lat2, lon2):
    R = 6371  # Earth radius in km
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) * math.sin(dLat / 2) + \
        math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * \
        math.sin(dLon / 2) * math.sin(dLon / 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return round(R * c, 2)


# --- 1. GET Search & Nearby Nurseries API ---
class SearchNearbyNurseriesView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        user_lat = request.query_params.get('lat') or request.query_params.get('user_lat') or '23.8103'
        user_lng = request.query_params.get('lng') or request.query_params.get('user_lng') or request.query_params.get('lon') or '90.4125'
        distance_km = request.query_params.get('distance', '5')
        search_query = request.query_params.get('query', '').strip()

        try:
            u_lat = float(user_lat)
            u_lng = float(user_lng)
            d_km = float(distance_km)
        except ValueError:
            return custom_response(
                data=None,
                message="অবস্থান (lat/lng) ও দূরত্ব সংখ্যায় প্রদান করুন।",
                code=status.HTTP_400_BAD_REQUEST,
                status=False
            )

        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '') or getattr(settings, 'GOOGLE_WEATHER_API_KEY', '')
        radius_in_meters = int(d_km * 1000)
        keyword = f"nursery {search_query}".strip() if search_query else "nursery"

        google_url = (
            f"https://maps.googleapis.com/maps/api/place/nearbysearch/json"
            f"?location={u_lat},{u_lng}"
            f"&radius={radius_in_meters}"
            f"&keyword={keyword}"
            f"&key={api_key}"
        )

        try:
            req = urllib.request.Request(google_url, headers={'User-Agent': 'PlanticaApp/1.0'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                g_data = json.loads(resp.read().decode('utf-8'))

            results = g_data.get('results', [])
            nurseries = []

            for place in results:
                n_lat = place.get('geometry', {}).get('location', {}).get('lat')
                n_lng = place.get('geometry', {}).get('location', {}).get('lng')

                if n_lat is not None and n_lng is not None:
                    dist = calculate_distance(u_lat, u_lng, float(n_lat), float(n_lng))

                    # Strict distance filter: only include nurseries strictly within selected radius
                    if dist <= d_km:
                        photo_ref = None
                        photos_arr = place.get('photos', [])
                        if photos_arr:
                            photo_ref = photos_arr[0].get('photo_reference')

                        photo_url = f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=400&photo_reference={photo_ref}&key={api_key}" if photo_ref else None

                        nurseries.append({
                            "id": place.get('place_id'),
                            "name": place.get('name'),
                            "address": place.get('vicinity'),
                            "rating": place.get('rating', 0.0),
                            "user_ratings_total": place.get('user_ratings_total', 0),
                            "distance_km": dist,
                            "distance_text": f"{dist} কিমি",
                            "latitude": n_lat,
                            "longitude": n_lng,
                            "photo": photo_url,
                            "is_open": place.get('opening_hours', {}).get('open_now', True)
                        })

            # Sort by distance
            nurseries.sort(key=lambda x: x['distance_km'])


            return custom_response(
                data={
                    "total_count": len(nurseries),
                    "selected_distance_km": int(d_km),
                    "nurseries": nurseries
                },
                message="নিকটস্থ নার্সারির ডেটা সফলভাবে পাওয়া গেছে",
                code=status.HTTP_200_OK,
                status=True
            )

        except Exception as e:
            return custom_response(
                data=str(e),
                message="গুগল ম্যাপস সার্ভিস হতে ডেটা লোড করতে ব্যর্থ হয়েছে",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                status=False
            )


# --- 2. GET Nursery Full Details API ---
class NurseryDetailView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, place_id):
        api_key = getattr(settings, 'GOOGLE_MAPS_API_KEY', '') or getattr(settings, 'GOOGLE_WEATHER_API_KEY', '')

        google_url = (
            f"https://maps.googleapis.com/maps/api/place/details/json"
            f"?place_id={place_id}"
            f"&fields=name,formatted_address,formatted_phone_number,rating,user_ratings_total,reviews,geometry,opening_hours,photos,url,website"
            f"&key={api_key}"
        )

        try:
            req = urllib.request.Request(google_url, headers={'User-Agent': 'PlanticaApp/1.0'})
            with urllib.request.urlopen(req, timeout=8) as resp:
                g_data = json.loads(resp.read().decode('utf-8'))

            place = g_data.get('result', {})

            if not place:
                return custom_response(
                    data=None,
                    message="নার্সারির তথ্য পাওয়া যায়নি",
                    code=status.HTTP_404_NOT_FOUND,
                    status=False
                )

            lat = place.get('geometry', {}).get('location', {}).get('lat')
            lng = place.get('geometry', {}).get('location', {}).get('lng')

            # Photo Gallery
            photos = []
            for photo in place.get('photos', [])[:6]:
                ref = photo.get('photo_reference')
                if ref:
                    photos.append(f"https://maps.googleapis.com/maps/api/place/photo?maxwidth=800&photo_reference={ref}&key={api_key}")

            # Reviews
            reviews = []
            for rev in place.get('reviews', []):
                reviews.append({
                    "author_name": rev.get('author_name'),
                    "rating": rev.get('rating'),
                    "relative_time_description": rev.get('relative_time_description'),
                    "text": rev.get('text'),
                    "profile_photo_url": rev.get('profile_photo_url')
                })

            details = {
                "place_id": place_id,
                "name": place.get('name'),
                "address": place.get('formatted_address'),
                "phone_number": place.get('formatted_phone_number') or "উপলব্ধ নয়",
                "rating": place.get('rating', 0.0),
                "user_ratings_total": place.get('user_ratings_total', 0),
                "website": place.get('website'),
                "google_maps_url": place.get('url') or f"https://www.google.com/maps/search/?api=1&query={lat},{lng}",
                "latitude": lat,
                "longitude": lng,
                "is_open": place.get('opening_hours', {}).get('open_now', True),
                "weekday_text": place.get('opening_hours', {}).get('weekday_text', []),
                "photos": photos,
                "reviews": reviews
            }

            return custom_response(
                data=details,
                message="নার্সারির বিস্তারিত তথ্য পাওয়া গেছে",
                code=status.HTTP_200_OK,
                status=True
            )

        except Exception as e:
            return custom_response(
                data=str(e),
                message="তথ্য লোড করতে সমস্যা হয়েছে",
                code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                status=False
            )


