import re
from datetime import timedelta, datetime
from rest_framework import serializers
from .models import HomePage, Event, Service, Tariff, Application, Program, Assignment, Staff, StaffGroup

class HomePageSerializer(serializers.ModelSerializer):
    class Meta:
        model = HomePage
        fields = '__all__'

class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = '__all__'

class ServiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Service
        fields = '__all__'

class TariffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tariff
        fields = '__all__'

class ApplicationSerializer(serializers.ModelSerializer):
    created_at = serializers.DateTimeField(format="%d.%m.%Y %H:%M", read_only=True)
    tariff_name = serializers.ReadOnlyField(source='tariff.name')
    show_name = serializers.ReadOnlyField(source='chosen_show.title')
    program_name = serializers.ReadOnlyField(source='chosen_program.title')
    tariff = serializers.StringRelatedField()
    chosen_show = serializers.StringRelatedField()
    chosen_program = serializers.StringRelatedField()

    class Meta:
        model = Application
        fields = [
            'id', 'category', 'full_name', 'phone', 'email', 
            'age', 'address', 'event_date', 'event_time', 
            'tariff', 'tariff_name', 
            'chosen_show', 'show_name',
            'chosen_program', 'program_name',
            'guests_count', 'message', 'status', 'created_at'
        ]

class StaffSerializer(serializers.ModelSerializer):
    class Meta:
        model = Staff
        fields = '__all__'

class AssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = ['id', 'staff', 'application']

    def calc_interval(self, target_app):
        dur = 60
        if target_app.category != 'spectacle' and target_app.tariff and target_app.tariff.duration:
            s = str(target_app.tariff.duration).lower().strip()
            nums = re.findall(r'\d+', s)
            if nums:
                v = int(nums[0])
                if 'мин' in s:
                    dur = v
                else:
                    dur = v * 60
        
        if not target_app.event_date or not target_app.event_time:
            return None, None

        start = datetime.combine(target_app.event_date, target_app.event_time)
        end = start + timedelta(minutes=dur + 60)
        return start, end
    
    def validate(self, data):
        staff = data.get('staff') or (self.instance.staff if self.instance else None)
        app = data.get('application') or (self.instance.application if self.instance else None)

        if not staff or not app:
            print("DEBUG: Данные не полные (нет сотрудника или заявки)")
            return data

        curr_start, curr_end = self.calc_interval(app)
        
        print(f"\n=== DEBUG ВАЛИДАЦИЯ ===")
        print(f"Сотрудник: {staff.full_name}")
        print(f"Проверяем заявку: {app.full_name}")
        print(f"Интервал НОВОЙ: {curr_start} --- {curr_end}")

        existing = Assignment.objects.filter(staff=staff)
        if self.instance:
            existing = existing.exclude(pk=self.instance.pk)

        for other in existing:
            other_app = other.application
            o_start, o_end = self.calc_interval(other_app)

            if not o_start:
                continue
                
            print(f"Сравниваем с существующей: {other_app.full_name}")
            print(f"Интервал СТАРОЙ: {o_start} --- {o_end}")

            if curr_start < o_end and curr_end > o_start:
                print(f"!!! КОНФЛИКТ ОБНАРУЖЕН !!!")
                raise serializers.ValidationError(
                    f"Конфликт: {staff.full_name} уже занят на событии '{other_app.full_name}' до {o_end.strftime('%H:%M')}."
                )

        print("DEBUG: Конфликтов не найдено, сохраняем.\n")
        return data
    
class StaffGroupSerializer(serializers.ModelSerializer):
    member_names = serializers.StringRelatedField(source='members', many=True, read_only=True)

    class Meta:
        model = StaffGroup
        fields = ['id', 'name', 'members', 'member_names']